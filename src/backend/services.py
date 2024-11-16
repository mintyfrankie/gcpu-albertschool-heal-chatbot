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

from typing import Annotated, Any, Optional
from dataclasses import dataclass
import logging
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph.state import CompiledStateGraph
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from backend import format_severity_response
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
)

logger = logging.getLogger(__name__)
load_dotenv()


@dataclass
class ChatState:
    """State management for chat interactions."""

    responses: list[dict[str, Any]]
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]


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


def classify_severity(state: ChatState) -> str:
    """Classify the severity of user input using LLM-based classification.

    Args:
        state: Current chat state containing messages and responses

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
        classification_response = classification_chain.invoke(
            {
                "user_input": state.messages[-1].content,
                "chat_history": get_all_user_messages(state.messages),
            }
        )
        return format_severity_response(classification_response)
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise ValueError("Failed to classify severity") from e


def mild_severity_node(state: ChatState) -> dict[str, list[Any]]:
    """Process and generate response for mild severity cases.

    Args:
        state: Current chat state containing messages and responses

    Returns:
        Dictionary containing:
            - response: List of processed responses
            - messages: List of tuples containing message type and content
    """
    triage_prompt = ChatPromptTemplate.from_template(MILD_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=MildSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state.messages})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
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
    triage_prompt = ChatPromptTemplate.from_template(MODERATE_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=ModerateSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state.messages})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
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
    triage_prompt = ChatPromptTemplate.from_template(SEVERE_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=SevereSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state.messages})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
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
    triage_prompt = ChatPromptTemplate.from_template(OTHER_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=OtherSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state.messages})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
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
        model="gemini-1.5-flash-001",
        temperature=0,
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


def process_user_input(
    user_input: str,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Process user input through the graph workflow.

    Main entry point for processing user messages through the severity classification
    and response generation workflow.

    Args:
        user_input: User's input message
        config: Configuration settings including checkpoint information

    Returns:
        Dictionary containing:
            - messages: List of tuples (message_type, content)
            - response: List of processed responses

    Raises:
        RuntimeError: If processing fails at any stage
    """
    try:
        if not config:
            raise ValueError("Config is required for checkpointing")

        if "configurable" not in config or not isinstance(config["configurable"], dict):
            raise ValueError("Config must contain 'configurable' dictionary")

        required_keys = ["thread_id", "checkpoint_ns", "checkpoint_id"]
        missing_keys = [
            key for key in required_keys if key not in config["configurable"]
        ]
        if missing_keys:
            raise ValueError(f"Missing required config keys: {missing_keys}")

        result = graph.invoke(
            {
                "responses": [],
                "messages": [HumanMessage(content=user_input)],
            },
            config=config,
        )

        logger.info(f"Raw graph result: {result}")

        # Extract the response from the result
        if isinstance(result, dict):
            # Handle messages field containing LangChain Message objects
            if "messages" in result and isinstance(result["messages"], list):
                formatted_messages = []
                for msg in result["messages"]:
                    if hasattr(msg, "content"):
                        # For AI messages
                        if hasattr(msg, "type") and msg.type == "ai":
                            formatted_messages.append(("ai", msg.content))
                        # For human messages
                        elif isinstance(msg, HumanMessage):
                            formatted_messages.append(("human", msg.content))
                        # For AIMessage
                        elif isinstance(msg, AIMessage):
                            formatted_messages.append(("ai", msg.content))

                if formatted_messages:
                    return {"messages": formatted_messages}

            # Handle response field with Pydantic models
            if "response" in result and result["response"]:
                response = result["response"]
                if isinstance(response, list) and response:
                    first_response = response[0]
                    if hasattr(first_response, "model_dump"):
                        response_text = first_response.model_dump().get("Response", "")
                        if response_text:
                            return {"messages": [("ai", response_text)]}

        # Fallback response if no valid format is found
        return {
            "messages": [
                ("ai", "I apologize, but I couldn't process your request properly.")
            ]
        }

    except Exception as e:
        logger.error(f"Error processing input: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to process input: {str(e)}") from e
