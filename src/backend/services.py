"""
Service layer for the chatbot that handles business logic and implements a LangGraph-based
triage system with severity classification.

The graph workflow:
1. Takes user input and classifies severity
2. Routes to appropriate severity handler node
3. Generates appropriate response based on severity level
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
    """Extract all user messages from chat history.

    Args:
        messages: List of chat messages

    Returns:
        List of formatted user message strings
    """
    return [
        f"User Input {i}: {msg.content}"
        for i, msg in enumerate(messages)
        if isinstance(msg, HumanMessage)
    ]


def classify_severity(state: ChatState) -> str:
    """Classify severity of user input with error handling.

    Args:
        state: Current chat state

    Returns:
        Classified severity level

    Raises:
        ValueError: If classification fails
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


def mild_severity_node(state: ChatState) -> dict[str, list]:
    """Handle mild severity cases.

    Args:
        state: Current chat state

    Returns:
        Dictionary containing response and messages
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


def moderate_severity_node(state: ChatState) -> dict[str, list]:
    """Handle moderate severity cases.

    Args:
        state: Current chat state

    Returns:
        Dictionary containing response and messages
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


def severe_severity_node(state: ChatState) -> dict[str, list]:
    """Handle severe severity cases.

    Args:
        state: Current chat state

    Returns:
        Dictionary containing response and messages
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


def other_severity_node(state: ChatState) -> dict[str, list]:
    """Handle other severity cases.

    Args:
        state: Current chat state

    Returns:
        Dictionary containing response and messages
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
    tuple[dict, CompiledStateGraph, ChatGoogleGenerativeAI, MemorySaver]
):
    """Initialize and configure the main graph workflow.

    Returns:
        Tuple containing config, compiled graph, LLM instance, and memory
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
    thread_id: Optional[str] = None,
) -> dict[str, Any]:
    """Process user input through the graph workflow.

    Args:
        user_input: User's input message
        config: Optional graph configuration
        thread_id: Optional thread ID for conversation tracking

    Returns:
        Dictionary containing the response
    """
    try:
        # Create config with thread_id if provided
        if thread_id and not config:
            config = {"configurable": {"thread_id": thread_id}}
        elif not config:
            config = {"configurable": {}}

        result = graph.invoke(
            {
                "responses": [],
                "messages": [HumanMessage(content=user_input)],
            },
            config=config,
        )
        return result
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        raise RuntimeError(f"Failed to process input: {str(e)}") from e
