"""Header component for the Streamlit application."""

from typing import Final

import streamlit as st

HEADER_HTML: Final[str] = """
    <div class='title-area' style='margin-bottom: 4rem;'>
        <h1>🧑‍⚕️ Heal</h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 0.5rem;'>Your AI-powered medical assistant</p>
        <div class='powered-by'>
            Powered by
            <div class='gemini-badge'>
                ✨ Gemini 1.5 Pro
            </div>
        </div>
    </div>
"""


def render_header() -> None:
    """Render the application header."""
    st.markdown(HEADER_HTML, unsafe_allow_html=True)
