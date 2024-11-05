import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

# app config
st.set_page_config(page_title="Medical Triage Chatbot", page_icon="🧑‍⚕️")
st.title("Medical Triage Chatbot")


def get_response(user_question: str, chat_history:str):

    template = """
    You are a medical assistant specializing in initial triage. When assessing a patient, you should evaluate the severity of their symptoms as "Mild," "Moderate," or "Severe" based on their descriptions and any additional context from an image if provided. 

    Please respond in the following structured format:
    {{
        "Advice": "[Provide advice based on the severity]",
        "Severity": "[Severity level: Mild, Moderate, or Severe]"
    }}

    Consider both text descriptions of symptoms and image descriptions when formulating your response.
    Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: Patient reports the following symptoms: {user_question}.

    Please assess the severity and provide advice.
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.4,
    )

    chain = prompt | llm | StrOutputParser()

    return chain.stream(
        {
            "chat_history": chat_history,
            "user_question": user_question,
        }
    )


# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]


# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query: str | None = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = st.write_stream(
            get_response(user_query, st.session_state.chat_history)
        )

    st.session_state.chat_history.append(AIMessage(content=response))
