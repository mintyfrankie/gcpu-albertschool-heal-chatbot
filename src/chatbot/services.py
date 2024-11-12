"""
Service layer for the chatbot that handles business logic
"""

import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.callback import CallbackHandler
from pydantic import BaseModel, Field, model_validator

from chatbot import MAIN_PROMPT_TEMPLATE
from chatbot.utils.langfuse import get_langfuse_callback_handler

load_dotenv()


class TriageResponse(BaseModel):
    Advice: Optional[str] = Field(
        default=None,
        description="Advice based on severity",
    )
    Severity: Optional[str] = Field(
        default=None,
        description="Severity level: Mild, Moderate, or Severe",
    )
    Confidence_Level: Optional[int] = Field(
        default=None,
        description="Confidence score out of 100",
    )
    Follow_up_Questions: List[str] = Field(
        default_factory=list,
        description="Additional questions if confidence is low",
    )

    @model_validator(mode="before")
    @classmethod
    def severity_in_list(cls, values: dict) -> dict:
        severity = values.get("Severity")
        if severity and severity not in ["Mild", "Moderate", "Severe"]:
            raise ValueError("Invalid Severity value")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_follow_up_questions(cls, values: dict) -> dict:
        follow_up = values.get("Follow_up_Questions", [])
        if not isinstance(follow_up, list):
            raise ValueError("Follow-up questions must be a list")
        return values


def get_response(user_question: str, chat_history: list[str]) -> TriageResponse:
    """Generate a response based on user input and chat history."""
    parser = PydanticOutputParser(pydantic_object=TriageResponse)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
    )

    prompt = PromptTemplate.from_template(MAIN_PROMPT_TEMPLATE)

    chain = prompt | llm | parser

    response = chain.invoke(
        {"chat_history": chat_history, "user_question": user_question},
        config={"callbacks": [get_langfuse_callback_handler()]},
    )

    return response


if __name__ == "__main__":
    QUERY = "I have a headache and a cough"
    response = get_response(QUERY, [])
    print(response)
