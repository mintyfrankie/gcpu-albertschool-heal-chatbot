"""State management utilities for the Streamlit application."""

from typing import List

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage


def initialize_chat_history() -> List[AIMessage | HumanMessage]:
    """
    Initialize or retrieve chat history from session state.

    Returns:
        List of chat messages
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history
