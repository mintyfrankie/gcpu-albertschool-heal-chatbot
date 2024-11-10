"""
Utility functions
"""

import json


def format_response(response: str) -> str:
    """Format the JSON response into a user-friendly string output."""
    try:
        response_dict = json.loads(response)
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
    except (json.JSONDecodeError, KeyError) as e:
        return f"Error formatting response: {e}"
