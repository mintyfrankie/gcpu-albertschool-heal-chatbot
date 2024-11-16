"""Chat interface component for the Streamlit application."""

from typing import Any

import logging
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from backend.services import process_user_input

# Configure logging
logger = logging.getLogger(__name__)


def render_message(message: AIMessage | HumanMessage) -> None:
    """Render a single chat message.

    Args:
        message: The message to render
    """
    avatar = "🧑‍⚕️" if isinstance(message, AIMessage) else "👤"
    role = "AI" if isinstance(message, AIMessage) else "Human"

    with st.chat_message(role, avatar=avatar):
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
        render_message(message)


def handle_user_input(
    user_query: str,
    chat_container: Any,
    chat_history: list[AIMessage | HumanMessage],
) -> None:
    """Handle user input and generate AI response using the graph workflow.

    Args:
        user_query: The user's input query
        chat_container: Streamlit container for chat messages
        chat_history: List of chat messages
    """
    chat_history.append(HumanMessage(content=user_query))

    with chat_container:
        render_message(HumanMessage(content=user_query))

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
                            # Try to extract content from unknown format
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
