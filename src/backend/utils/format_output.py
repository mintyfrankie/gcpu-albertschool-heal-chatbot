"""
Utility functions
"""

from backend.utils import SeverityClassificationResponse, TriageResponse


def format_severity_response(response: SeverityClassificationResponse) -> str:
    """Format the JSON response into a user-friendly string output."""
    try:
        response_dict = response.model_dump()
        formatted_output = f"{response_dict.get('Severity', 'N/A')}"
        return formatted_output
    except Exception as e:
        return f"Error formatting response: {e}"


def format_response(response: TriageResponse) -> str:
    """Format the JSON response into a user-friendly string output."""
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
