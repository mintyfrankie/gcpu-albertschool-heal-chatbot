"""Output formatting utilities for response processing.

This module provides utility functions for formatting various types of responses
into consistent, user-friendly formats.
"""

from backend.utils import SeverityClassificationResponse
from backend.utils.logging import setup_logger

logger = setup_logger(__name__)


def format_severity_response(response: SeverityClassificationResponse) -> str:
    """Format severity classification response into a simple string.

    Args:
        response: Severity classification response object

    Returns:
        Formatted severity level string

    Raises:
        Exception: If response formatting fails
    """
    try:
        logger.debug(f"Formatting severity response: {response}")
        response_dict = response.model_dump()
        formatted_output = f"{response_dict.get('Severity', 'N/A')}"
        logger.debug(f"Formatted output: {formatted_output}")
        return formatted_output
    except Exception as e:
        logger.error(f"Error formatting severity response: {str(e)}", exc_info=True)
        return f"Error formatting response: {e}"
