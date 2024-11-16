"""Chat interface component for the Streamlit application.

This module provides components for rendering chat messages and handling
user input in the Streamlit interface. It includes support for displaying
messages with optional images and processing user queries through the
backend service.
"""

from typing import Any, Optional
import logging
from PIL import Image

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from backend.services import process_user_input
from web.utils.image import image_to_bytes, bytes_to_image

logger = logging.getLogger(__name__)


def render_message(
    message: AIMessage | HumanMessage, image: Optional[Image.Image] = None
) -> None:
    """Render a single chat message with optional image.

    Args:
        message: The message to render (either AI or Human message)
        image: Optional PIL Image to display
    """
    avatar = "🧑‍⚕️" if isinstance(message, AIMessage) else "👤"
    role = "AI" if isinstance(message, AIMessage) else "Human"

    with st.chat_message(role, avatar=avatar):
        if image:
            st.image(image, caption="Uploaded Image", use_container_width=True)

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
    """
    for message in messages:
        # Get image from message metadata if it exists
        image = (
            message.additional_kwargs.get("image")
            if hasattr(message, "additional_kwargs")
            else None
        )
        render_message(message, image)


def extract_ai_message(response: Any) -> Optional[AIMessage]:
    """Extract AI message from various response formats.

    Args:
        response: Response object from the backend service

    Returns:
        Extracted AIMessage or None if extraction fails
    """
    if isinstance(response, AIMessage):
        return response
    elif isinstance(response, tuple) and len(response) >= 2:
        msg_type, content, *_ = response
        if msg_type == "ai" and isinstance(content, str):
            return AIMessage(content=content)
    elif isinstance(response, dict) and "messages" in response:
        messages = response["messages"]
        if messages and isinstance(messages[-1], tuple):
            msg_type, content = messages[-1]
            if msg_type == "ai" and isinstance(content, str):
                return AIMessage(content=content)
    return None


def handle_user_input(
    user_query: str,
    chat_container: Any,
    chat_history: list[AIMessage | HumanMessage],
    uploaded_image: Optional[Image.Image] = None,
    thread_id: Optional[str] = None,
) -> None:
    """Handle user input and generate AI response."""
    image_bytes = image_to_bytes(uploaded_image) if uploaded_image else None

    human_message = HumanMessage(
        content=user_query,
        additional_kwargs={"image_bytes": image_bytes} if image_bytes else {},
    )
    chat_history.append(human_message)

    with chat_container:
        display_image = bytes_to_image(image_bytes) if image_bytes else None
        render_message(human_message, display_image)

        try:
            with st.spinner("Analyzing and processing your query..."):
                config: RunnableConfig = {
                    "configurable": {
                        "thread_id": thread_id or "default",
                        "checkpoint_ns": "chat",
                        "checkpoint_id": thread_id or "default",
                    }
                }

                response = process_user_input(
                    user_query,
                    config=config,
                    image=image_bytes if image_bytes else None,
                )

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
