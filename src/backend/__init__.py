"""Backend package initialization.

This module initializes the backend package and sets up logging configuration.
It also exports commonly used functions and constants.
"""

from backend.utils.format_output import format_severity_response
from backend.utils.global_variables import user_location
from backend.utils.logging import setup_logger
from backend.utils.prompt_templates import (
    MAIN_PROMPT_TEMPLATE,
    MILD_SEVERITY_PROMPT_TEMPLATE,
    MODERATE_SEVERITY_PROMPT_TEMPLATE,
    OTHER_SEVERITY_PROMPT_TEMPLATE,
    SEVERE_SEVERITY_PROMPT_TEMPLATE,
)

# Initialize root logger for backend package
logger = setup_logger("backend")
logger.info("Initializing backend package")

# Log the availability of templates
logger.debug("Loaded prompt templates:")
logger.debug("- Main prompt template")
logger.debug("- Mild severity template")
logger.debug("- Moderate severity template")
logger.debug("- Severe severity template")
logger.debug("- Other severity template")

__all__ = [
    "format_severity_response",
    "user_location",
    "MAIN_PROMPT_TEMPLATE",
    "MILD_SEVERITY_PROMPT_TEMPLATE",
    "MODERATE_SEVERITY_PROMPT_TEMPLATE",
    "OTHER_SEVERITY_PROMPT_TEMPLATE",
    "SEVERE_SEVERITY_PROMPT_TEMPLATE",
]
