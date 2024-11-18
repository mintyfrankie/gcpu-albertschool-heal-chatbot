"""Service layer for the chatbot that handles business logic and implements a LangGraph-based triage system.

This module provides the core functionality for processing user inputs through a severity-based
triage system using LangGraph. It implements a workflow that:
1. Takes user input and classifies severity
2. Routes to appropriate severity handler node
3. Generates appropriate response based on severity level

Typical usage example:
    result = process_user_input("I have a headache", thread_id="123")
    print(result['messages'])
"""

import base64
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Annotated, Any, Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from PIL import Image

from backend import format_severity_response, user_location
from backend.utils import (
    MAIN_PROMPT_TEMPLATE,
    MILD_SEVERITY_PROMPT_TEMPLATE,
    MODERATE_SEVERITY_PROMPT_TEMPLATE,
    OTHER_SEVERITY_PROMPT_TEMPLATE,
    SEVERE_SEVERITY_PROMPT_TEMPLATE,
    MildSeverityResponse,
    ModerateSeverityResponse,
    OtherSeverityResponse,
    SevereSeverityResponse,
    SeverityClassificationResponse,
    find_nearby_facilities,
    get_doctors,
)
from backend.utils.logging import setup_logger
from backend.utils.models import Place, PlacesResponse

logger = setup_logger(__name__)
load_dotenv("./credentials/.env")

GEMINI_VERSION = os.getenv("GEMINI_VERSION", "gemini-1.5-flash-001")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0))


@dataclass
class ChatState:
    """State management for chat interactions.

    Attributes:
        responses: List of previous responses
        messages: List of chat messages (human and AI)
        image_data: Optional base64 encoded image string for multimodal processing
    """

    responses: list[dict[str, Any]]
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]
    image_data: Optional[str] = None


def get_all_user_messages(messages: list[HumanMessage | AIMessage]) -> list[str]:
    """Extract and format all user messages from chat history.

    Args:
        messages: List of chat messages containing both human and AI messages

    Returns:
        List of formatted user message strings, each prefixed with "User Input N: "
    """
    return [
        f"User Input {i}: {msg.content}"
        for i, msg in enumerate(messages)
        if isinstance(msg, HumanMessage)
    ]


