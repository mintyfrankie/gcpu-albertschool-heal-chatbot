from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import backend
import format_output

import os


app = FastAPI(
    title="Medical Triage Chatbot API", description="API for a Medical Triage Chatbot"
)


# Pydantic model for request and response
class UserQuery(BaseModel):
    query: str
    chat_history: list[str] = []  # Default to empty list if not provided


@app.post("/triage/")
async def get_triage_response(user_query: UserQuery):
    """
    Endpoint to receive user queries and generate a triage response.

    Args:
    - user_query (UserQuery): Input containing the user's query and optionally their chat history.

    Returns:
    - JSON response with formatted response from the chatbot.
    """
    try:
        response = backend.get_response(user_query.query, user_query.chat_history)
        formatted_response = format_output.format_response(response)
        return {"response": formatted_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
