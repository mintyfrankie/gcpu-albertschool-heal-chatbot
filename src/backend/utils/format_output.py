"""Output formatting utilities for response processing.

This module provides utility functions for formatting various types of responses
into consistent, user-friendly formats.
"""

from backend.utils import SeverityClassificationResponse


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
        response_dict = response.model_dump()
        formatted_output = f"{response_dict.get('Severity', 'N/A')}"
        return formatted_output
    except Exception as e:
        return f"Error formatting response: {e}"
