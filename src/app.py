"""
Streamlit app prototype for frontend display
"""

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# from chatbot import format_response, stream_graph_updates
from chatbot.services import main_graph, stream_graph_updates

# Load environment variables
load_dotenv()


# App configuration
st.set_page_config(page_title="Medical Pre-triage Chatbot", page_icon="🧑‍⚕️")
st.title("Medical Pre-Triage Chatbot")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # st.session_state.chat_history.append(
    # AIMessage(content="Hello, I am a bot. How can I help you?")
    # )


# Display the chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# config, graph, llm, memory = main_graph()

# Capture user input
user_query: str | None = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    # Get response and format it
    try:
        events = stream_graph_updates(user_query)
        *_, last_response = events

        with st.chat_message("AI"):
            st.write(
                last_response["messages"][-1].content
            )  # Display the formatted response

        st.session_state.chat_history.append(
            AIMessage(content=last_response["messages"][-1].content)
        )
    except Exception as e:
        st.error(f"Error generating response: {e}")
