"""
Streamlit app prototype for frontend display with custom styling.

TODO: add image attachments capability
TODO: add location sharing capability
"""

from typing import Final

import streamlit as st
from dotenv import load_dotenv

from web.components.chat import handle_user_input, render_chat_history
from web.components.header import render_header
from web.components.styles import CUSTOM_CSS, DISCLAIMER_HTML
from web.utils.state import initialize_chat_history

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
        user_query = st.chat_input("How can I help you today?")
        st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)

        if user_query:
            handle_user_input(user_query, chat_container, chat_history)


if __name__ == "__main__":
    main()
