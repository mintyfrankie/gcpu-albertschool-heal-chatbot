"""
Service layer for the chatbot that handles business logic
"""

from typing import Annotated, Any, Iterator

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.callback import CallbackHandler
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from chatbot import format_severity_response
from chatbot.utils import (
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
from chatbot.utils.langfuse import get_langfuse_callback_handler

load_dotenv()


# Build basic chatbot
class State(TypedDict):
    responses: Any
    messages: Annotated[list, add_messages]


def get_all_user_messages(all_messages):
    user_messages = []
    for i, message in enumerate(all_messages):
        if isinstance(message, HumanMessage):
            user_messages.append(f"User Input {i}: {message.content}")
    return user_messages


# Define severity classification node
def classify_severity(state: State) -> str:
    classification_prompt = PromptTemplate.from_template(MAIN_PROMPT_TEMPLATE)
    classification_parser = PydanticOutputParser(
        pydantic_object=SeverityClassificationResponse
    )
    classification_chain = classification_prompt | llm | classification_parser
    classification_response = classification_chain.invoke(
        {
            "user_input": state["messages"][-1].content,
            "chat_history": get_all_user_messages(state["messages"]),
        }
    )
    return format_severity_response(classification_response)


# Define nodes for different severity levels
def mild_severity_node(state: State) -> dict:
    triage_prompt = PromptTemplate.from_template(MILD_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=MildSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state["messages"]})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
    }


def moderate_severity_node(state: State) -> dict:
    triage_prompt = PromptTemplate.from_template(MODERATE_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=ModerateSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state["messages"]})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
    }


def severe_severity_node(state: State) -> dict:
    triage_prompt = PromptTemplate.from_template(SEVERE_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=SevereSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state["messages"]})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
    }


def other_severity_node(state: State) -> dict:
    triage_prompt = PromptTemplate.from_template(OTHER_SEVERITY_PROMPT_TEMPLATE)
    triage_parser = PydanticOutputParser(pydantic_object=OtherSeverityResponse)
    triage_chain = triage_prompt | llm | triage_parser
    triage_response = triage_chain.invoke({"user_input": state["messages"]})
    triage_response_str = triage_response.model_dump().get("Response")
    return {
        "response": [triage_response],
        "messages": [("ai", triage_response_str)],
    }


def main_graph():
    base_memory = MemorySaver()
    base_memory.storage.clear()

    base_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-001",
        temperature=0,
        max_tokens=None,
    )
    # Create conditional graph
    graph = StateGraph(State)
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
    # Define different endpoints for each severity level

    # Add edges to the respective endpoint nodes
    graph.add_edge("mild", END)
    graph.add_edge("moderate", END)
    graph.add_edge("severe", END)
    graph.add_edge("other", END)

    # Run the graph
    compiled_graph = graph.compile(base_memory)
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


config, graph, llm, memory = main_graph()


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
    return events


# if __name__ == "__main__":
#     while True:
#         user_input = input("User: ")
#         # user_input = "I have a headache and a cough"
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break

#         final_response = stream_graph_updates(user_input, config)

#         for event in events:
#             try:
#                 # Display human message if available
#                 if "messages" in event and event["messages"]:
#                     event["messages"][-1].pretty_print()
#             except Exception as e:
#                 print("Error while processing messages:", e)

#     #     QUERY = "I have a headache and a cough"
#     #     response = get_response(QUERY, [])
#     #     print(response)
