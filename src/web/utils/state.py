"""State management utilities for the Streamlit application.

This module provides utilities for managing chat history and other stateful
data in the Streamlit application using session state.
"""

from typing import List
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage


def initialize_chat_history() -> List[AIMessage | HumanMessage]:
    """Initialize or retrieve chat history from session state.

    Creates a new chat history list if one doesn't exist in the session state,
    or returns the existing one.

    Returns:
        A list of chat messages (both AI and Human messages)
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history
