"""Pydantic models for parsing and validating LLM outputs.

This module defines the data models used to parse and validate various types
of responses from the language model, including severity classifications and
different severity-level responses.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from backend.utils.logging import setup_logger

logger = setup_logger(__name__)


class TriageResponse(BaseModel):
    """Model for parsing general triage responses.

    Attributes:
        Advice: Specific advice based on severity level
        Severity: Classification of symptom severity
        Confidence_Level: Confidence score for the classification
        Follow_up_Questions: List of follow-up questions if needed
    """

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
    Follow_up_Questions: list[str] = Field(
        default_factory=list,
        description="Additional questions if confidence is low",
    )

    @model_validator(mode="before")
    @classmethod
    def severity_in_list(cls, values: dict) -> dict:
        severity = values.get("Severity")
        if severity and severity not in ["Mild", "Moderate", "Severe"]:
            if severity == "Unknown":
                values["Severity"] = "Other"
            else:
                raise ValueError("Invalid Severity value")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_follow_up_questions(cls, values: dict) -> dict:
        follow_up = values.get("Follow_up_Questions", [])
        if not isinstance(follow_up, list):
            raise ValueError("Follow-up questions must be a list")
        return values


class SeverityClassificationResponse(BaseModel):
    """Model for parsing severity classification responses.

    Attributes:
        Severity: The classified severity level, must be one of the defined literals
    """

    Severity: Literal["Mild", "Moderate", "Severe", "Other"] = Field(
        description="The severity classification of the symptoms, must be one of 'Mild', 'Moderate', 'Severe', or 'Other'.",
    )

    @model_validator(mode="before")
    @classmethod
    def check_valid_severity(cls, values: dict) -> dict:
        severity = values.get("Severity")
        allowed_values = ["Mild", "Moderate", "Severe", "Other"]
        logger.debug(f"Validating severity value: {severity}")

        if severity not in allowed_values:
            if severity == "Unknown":
                logger.info("Converting 'Unknown' severity to 'Other'")
                values["Severity"] = "Other"
            else:
                logger.error(f"Invalid severity value received: {severity}")
                raise ValueError(
                    f"Invalid severity value: {severity}. Must be one of {allowed_values}."
                )
        return values


class MildSeverityResponse(BaseModel):
    """Model for parsing responses to mild severity cases.

    Attributes:
        Response: The formatted response text for mild severity
    """

    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )


class ModerateSeverityResponse(BaseModel):
    """Model for parsing responses to moderate severity cases.

    Attributes:
        Recommended_Specialists: List of recommended medical specialists
        Response: The formatted response text for moderate severity
    """

    Recommended_Specialists: list[str] = Field(
        default_factory=list,
        description="Any recommended specialists",
    )
    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_recommended_specialists(cls, values: dict) -> dict:
        allowed_specialists = [
            "allergologue",
            "cardiologue",
            "dentiste",
            "dermatologue",
            "masseur-kinesitherapeute",
            "medecin-generaliste",
            "ophtalmologue",
            "opticien-lunetier",
            "orl-oto-rhino-laryngologie",
            "orthodontiste",
            "osteopathe",
            "pediatre",
            "pedicure-podologue",
            "psychiatre",
            "psychologue",
            "radiologue",
            "rhumatologue",
            "sage-femme",
        ]
        recommended_specialists = values.get("Recommended_Specialists", [])
        if not isinstance(recommended_specialists, list):
            raise ValueError("Recommended specialists must be a list")
        for specialist in recommended_specialists:
            if not specialist in allowed_specialists:
                recommended_specialists.remove(specialist)
        return values


class SevereSeverityResponse(BaseModel):
    """Model for parsing responses to severe severity cases.

    Attributes:
        Response: The formatted response text for severe severity
    """

    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )


class OtherSeverityResponse(BaseModel):
    """Model for parsing responses to other/unknown severity cases.

    Attributes:
        Response: The formatted response text for other severity cases
    """

    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )
