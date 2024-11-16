"""Output formatting utilities for response processing.

This module provides utility functions for formatting various types of responses
into consistent, user-friendly formats.
"""

from backend.utils import SeverityClassificationResponse, TriageResponse


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


# FIXME: deprecated
def format_response(response: TriageResponse) -> str:
    """Format triage response into a structured string output.

    Note:
        This function is deprecated and will be removed in a future version.

    Args:
        response: Triage response object containing advice, severity, etc.

    Returns:
        Formatted string with sections for advice, severity, confidence,
        and follow-up questions

    Raises:
        Exception: If response formatting fails
    """
    try:
        response_dict = response.model_dump()
        formatted_output = (
            f"### Advice:\n{response_dict.get('Advice', 'N/A')}\n\n"
            f"### Severity:\n{response_dict.get('Severity', 'N/A')}\n\n"
            f"### Confidence Level:\n{response_dict.get('Confidence_Level', 'N/A')}%\n\n"
            f"### Follow-up Questions:\n"
        )
        for idx, question in enumerate(
            response_dict.get("Follow_up_Questions", []), start=1
        ):
            formatted_output += f"{idx}. {question}\n"
        return formatted_output
    except Exception as e:
        return f"Error formatting response: {e}"