def get_image_str(image: Image.Image) -> str:
    """Convert PIL Image to base64 string for LLM processing.

    Args:
        image: PIL Image object to convert

    Returns:
        Base64 encoded string representation of the image
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


def classify_severity(
    chat_state: ChatState,
) -> str:
    """Classify the severity of user input using LLM-based classification.

    Args:
        chat_state: Current chat state containing messages, responses and optional image

    Returns:
        String indicating severity level ("Mild", "Moderate", "Severe", or "Other")

    Raises:
        ValueError: If classification fails or returns invalid severity level
    """
    try:
        classification_prompt = ChatPromptTemplate.from_template(MAIN_PROMPT_TEMPLATE)
        classification_parser = PydanticOutputParser(
            pydantic_object=SeverityClassificationResponse
        )
        classification_chain = classification_prompt | llm | classification_parser

        input_data = {
            "user_input": chat_state.messages[-1].content,
            "chat_history": get_all_user_messages(chat_state.messages),
            "image": "",
        }

        if chat_state.image_data:
            input_data["image"] = f"data:image/jpeg;base64,{chat_state.image_data}"

        classification_response = classification_chain.invoke(input_data)
        return format_severity_response(classification_response)
    except Exception as e:
        raise ValueError("Failed to classify severity") from e


class SeverityNodeResponse(TypedDict):
    response: list[Any]  # Could be more specific based on actual response type
    messages: list[tuple[Literal["ai", "human"], str]]


def prepare_input_data(state: ChatState) -> dict[str, Any]:
    """Prepare input data for prompt templates.

    Args:
        state (ChatState): Current chat state

    Returns:
        dict[str, str | list[str]]: Prepared input data with user input, chat history, and image
    """
    user_input = state.messages[-1].content
    chat_history = get_all_user_messages(state.messages)
    image = ""
    if state.image_data:
        image = f"data:image/jpeg;base64,{state.image_data}"

    return {
        "user_input": user_input,
        "chat_history": chat_history,
        "image": image,
    }


def mild_severity_node(state: ChatState) -> SeverityNodeResponse:
    """Process and generate response for mild severity cases.

    Args:
        state (ChatState): Current chat state containing messages and responses

    Returns:
        Dictionary containing:
            - response: List of processed responses
            - messages: List of tuples containing message type and content
    """
    input_data = prepare_input_data(state)

    prompt = ChatPromptTemplate.from_template(MILD_SEVERITY_PROMPT_TEMPLATE)
    parser = PydanticOutputParser(pydantic_object=MildSeverityResponse)

    response = (prompt | llm | parser).invoke(input_data)
    response_str = response.model_dump().get("Response")

    return {
        "response": [response],
        "messages": [("ai", response_str)],
    }


def moderate_severity_node(state: ChatState) -> dict[str, list[Any]]:
    """Process and generate response for moderate severity cases.

    Args:
        state: Current chat state containing messages and responses

    Returns:
        Dictionary containing:
            - response: List of processed responses
            - messages: List of tuples containing message type and content
    """
    input_data = prepare_input_data(state)

    moderate_severity_prompt = ChatPromptTemplate.from_template(
        MODERATE_SEVERITY_PROMPT_TEMPLATE
    )
    moderate_severity_response_parser = PydanticOutputParser(
        pydantic_object=ModerateSeverityResponse
    )
    response = (
        moderate_severity_prompt | llm | moderate_severity_response_parser
    ).invoke(input_data)
    response_text = response.model_dump().get("Response")
    specializations = response.model_dump().get("Recommended_Specialists")

    if user_location["latitude"] and user_location["longitude"]:
        latitude = user_location["latitude"]
        longitude = user_location["longitude"]

        doctors = get_doctors(specializations, latitude, longitude)
        doctors_info = "\n\n---\n".join(
            f"<p><b>{doctor['name_with_title']}</b><br>\n"
            f"Address: {doctor['address']}, {doctor['zipcode']} {doctor['city']}<br>\n"
            f"<a href='https://www.doctolib.fr{doctor['link']}'>Book an appointment</a><br></p>\n"
            for doctor in doctors
        )

        # Parse the facilities response using Pydantic model
        facilities_response = find_nearby_facilities(
            latitude, longitude, facility_type="pharmacy"
        )
        try:
            # Convert dict responses to Place objects first
            place_objects = [Place(**place) for place in facilities_response]
            places = PlacesResponse(places=place_objects)
            pharmacies_info = "\n\n---\n".join(
                f"<p><b>{place.displayName.text}</b><br>\n"
                f"Address: {place.formattedAddress}<br>\n"
                f"<a href='https://www.google.com/maps/place/?q=place_id:{place.id}'>Get Directions</a><br></p>\n"
                for place in places.places
            )
        except Exception as e:
            logger.error(f"Error parsing facilities response: {e}")
            pharmacies_info = ""

        if pharmacies_info and doctors_info:
            response_text += (
                f"\n\nRecommended Pharmacies:\n---\n{pharmacies_info}---\n"
                f"\n\nRecommended Doctors:\n---\n{doctors_info}---\n"
            )
        elif pharmacies_info:
            response_text += f"\n\nRecommended Pharmacies:\n---\n{pharmacies_info}---\n"
        elif doctors_info:
            response_text += f"\n\nRecommended Doctors:\n---\n{doctors_info}---\n"

    return {
        "response": [response],
        "messages": [("ai", response_text)],
    }


def severe_severity_node(state: ChatState) -> dict[str, list[Any]]:
    """Process and generate response for severe severity cases.

    Args:
        state: Current chat state containing messages and responses

    Returns:
        Dictionary containing:
            - response: List of processed responses
            - messages: List of tuples containing message type and content
    """
    input_data = prepare_input_data(state)

    response = (
        ChatPromptTemplate.from_template(SEVERE_SEVERITY_PROMPT_TEMPLATE)
        | llm
        | PydanticOutputParser(pydantic_object=SevereSeverityResponse)
    ).invoke(input_data)

    response_text = response.model_dump().get("Response")

    if user_location["latitude"] and user_location["longitude"]:
        latitude = user_location["latitude"]
        longitude = user_location["longitude"]

        specializations = ["medecin-generaliste"]
        doctors = get_doctors(specializations, latitude, longitude, is_urgent=True)
        doctors_info = "\n\n---\n".join(
            f"<p><b>{doctor['name_with_title']}</b><br>\n"
            f"Address: {doctor['address']}, {doctor['zipcode']} {doctor['city']}<br>\n"
            f"<a href='https://www.doctolib.fr{doctor['link']}'>Book an appointment</a><br></p>\n"
            for doctor in doctors
        )

        hospitals_response = find_nearby_facilities(
            latitude, longitude, facility_type="hospital"
        )
        try:
            place_objects = [Place(**place) for place in hospitals_response]
            places = PlacesResponse(places=place_objects)
            hospitals_info = "\n\n---\n".join(
                f"<p><b>{place.displayName.text}</b><br>\n"
                f"Address: {place.formattedAddress}<br>\n"
                f"<a href='https://www.google.com/maps/place/?q=place_id:{place.id}'>Get Directions</a><br></p>\n"
                for place in places.places
            )
        except Exception as e:
            logger.error(f"Error parsing hospitals response: {e}")
            hospitals_info = ""

        if hospitals_info and doctors_info:
            response_text += (
                f"\n\nRecommended Hospitals:\n---\n{hospitals_info}---\n"
                f"\n\nRecommended Doctors:\n---\n{doctors_info}---\n"
            )
        elif hospitals_info:
            response_text += f"\n\nRecommended Hospitals:\n---\n{hospitals_info}---\n"
        elif doctors_info:
            response_text += f"\n\nRecommended Doctors:\n---\n{doctors_info}---\n"

    return {
        "response": [response],
        "messages": [("ai", response_text)],
    }


def other_severity_node(state: ChatState) -> dict[str, list[Any]]:
    """Process and generate response for other/unknown severity cases.

    Args:
        state: Current chat state containing messages and responses

    Returns:
        Dictionary containing:
            - response: List of processed responses
            - messages: List of tuples containing message type and content
    """
    input_data = prepare_input_data(state)
    response = (
        ChatPromptTemplate.from_template(OTHER_SEVERITY_PROMPT_TEMPLATE)
        | llm
        | PydanticOutputParser(pydantic_object=OtherSeverityResponse)
    ).invoke(input_data)

    response_text = response.model_dump().get("Response")

    return {
        "response": [response],
        "messages": [("ai", response_text)],
    }


def main_graph() -> (
    tuple[dict[str, dict], CompiledStateGraph, ChatGoogleGenerativeAI, MemorySaver]
):
    """Initialize and configure the main LangGraph workflow.

    Creates and configures the graph with all severity nodes and their connections.
    Initializes the LLM and memory components.

    Returns:
        Tuple containing:
            - Configuration dictionary
            - Compiled state graph
            - LLM instance
            - Memory saver instance
    """
    base_memory = MemorySaver()
    base_memory.storage.clear()

    base_llm = ChatGoogleGenerativeAI(
        model=GEMINI_VERSION,
        temperature=GEMINI_TEMPERATURE,
        max_tokens=None,
    )

    graph = StateGraph(ChatState)
    graph.add_node("mild", mild_severity_node)
    graph.add_node("moderate", moderate_severity_node)
    graph.add_node("severe", severe_severity_node)
    graph.add_node("other", other_severity_node)

    graph.add_conditional_edges(
        START,
        classify_severity,
        {
            "Mild": "mild",
            "Moderate": "moderate",
            "Severe": "severe",
            "Other": "other",
        },
    )

    graph.add_edge("mild", END)
    graph.add_edge("moderate", END)
    graph.add_edge("severe", END)
    graph.add_edge("other", END)

    compiled_graph = graph.compile(base_memory)
    config_dict = {
        "configurable": {},
    }
    return (
        config_dict,
        compiled_graph,
        base_llm,
        base_memory,
    )


config, graph, llm, memory = main_graph()


def validate_config(config: Optional[RunnableConfig]) -> None:
    """Validate the configuration for processing user input.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    if not config:
        raise ValueError("Config is required for checkpointing")

    if not isinstance(config.get("configurable"), dict):
        raise ValueError("Config must contain 'configurable' dictionary")

    required_keys = ["thread_id", "checkpoint_ns", "checkpoint_id"]
    missing_keys = [
        key for key in required_keys if key not in config.get("configurable", {})
    ]
    if missing_keys:
        raise ValueError(f"Missing required config keys: {missing_keys}")


