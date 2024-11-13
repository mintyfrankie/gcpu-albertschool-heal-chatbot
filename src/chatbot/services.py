"""
Service layer for the chatbot that handles business logic
"""

import os
from typing import Annotated, Any, Iterator, List, Literal, Optional

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.callback import CallbackHandler
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, model_validator
from typing_extensions import TypedDict

from chatbot import format_response, format_severity_response
from chatbot.utils import (
    MAIN_PROMPT_TEMPLATE,
    MILD_SEVERITY_PROMPT_TEMPLATE,
    MODERATE_SEVERITY_PROMPT_TEMPLATE,
    ORIGINAL_PROMPT_TEMPLATE,
    OTHER_SEVERITY_PROMPT_TEMPLATE,
    SEVERE_SEVERITY_PROMPT_TEMPLATE,
    MildSeverityResponse,
    ModerateSeverityResponse,
    OtherSeverityResponse,
    SevereSeverityResponse,
    SeverityClassificationResponse,
    TriageResponse,
)
from chatbot.utils.langfuse import get_langfuse_callback_handler

load_dotenv()

memory = MemorySaver()


# Build basic chatbot
class State(TypedDict):
    responses: Any
    messages: Annotated[list, add_messages]


def get_llm_response(
    state: State,
) -> dict:
    classification_prompt = PromptTemplate.from_template(MAIN_PROMPT_TEMPLATE)
    classification_parser = PydanticOutputParser(
        pydantic_object=SeverityClassificationResponse
    )

    classification_chain = classification_prompt | llm | classification_parser

    try:
        classification_response = classification_chain.invoke(
            {"user_input": state["messages"]},
        )
        classification_response_str = format_severity_response(classification_response)
    except Exception as e:
        print(f"Error {e}")

    if classification_response_str == "Mild":
        triage_prompt = PromptTemplate.from_template(MILD_SEVERITY_PROMPT_TEMPLATE)
        triage_parser = PydanticOutputParser(pydantic_object=MildSeverityResponse)
    elif classification_response_str == "Moderate":
        triage_prompt = PromptTemplate.from_template(MODERATE_SEVERITY_PROMPT_TEMPLATE)
        triage_parser = PydanticOutputParser(pydantic_object=ModerateSeverityResponse)
    elif classification_response_str == "Severe":
        triage_prompt = PromptTemplate.from_template(SEVERE_SEVERITY_PROMPT_TEMPLATE)
        triage_parser = PydanticOutputParser(pydantic_object=SevereSeverityResponse)
    else:
        triage_prompt = PromptTemplate.from_template(OTHER_SEVERITY_PROMPT_TEMPLATE)
        triage_parser = PydanticOutputParser(pydantic_object=MildSeverityResponse)

    triage_chain = triage_prompt | llm | triage_parser

    try:
        print(f"state['messages']: {state["messages"]}\n\n")
        triage_response = triage_chain.invoke(
            {"user_input": state["messages"]},
        )
        triage_response_str = f"{triage_response.model_dump().get("Response")}"
    except Exception as e:
        print(f"Error {e}")

    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
    }


def main_graph():
    base_memory = MemorySaver()
    graph_builder = StateGraph(State)

    base_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-001",
        temperature=0,
        max_tokens=None,
    )
    # llm = ChatVertexAI(model="gemini-1.5-flash-001", temperature=0, max_tokens=None)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever the node is used.
    graph_builder.add_node("chatbot", get_llm_response)

    # Set entry point
    graph_builder.add_edge(START, "chatbot")
    # Set end point
    graph_builder.add_edge("chatbot", END)

    # Run the graph
    # graph = graph_builder.compile()
    compiled_graph = graph_builder.compile(checkpointer=base_memory)
    config_dict = {
        "configurable": {"thread_id": "3"},
        # "callbacks": [get_langfuse_callback_handler()],
    }
    return (
        config_dict,
        compiled_graph,
        base_llm,
        base_memory,
    )


def stream_graph_updates(
    user_input: str,
    config: dict = {
        "configurable": {"thread_id": "3"},
        # "callbacks": [get_langfuse_callback_handler()],
    },
) -> Iterator[dict[str, Any] | Any]:
    events = graph.stream(
        {"responses": "", "messages": [("user", user_input)]},
        config,
        stream_mode="values",
    )
    # *_, last_response = events
    # print(f"LAST RESPONSE: {last_response["messages"][-1].content}")
    return events


def get_response(user_question: str, chat_history: list[str]) -> TriageResponse:
    """Generate a response based on user input and chat history."""
    parser = PydanticOutputParser(pydantic_object=TriageResponse)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
    )

    prompt = PromptTemplate.from_template(ORIGINAL_PROMPT_TEMPLATE)

    chain = prompt | llm | parser

    response = chain.invoke(
        {"chat_history": chat_history, "user_question": user_question},
        config={"callbacks": [get_langfuse_callback_handler()]},
    )

    return response


config, graph, llm, memory = main_graph()

if __name__ == "__main__":
    while True:
        # user_input = input("User: ")
        user_input = "I have a headache and a cough"
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        events = stream_graph_updates(user_input, config)

        for event in events:
            try:
                # Display human message if available
                if "messages" in event and event["messages"]:
                    event["messages"][-1].pretty_print()
            except Exception as e:
                print("Error while processing messages:", e)

    #     QUERY = "I have a headache and a cough"
    #     response = get_response(QUERY, [])
    #     print(response)
