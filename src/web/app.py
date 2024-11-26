"""Streamlit web application for the medical assistant interface.

This module serves as the main entry point for the Streamlit web application.
It handles the initialization of the chat interface, session management,
and user interactions including image uploads and location sharing.
"""

import logging
import uuid
from typing import Any, Final, Tuple

import streamlit as st
from dotenv import load_dotenv
from streamlit_js_eval import get_geolocation

from backend import platform, user_location
from backend.services import main_graph
from web.components.chat import handle_user_input, render_chat_history
from web.components.header import render_header
from web.components.styles import CUSTOM_CSS, DISCLAIMER_HTML
from web.utils.image import process_uploaded_image
from web.utils.state import initialize_chat_history

platform = "web"

# Configure logging
logger = logging.getLogger(__name__)

# Application configuration constants
PAGE_CONFIG: Final[dict] = {
    "page_title": "Heal",
    "page_icon": "🧑‍⚕️",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}

# Type alias for Streamlit container
Container = Any


def initialize_session() -> None:
    """Initialize session state variables.

    Sets up session ID and initializes the graph workflow if not already present
    in the session state.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "graph_initialized" not in st.session_state:
        config, graph, llm, memory = main_graph()
        st.session_state.update(
            {
                "config": config,
                "graph": graph,
                "llm": llm,
                "memory": memory,
                "graph_initialized": True,
            }
        )


def setup_interface() -> Tuple[Container, Container]:
    """Set up the main interface containers.

    Returns:
        A tuple containing the chat and input containers
    """
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    render_header()

    return st.container(border=False), st.container(border=False)


def handle_user_interaction(input_container: Container) -> None:
    """Handle user interaction including file upload and message input.

    Args:
        input_container: Streamlit container for input elements
    """
    with input_container:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                user_query = st.text_input(
                    " ",
                    key="chat_input",
                    placeholder="Type your message here...",
                    label_visibility="hidden",
                )
            with col2:
                uploaded_file = st.file_uploader(
                    "Upload Image",
                    type=["png", "jpg", "jpeg"],
                    key="file_uploader_key",
                    label_visibility="hidden",
                )
            with col3:
                submit_button = st.form_submit_button("Send")

            if submit_button and user_query:
                image_path = (
                    process_uploaded_image(uploaded_file) if uploaded_file else None
                )
                handle_user_input(
                    user_query,
                    st.session_state.chat_container,
                    initialize_chat_history(),
                    image_path,
                    thread_id=st.session_state.session_id,
                )
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Initialize and run the Streamlit application.

    This function sets up the application state, initializes the interface,
    and handles the main application loop including user input processing.
    """
    load_dotenv("./credentials/.env")
    initialize_session()

    chat_container, input_container = setup_interface()
    st.session_state.chat_container = chat_container
    chat_history = initialize_chat_history()

    st.session_state.location = get_geolocation()
    if st.session_state.location:
        user_location["latitude"] = st.session_state.location["coords"]["latitude"]
        user_location["longitude"] = st.session_state.location["coords"]["longitude"]

    with chat_container:
        render_chat_history(chat_history)

    with input_container:
        handle_user_interaction(input_container)
        st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
