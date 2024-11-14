"""
Worker for Telegram bot that integrates with Langchain for chat capabilities
"""

import asyncio
import os
from typing import AsyncIterator, Optional, Dict, List
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

# Load environment variables
token = os.getenv("TELEGRAM_TOKEN")
assert token is not None, "TELEGRAM_TOKEN is not set"

# Initialize bot and LLM
bot = AsyncTeleBot(token)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
)

# Chat history storage: chat_id -> list of messages
chat_histories: Dict[int, List[HumanMessage | AIMessage]] = {}

# Setup prompt template with proper message structure and chat history
SYSTEM_PROMPT = """You are a helpful and friendly AI assistant. Maintain a natural conversation flow and remember context from previous messages. Be concise but engaging in your responses."""

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessage(content="{message}"),
    ]
)

# Create the chain
chain = prompt | llm | StrOutputParser()


def get_chat_history(chat_id: int) -> List[HumanMessage | AIMessage]:
    """
    Get chat history for a specific chat ID.

    Args:
        chat_id: The Telegram chat ID

    Returns:
        List of chat messages
    """
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    return chat_histories[chat_id]


def update_chat_history(chat_id: int, human_message: str, ai_message: str) -> None:
    """
    Update chat history with new messages.

    Args:
        chat_id: The Telegram chat ID
        human_message: The user's message
        ai_message: The AI's response
    """
    history = get_chat_history(chat_id)
    history.append(HumanMessage(content=human_message))
    history.append(AIMessage(content=ai_message))

    # Keep only last 10 messages to prevent context from growing too large
    chat_histories[chat_id] = history[-10:]


async def stream_response(message: Message, response_gen: AsyncIterator[str]) -> None:
    """
    Stream the response to the user, updating the message as new chunks arrive.

    Args:
        message: The original Telegram message to reply to
        response_gen: AsyncIterator containing streamed response chunks
    """
    full_response = ""
    sent_message: Optional[Message] = None

    try:
        async for chunk in response_gen:
            full_response += chunk

            # Send first message or edit existing message
            if sent_message is None:
                sent_message = await bot.reply_to(message, full_response)
            else:
                # Only update if response changed significantly (every 20 chars)
                if len(full_response) % 20 == 0:
                    try:
                        await bot.edit_message_text(
                            full_response, sent_message.chat.id, sent_message.message_id
                        )
                    except Exception:
                        continue

        # Ensure final message is complete
        if sent_message and message.text is not None:
            try:
                await bot.edit_message_text(
                    full_response, sent_message.chat.id, sent_message.message_id
                )
                # Update chat history with the complete exchange
                update_chat_history(message.chat.id, message.text, full_response)
            except Exception:
                pass

    except Exception as e:
        error_msg = f"Sorry, an error occurred: {str(e)}"
        if sent_message:
            await bot.edit_message_text(
                error_msg, sent_message.chat.id, sent_message.message_id
            )
        else:
            await bot.reply_to(message, error_msg)


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message: Message) -> None:
    """Handle start and help commands"""
    # Clear chat history when starting new conversation
    chat_histories[message.chat.id] = []

    welcome_text = (
        "👋 Hi! I'm an AI assistant that can help answer your questions.\n\n"
        "I'll remember our conversation context to provide better responses.\n"
        "Just start chatting with me!"
    )
    await bot.reply_to(message, welcome_text)


@bot.message_handler(commands=["clear"])
async def clear_history(message: Message) -> None:
    """Handle clearing chat history"""
    chat_histories[message.chat.id] = []
    await bot.reply_to(message, "Chat history cleared! Let's start fresh.")


@bot.message_handler(func=lambda message: True)
async def handle_message(message: Message) -> None:
    """Handle incoming messages by streaming responses from LLM"""
    try:
        # Show typing indicator
        await bot.send_chat_action(message.chat.id, "typing")

        # Get chat history
        chat_history = get_chat_history(message.chat.id)

        # Get streaming response with chat history context
        response_gen = chain.astream(
            {"message": message.text, "chat_history": chat_history}
        )

        # Stream response back to user
        await stream_response(message, response_gen)

    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        await bot.reply_to(message, error_message)


async def main() -> None:
    """Main function to run the bot"""
    try:
        print("Bot started...")
        await bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        print(f"Bot stopped due to error: {e}")
        await bot.close_session()


if __name__ == "__main__":
    asyncio.run(main())
