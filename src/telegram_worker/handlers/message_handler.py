"""Message handler module for Telegram bot messages.

This module contains the MessageHandler class which processes different types
of messages received by the Telegram bot and generates appropriate responses.
It handles both command messages and regular text messages.

Attributes:
    logger (logging.Logger): Module level logger for message handling operations
"""

import logging
import telebot
from telebot.types import Message
from langchain_core.runnables import RunnableConfig
from backend.services import process_user_input
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)


class MessageHandler:
    """Handler for processing Telegram bot messages.

    This class contains methods for handling different types of messages
    and commands received by the Telegram bot. It manages message processing,
    error handling, and response generation.

    Attributes:
        config (RunnableConfig): Configuration for message processing with callbacks
        bot (telebot.TeleBot): Reference to the Telegram bot instance for sending messages
    """

    def __init__(self, bot: telebot.TeleBot) -> None:
        """Initialize the message handler.

        Args:
            bot (telebot.TeleBot): Reference to the Telegram bot instance
                                  for sending responses
        """
        self.bot: telebot.TeleBot = bot
        self.config: RunnableConfig = RunnableConfig(
            callbacks=None, tags=["telegram"], metadata={"source": "telegram"}
        )

    def handle_text(self, message: Message) -> None:
        """Handle incoming text messages from users.

        Processes text messages from users and generates appropriate responses
        using the backend service. Handles any errors that occur during processing.

        Args:
            message (Message): Telegram message object containing the user's text
                             and metadata
        """
        try:
            if message.text is None:
                logger.warning("Received message with no text content")
                return

            response_data: dict[str, Any] = process_user_input(
                message.text, config=self.config
            )
            response_text: str = response_data["response"]
            self._send_response(message.chat.id, response_text)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self._send_error_message(message.chat.id)

    def handle_start(self, message: Message) -> None:
        """Handle the /start command from users.

        Sends a welcome message to new users starting the bot, explaining
        its capabilities and how to use it.

        Args:
            message (Message): Telegram message object containing the command
                             and user metadata
        """
        welcome_text: str = (
            "👋 Welcome! I'm your AI medical assistant.\n\n"
            "I can help you assess medical situations and provide guidance. "
            "Please describe your symptoms or concerns."
        )
        self._send_response(message.chat.id, welcome_text)

    def _send_response(self, chat_id: int, text: str) -> None:
        """Send a response message to a specific chat.

        Args:
            chat_id (int): Telegram chat ID to send the message to
            text (str): Message text to send to the user

        Raises:
            Exception: If there's an error sending the message
        """
        try:
            self.bot.send_message(chat_id, text)
            logger.info(f"Sent response to chat {chat_id}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    def _send_error_message(self, chat_id: int) -> None:
        """Send an error message to a specific chat.

        Sends a user-friendly error message when message processing fails.

        Args:
            chat_id (int): Telegram chat ID to send the error message to
        """
        error_text: str = (
            "Sorry, I encountered an error processing your message. "
            "Please try again later."
        )
        self._send_response(chat_id, error_text)
