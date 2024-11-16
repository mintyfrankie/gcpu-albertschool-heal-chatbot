"""Chat interface component for the Streamlit application."""

from typing import Any, Optional
import logging
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from backend.services import process_user_input
from web.utils.image import process_uploaded_image

# Configure logging
logger = logging.getLogger(__name__)


def render_message(
    message: AIMessage | HumanMessage, image_path: Optional[Path] = None
) -> None:
    """Render a single chat message with optional image.

    Args:
        message: The message to render
        image_path: Optional path to an uploaded image
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
    """Render the chat history.

    Args:
        messages: List of messages to render
    """
    for message in messages:
        # TODO: Add support for retrieving associated images from message metadata
        render_message(message)


def handle_user_input(
    user_query: str,
    chat_container: Any,
    chat_history: list[AIMessage | HumanMessage],
    uploaded_image: Optional[Path] = None,
) -> None:
    """Handle user input and generate AI response using the graph workflow.

    Args:
        user_query: The user's input query
        chat_container: Streamlit container for chat messages
        chat_history: List of chat messages
        uploaded_image: Optional path to an uploaded image
    """
    chat_history.append(HumanMessage(content=user_query))

    with chat_container:
        render_message(HumanMessage(content=user_query), uploaded_image)

        try:
            with st.spinner("Analyzing and processing your query..."):
                # Process through the graph workflow
                response = process_user_input(user_query)

                # Extract response from the graph output
                if response and isinstance(response, dict) and "messages" in response:
                    messages = response["messages"]
                    if messages:
                        last_message = messages[-1]

                        # Handle different response formats
                        if isinstance(last_message, AIMessage):
                            ai_message = last_message
                        elif isinstance(last_message, tuple) and len(last_message) == 2:
                            _, content = last_message
                            ai_message = AIMessage(content=content)
                        elif isinstance(last_message, str):
                            ai_message = AIMessage(content=last_message)
                        else:
                            logger.warning(
                                f"Unexpected message format, attempting to extract content: {last_message}"
                            )
                            content = getattr(
                                last_message, "content", str(last_message)
                            )
                            ai_message = AIMessage(content=content)

                        render_message(ai_message)
                        chat_history.append(ai_message)
                    else:
                        logger.error("Empty messages list in response")
                        st.error("No response generated from the system")
                else:
                    logger.error(f"Unexpected response format: {response}")
                    st.error("Unexpected response format from the system")

        except Exception as e:
            st.error(f"Error processing your request: {str(e)}")
            logger.exception("Error in chat processing")
