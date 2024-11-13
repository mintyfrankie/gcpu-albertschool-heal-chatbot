from typing import List, Literal, Optional

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, model_validator


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
    Severity: Literal["Mild", "Moderate", "Severe", "Other"] = Field(
        description="The severity classification of the symptoms, must be one of 'Mild', 'Moderate', 'Severe', or 'Other'.",
    )

    @model_validator(mode="before")
    @classmethod
    def check_valid_severity(cls, values: dict) -> dict:
        severity = values.get("Severity")
        allowed_values = ["Mild", "Moderate", "Severe", "Other"]
        if severity not in allowed_values:
            if severity == "Unknown":
                values["Severity"] = "Other"
            else:
                raise ValueError(
                    f"Invalid severity value: {severity}. Must be one of {allowed_values}."
                )
        return values


class MildSeverityResponse(BaseModel):
    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )


class ModerateSeverityResponse(BaseModel):
    Recommended_Specialists: List[str] = Field(
        default_factory=list,
        description="Any recommended specialists",
    )
    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_recommended_specialists(cls, values: dict) -> dict:
        recommended_specialists = values.get("Recommended_Specialists", [])
        if not isinstance(recommended_specialists, list):
            raise ValueError("Recommended specialists must be a list")
        return values


class SevereSeverityResponse(BaseModel):
    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )


class OtherSeverityResponse(BaseModel):
    Response: str = Field(
        description="The response from the llm for mild severity symptoms.",
    )
