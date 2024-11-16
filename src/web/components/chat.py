"""Chat interface component for the Streamlit application.

This module provides components for rendering chat messages and handling
user input in the Streamlit interface. It includes support for displaying
messages with optional images and processing user queries through the
backend service.
"""

from typing import Any, Optional
import logging
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from backend.services import process_user_input

logger = logging.getLogger(__name__)


def render_message(
    message: AIMessage | HumanMessage, image_path: Optional[Path] = None
) -> None:
    """Render a single chat message with optional image.

    Args:
        message: The message to render (either AI or Human message)
        image_path: Optional path to an uploaded image to display
    """
    avatar = "🧑‍⚕️" if isinstance(message, AIMessage) else "👤"
    role = "AI" if isinstance(message, AIMessage) else "Human"

    with st.chat_message(role, avatar=avatar):
        if image_path:
            st.image(str(image_path), caption="Uploaded Image")

        st.markdown(
            f"""
            <div class='chat-message {role.lower()}-message'>
                {message.content}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_chat_history(messages: list[AIMessage | HumanMessage]) -> None:
    """Render the complete chat history.

    Args:
        messages: List of messages to render in the chat interface

    Note:
        Future implementation should support retrieving associated images
        from message metadata.
    """
    for message in messages:
        render_message(message)


def extract_ai_message(response: Any) -> Optional[AIMessage]:
    """Extract AI message from various response formats.

    Args:
        response: Response object from the backend service

    Returns:
        Extracted AIMessage or None if extraction fails

    Note:
        Handles multiple response formats including direct AIMessage,
        tuples, strings, and objects with content attributes.
    """
    if isinstance(response, AIMessage):
        return response
    elif isinstance(response, tuple):
        if len(response) >= 2:
            content = response[1]
            if isinstance(content, str):
                return AIMessage(content=content)
            elif hasattr(content, "content"):
                return AIMessage(content=content.content)
    elif isinstance(response, str):
        return AIMessage(content=response)
    elif hasattr(response, "content") and not isinstance(response, tuple):
        return AIMessage(content=response.content)
    return None


def handle_user_input(
    user_query: str,
    chat_container: Any,
    chat_history: list[AIMessage | HumanMessage],
    uploaded_image: Optional[Path] = None,
    thread_id: Optional[str] = None,
) -> None:
    """Handle user input and generate AI response.

    Args:
        user_query: The user's input query
        chat_container: Streamlit container for chat messages
        chat_history: List of chat messages
        uploaded_image: Optional path to an uploaded image
        thread_id: Optional thread ID for conversation tracking

    Note:
        Handles the complete flow from user input to AI response,
        including error handling and message rendering.
    """
    chat_history.append(HumanMessage(content=user_query))

    with chat_container:
        render_message(HumanMessage(content=user_query), uploaded_image)

        try:
            with st.spinner("Analyzing and processing your query..."):
                response = process_user_input(user_query, thread_id=thread_id)

                if response and isinstance(response, dict) and "messages" in response:
                    messages = response["messages"]
                    if messages:
                        ai_message = extract_ai_message(messages[-1])
                        if ai_message:
                            render_message(ai_message)
                            chat_history.append(ai_message)
                        else:
                            logger.error("Failed to extract AI message from response")
                            st.error("Unable to process the response")
                    else:
                        logger.error("Empty messages list in response")
                        st.error("No response generated from the system")
                else:
                    logger.error(f"Unexpected response format: {response}")
                    st.error("Unexpected response format from the system")

        except Exception as e:
            logger.exception("Error in chat processing")
            st.error(f"Error processing your request: {str(e)}")
