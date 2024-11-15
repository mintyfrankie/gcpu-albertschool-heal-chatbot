"""Chat interface component for the Streamlit application."""

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from chatbot.services import stream_graph_updates


def render_message(message: AIMessage | HumanMessage) -> None:
    """
    Render a single chat message.

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
    """
    Render the chat history.

    Args:
        messages: List of messages to render
    """
    for message in messages:
        render_message(message)


def handle_user_input(
    user_query: str,
    chat_container,
    chat_history: list[AIMessage | HumanMessage],
) -> None:
    """
    Handle user input and generate AI response.

    Args:
        user_query: The user's input query
        chat_container: Streamlit container for chat messages
        chat_history: List of chat messages
    """
    chat_history.append(HumanMessage(content=user_query))

    with chat_container:
        render_message(HumanMessage(content=user_query))

        try:
            with st.spinner("Thinking..."):
                events = stream_graph_updates(user_query)
                *_, last_response = events

                ai_message = AIMessage(content=last_response["messages"][-1].content)
                render_message(ai_message)
                chat_history.append(ai_message)

        except Exception as e:
            st.error(f"Error generating response: {e}")
