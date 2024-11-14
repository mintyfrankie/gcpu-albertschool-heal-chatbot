"""
Worker for Telegram bot that integrates with Langchain for chat capabilities
"""

import asyncio
import os
from typing import AsyncIterator, Optional
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Load environment variables
token = os.getenv("TELEGRAM_TOKEN")
assert token is not None, "TELEGRAM_TOKEN is not set"

# Initialize bot and LLM
bot = AsyncTeleBot(token)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", temperature=0, convert_system_message_to_human=True
)

# Setup prompt template
PROMPT_TEMPLATE = """You are a helpful AI assistant. Respond to the user's message in a clear and concise way.

User's message: {message}

Response:"""

prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

# Create the chain
chain = prompt | llm | StrOutputParser()


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
                        # Handle rate limiting or other edit errors
                        continue

        # Ensure final message is complete
        if sent_message:
            try:
                await bot.edit_message_text(
                    full_response, sent_message.chat.id, sent_message.message_id
                )
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


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
async def send_welcome(message: Message) -> None:
    """Handle start and help commands"""
    welcome_text = (
        "👋 Hi! I'm an AI assistant that can help answer your questions.\n\n"
        "Just send me a message and I'll do my best to help!"
    )
    await bot.reply_to(message, welcome_text)


# Handle all text messages
@bot.message_handler(func=lambda message: True)
async def handle_message(message: Message) -> None:
    """Handle incoming messages by streaming responses from LLM"""
    try:
        # Show typing indicator
        await bot.send_chat_action(message.chat.id, "typing")

        # Get streaming response
        response_gen = chain.astream({"message": message.text})

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
