"""
Streamlit app prototype for frontend display with custom styling.
"""

# TODO: add image attachments capability
# TODO: add location sharing capability

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from chatbot.services import stream_graph_updates

load_dotenv()

st.set_page_config(
    page_title="Heal",
    page_icon="🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        .stApp > header {
            background-color: transparent;
        }
        
        [data-testid="stHeader"] {
            display: none;
        }
        
        .stDeployButton {
            display: none;
        }

        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 1000px;
        }

        .stApp {
            margin: 0 auto;
            overflow: hidden;
        }
        
        .stChatMessage {
            padding: 1.5rem;
            border-radius: 20px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .title-area {
            text-align: center;
            padding: 1rem 0;
            margin-top: -2rem;
            margin-bottom: 2rem;
        }

        h1 {
            color: #1565C0;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em;
        }

        .stChatInput {
            font-family: 'Inter', sans-serif !important;
        }
        
        input.stChatInput > div > input {
            font-family: 'Inter', sans-serif !important;
        }

        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
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

        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 5rem; 
            
            background: white;
            z-index: 99;
        }

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

    </style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_container = st.container()
spacer = st.container()
input_container = st.container()

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


with input_container:
    user_query: str | None = st.chat_input("How can I help you today?")
    st.markdown(
        """
        <div class='disclaimer-container'>
            <p style='
                font-size: 0.7rem;
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
