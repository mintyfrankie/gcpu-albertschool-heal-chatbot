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

    template = """
        You are a medical assistant specializing in initial triage. When assessing a patient, evaluate the severity of their symptoms as "Mild," "Moderate," or "Severe" based on their descriptions and any additional context from an image if provided. Also provide a score out of 100 for how confident you are about the severity level.

        If you are less than 70% confident in your assessment, generate follow-up questions that could help you gain more clarity about the patient's symptoms. These questions should be relevant, specific, and aimed at better understanding the patient's condition.

        Consider both text descriptions of symptoms and image descriptions when formulating your response. Your response should include the following structure:

        1. "Severity": The severity level ("Mild," "Moderate," or "Severe").
        2. "Confidence_Level": A confidence score out of 100 for your assessment.
        3. "Advice": Provide recommendations or advice based on the symptoms.
        4. "Follow_up_Questions": A list of follow-up questions for the user if you are not confident in your assessment (otherwise, provide an empty list).

        Chat history: {chat_history}

        User question: Patient reports the following symptoms: {user_question}.

        Please provide your response in the following JSON format:
        {{
            "Severity": "<Severity Level>",
            "Confidence_Level": <Confidence Score>,
            "Advice": "<Advice>",
            "Follow_up_Questions": ["<Question 1>", "<Question 2>"]
        }}
    """

    prompt = PromptTemplate.from_template(template)

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
