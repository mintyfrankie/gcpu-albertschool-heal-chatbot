"""
Streamlit app prototype for frontend display with custom styling.

TODO: add image attachments capability
TODO: add location sharing capability
"""

from typing import Final
import logging

import streamlit as st
from dotenv import load_dotenv

from web.components.chat import handle_user_input, render_chat_history
from web.components.header import render_header
from web.components.styles import CUSTOM_CSS, DISCLAIMER_HTML
from web.utils.state import initialize_chat_history
from backend.services import main_graph
from web.utils.image import process_uploaded_image

# Configure logging
logger = logging.getLogger(__name__)

# Constants
PAGE_CONFIG: Final[dict] = {
    "page_title": "Heal",
    "page_icon": "🧑‍⚕️",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}


def main() -> None:
    """Initialize and run the Streamlit application."""
    load_dotenv()

    # Initialize the graph workflow
    if "graph_initialized" not in st.session_state:
        config, graph, llm, memory = main_graph()
        st.session_state.config = config
        st.session_state.graph = graph
        st.session_state.llm = llm
        st.session_state.memory = memory
        st.session_state.graph_initialized = True

    # Configure page
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Render header
    render_header()

    # Initialize state and containers
    chat_history = initialize_chat_history()
    chat_container = st.container()
    input_container = st.container()

    # Render chat interface
    with chat_container:
        render_chat_history(chat_history)

    with input_container:
        uploaded_file = st.file_uploader(
            "Upload Image",
            type=["png", "jpg", "jpeg"],
            key="image_uploader",
            label_visibility="hidden",
        )
        user_query = st.chat_input("How can I help you today?")
        st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)

        if user_query:
            image_path = (
                process_uploaded_image(uploaded_file) if uploaded_file else None
            )
            handle_user_input(user_query, chat_container, chat_history, image_path)


if __name__ == "__main__":
    main()