def prepare_image_data(image: Optional[bytes]) -> Optional[str]:
    """Prepare image data for processing.

    Args:
        image: Raw image bytes

    Returns:
        Base64 encoded image string or None
    """
    if not image:
        return None
    return base64.b64encode(image).decode("utf-8")


def process_user_input(
    user_input: str,
    config: Optional[RunnableConfig] = None,
    image: Optional[bytes] = None,
) -> dict[str, Any]:
    """Process user input through the graph workflow."""
    try:
        logger.info("Processing new user input")
        logger.debug(f"User input: {user_input}")
        if image:
            logger.debug("Image data received with input")

        validate_config(config)

        image_data = prepare_image_data(image)

        result = graph.invoke(
            {
                "responses": [],
                "messages": [HumanMessage(content=user_input)],
                "image_data": image_data,
            },
            config=config,
        )

        logger.info(f"Raw graph result: {result}")

        if isinstance(result, dict):
            if "messages" in result and isinstance(result["messages"], list):
                formatted_messages = []
                for msg in result["messages"]:
                    if hasattr(msg, "content"):
                        if hasattr(msg, "type") and msg.type == "ai":
                            formatted_messages.append(("ai", msg.content))
                        elif isinstance(msg, HumanMessage):
                            formatted_messages.append(("human", msg.content))
                        elif isinstance(msg, AIMessage):
                            formatted_messages.append(("ai", msg.content))

                if formatted_messages:
                    return {"messages": formatted_messages}

            if "response" in result and result["response"]:
                response = result["response"]
                if isinstance(response, list) and response:
                    first_response = response[0]
                    if hasattr(first_response, "model_dump"):
                        response_text = first_response.model_dump().get("Response", "")
                        if response_text:
                            return {
                                "messages": [("ai", response_text)],
                                "image": [image],
                            }

        return {
            "messages": [
                ("ai", "I apologize, but I couldn't process your request properly.")
            ],
            "image": [image],
        }

    except Exception as e:
        logger.error("Failed to process user input", exc_info=True)
        return {
            "messages": [
                ("ai", f"An error occurred while processing your request: {str(e)}")
            ]
        }
