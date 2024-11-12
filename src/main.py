import json
from typing import Annotated, List, Optional

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing_extensions import TypedDict

from chatbot import format_response
from chatbot.utils import ORIGINAL_PROMPT_TEMPLATE

load_dotenv()

print("ENVIRONMENT VARIABLES LOADED")

# # Build basic chatbot
# class State(TypedDict):
#     # Messages have the type "list". The `add_messages` function
#     # in the annotation defines how this state key should be updated
#     # (in this case, it appends messages to the list, rather than overwriting them)
#     messages: Annotated[list, add_messages]


# graph_builder = StateGraph(State)

# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash-001", temperature=0, max_tokens=None
# )
# # llm = ChatVertexAI(model="gemini-1.5-flash-001", temperature=0, max_tokens=None)


# class TriageResponse(BaseModel):
#     Advice: Optional[str] = Field(
#         default=None,
#         description="Advice based on severity",
#     )
#     Severity: Optional[str] = Field(
#         default=None,
#         description="Severity level: Mild, Moderate, or Severe",
#     )
#     Confidence_Level: Optional[int] = Field(
#         default=None,
#         description="Confidence score out of 100",
#     )
#     Follow_up_Questions: List[str] = Field(
#         default_factory=list,
#         description="Additional questions if confidence is low",
#     )
#     Symptom_Summary: List[str] = Field(
#         default_factory=list,
#         description="Patient symptom summary",
#     )

#     @model_validator(mode="before")
#     @classmethod
#     def severity_in_list(cls, values: dict) -> dict:
#         severity = values.get("Severity")
#         if severity and severity not in ["Mild", "Moderate", "Severe"]:
#             raise ValueError("Invalid Severity value")
#         return values

#     @model_validator(mode="before")
#     @classmethod
#     def validate_follow_up_questions(cls, values: dict) -> dict:
#         follow_up = values.get("Follow_up_Questions", [])
#         if not isinstance(follow_up, list):
#             raise ValueError("Follow-up questions must be a list")
#         return values

#     @model_validator(mode="before")
#     @classmethod
#     def validate_symptom_summary(cls, values: dict) -> dict:
#         symptom_summary = values.get("Symptom_Summary", [])
#         if not isinstance(symptom_summary, list):
#             raise ValueError("Follow-up questions must be a list")
#         return values


# def chatbot(state: State):
#     parser = PydanticOutputParser(pydantic_object=TriageResponse)
#     prompt = PromptTemplate.from_template(MAIN_PROMPT)
#     chain = prompt | llm | parser
#     response = chain.invoke(
#         {
#             "user_question": state["messages"],
#         }
#     )
#     if isinstance(response, TriageResponse):
#         response_str = response.model_dump_json(indent=2)
#     elif isinstance(response, dict):
#         response_str = json.dumps(response, indent=2)
#     else:
#         response_str = str(response)
#     return {"messages": [response_str]}


# # The first argument is the unique node name
# # The second argument is the function or object that will be called whenever
# # the node is used.
# graph_builder.add_node("chatbot", chatbot)

# # Set entry point
# graph_builder.add_edge(START, "chatbot")
# # Set end point
# graph_builder.add_edge("chatbot", END)

# # Run the graph
# memory = MemorySaver()
# # graph = graph_builder.compile()
# graph = graph_builder.compile(checkpointer=memory)


# def stream_graph_updates(user_input: str):
#     events = graph.stream(
#         {"messages": [("user", user_input)]},
#         config,
#         stream_mode="values",
#     )
#     for event in events:
#         event["messages"][-1].pretty_print()


# config = {"configurable": {"thread_id": "2"}}

# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break

#         stream_graph_updates(user_input)
#     except:
#         # # fallback if input() is not available
#         # user_input = "What do you know about LangGraph?"
#         # print("User: " + user_input)
#         # stream_graph_updates(user_input)
#         # break
#         continue
