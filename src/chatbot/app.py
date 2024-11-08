import streamlit as st

import backend
import format_output

from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App configuration
st.set_page_config(page_title="Medical Pre-triage Chatbot", page_icon="🧑‍⚕️")
st.title("Medical Pre-Triage Chatbot")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]


# Display the chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# Capture user input
user_query: str | None = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    # Get response and format it
    try:
        response = backend.get_response(user_query, st.session_state.chat_history)
        formatted_response = format_output.format_response(response)

        with st.chat_message("AI"):
            st.write(formatted_response)  # Display the formatted response

        st.session_state.chat_history.append(AIMessage(content=response))
    except Exception as e:
        st.error(f"Error generating response: {e}")
