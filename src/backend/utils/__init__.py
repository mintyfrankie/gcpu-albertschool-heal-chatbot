from backend.utils.get_doctors import get_doctors
from backend.utils.get_facilities import find_nearby_facilities
from backend.utils.global_variables import platform, user_location
from backend.utils.logging import setup_logger
from backend.utils.output_parsers import (
    MildSeverityResponse,
    ModerateSeverityResponse,
    OtherSeverityResponse,
    SevereSeverityResponse,
    SeverityClassificationResponse,
    TriageResponse,
)
from backend.utils.prompt_templates import (
    MAIN_PROMPT_TEMPLATE,
    MILD_SEVERITY_PROMPT_TEMPLATE,
    MODERATE_SEVERITY_PROMPT_TEMPLATE,
    OTHER_SEVERITY_PROMPT_TEMPLATE,
    SEVERE_SEVERITY_PROMPT_TEMPLATE,
)

logger = setup_logger(__name__)
logger.info("Initializing backend utilities")
logger.debug("Loaded all utility modules and components")

__all__ = [
    "get_doctors",
    "find_nearby_facilities",
    "platform",
    "user_location",
    "MildSeverityResponse",
    "ModerateSeverityResponse",
    "OtherSeverityResponse",
    "SevereSeverityResponse",
    "SeverityClassificationResponse",
    "TriageResponse",
    "MAIN_PROMPT_TEMPLATE",
    "MILD_SEVERITY_PROMPT_TEMPLATE",
    "MODERATE_SEVERITY_PROMPT_TEMPLATE",
    "OTHER_SEVERITY_PROMPT_TEMPLATE",
    "SEVERE_SEVERITY_PROMPT_TEMPLATE",
]
