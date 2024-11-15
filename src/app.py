"""
Streamlit app prototype for frontend display with custom styling.
"""

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from chatbot.services import stream_graph_updates

# Load environment variables
load_dotenv()

# App configuration - MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="Medical Pre-triage Chatbot",
    page_icon="🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS styling
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Global font settings */
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Remove top padding and header decoration */
        .stApp > header {
            background-color: transparent;
        }
        
        [data-testid="stHeader"] {
            display: none;
        }
        
        .stDeployButton {
            display: none;
        }

        /* Remove extra spacing and scrollbar */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 1000px;
        }

        .stApp {
            margin: 0 auto;
            overflow: hidden;
        }
        
        /* Chat messages */
        .stChatMessage {
            padding: 1rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Title area */
        .title-area {
            text-align: center;
            padding: 1rem 0;
            margin-top: -2rem;
            margin-bottom: 2rem;
        }

        /* Header styling */
        h1 {
            color: #1565C0;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            text-align: center;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em;
        }

        /* Chat input styling */
        .stChatInput {
            font-family: 'Inter', sans-serif !important;
        }
        
        input.stChatInput > div > input {
            font-family: 'Inter', sans-serif !important;
        }

        /* AI message specific styling */
        .ai-message {
            background-color: #E3F2FD;
            border-left: 4px solid #1565C0;
        }
        
        /* Human message specific styling */
        .human-message {
            background-color: #FFFFFF;
            border-left: 4px solid #2196F3;
        }

        /* Improve text rendering */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Title area with disclaimer
st.markdown(
    """
    <div class='title-area'>
        <h1>🧑‍⚕️ Heal</h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 1rem;'>Your AI-powered medical assistant</p>
        <p style='font-size: 0.8rem; color: #666; max-width: 800px; margin: 0 auto; padding: 0 1rem;'>
            <strong>Medical Disclaimer:</strong> This chatbot is for informational purposes only and is not a substitute for professional medical advice. 
            In case of emergency, please call your local emergency services immediately.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat messages
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI", avatar="🧑‍⚕️"):
            st.markdown(
                f"""
                <div class='chat-message ai-message'>
                    {message.content}
                </div>
            """,
                unsafe_allow_html=True,
            )
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human", avatar="👤"):
            st.markdown(
                f"""
                <div class='chat-message human-message'>
                    {message.content}
                </div>
            """,
                unsafe_allow_html=True,
            )

# Chat input and response handling
user_query: str | None = st.chat_input("How can I help you today?")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human", avatar="👤"):
        st.markdown(
            f"""
            <div class='chat-message human-message'>
                {user_query}
            </div>
        """,
            unsafe_allow_html=True,
        )

    try:
        with st.spinner("Thinking..."):
            events = stream_graph_updates(user_query)
            *_, last_response = events

            with st.chat_message("AI", avatar="🧑‍⚕️"):
                st.markdown(
                    f"""
                    <div class='chat-message ai-message'>
                        {last_response["messages"][-1].content}
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.session_state.chat_history.append(
                AIMessage(content=last_response["messages"][-1].content)
            )
    except Exception as e:
        st.error(f"Error generating response: {e}")
