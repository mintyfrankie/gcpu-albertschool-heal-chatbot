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

        /* Google colors for branding bar */
        .google-brand-bar {
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        .google-brand-bar span {
            font-size: 1.5rem;
            font-weight: bold;
            letter-spacing: -0.02em;
        }
        
        .google-blue { color: #4285F4; }
        .google-red { color: #DB4437; }
        .google-yellow { color: #F4B400; }
        .google-green { color: #0F9D58; }
        
        /* Gemini badge styling */
        .gemini-badge {
            background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 1rem;
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .powered-by {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1.5rem;
        }

        /* Style for input container to stick to bottom */
        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 3rem;  /* Leave space for disclaimer */
            left: 0;
            right: 0;
            background: white;
            padding: 1rem 1rem;
            z-index: 99;
        }
        
        /* Style for disclaimer to stick to bottom */
        .disclaimer-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 0.5rem 1rem;
            z-index: 99;
            border-top: 1px solid #f0f0f0;
        }

        /* Add padding to chat container to prevent content from being hidden */
        .stChatMessageContent {
            margin-bottom: 120px;  /* Space for input and disclaimer */
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Title area with Google branding and Gemini badge
st.markdown(
    """
    <div class='title-area' style='margin-bottom: 4rem;'>
        <div class='google-brand-bar'>
            <span class='google-blue'>G</span>
            <span class='google-red'>o</span>
            <span class='google-yellow'>o</span>
            <span class='google-blue'>g</span>
            <span class='google-green'>l</span>
            <span class='google-red'>e</span>
        </div>
        <h1>🧑‍⚕️ Heal</h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 0.5rem;'>Your AI-powered medical assistant</p>
        <div class='powered-by'>
            Powered by
            <div class='gemini-badge'>
                ✨ Gemini 1.5 Pro
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Create containers in the right order for proper stacking
chat_container = st.container()
spacer = st.container()  # This will push the input container down
input_container = st.container()

# Display chat messages in the chat container
with chat_container:
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

# Add flexible space to push input to bottom
with spacer:
    st.markdown(
        "<div style='flex-grow: 1; min-height: 200px;'></div>", unsafe_allow_html=True
    )

# Handle input and disclaimer in the input container
with input_container:
    # Chat input
    user_query: str | None = st.chat_input("How can I help you today?")

    # Medical disclaimer (left-aligned, closer to input)
    st.markdown(
        """
        <div class='disclaimer-container'>
            <p style='
                font-size: 0.8rem;
                color: #666;
                margin: 0;
                line-height: 1.4;
            '>
                <strong>Medical Disclaimer:</strong> This chatbot is for informational purposes only and is not a substitute for professional medical advice. 
                In case of emergency, please call your local emergency services immediately.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Handle user input
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with chat_container:
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
