"""Message handler module for Telegram bot messages.

This module contains the MessageHandler class which processes different types
of messages received by the Telegram bot and generates appropriate responses.
It handles both command messages and regular text messages.

Attributes:
    logger (logging.Logger): Module level logger for message handling operations
"""

import logging
import os
import time
from typing import Any, Optional, cast

import telebot
from langchain_core.runnables import RunnableConfig
from telebot.types import Message, PhotoSize

from backend import user_location
from backend.services import process_user_input
from telegram_worker.config import settings

logger: logging.Logger = logging.getLogger(__name__)


class MessageHandler:
    """Handler for processing Telegram bot messages.

    This class contains methods for handling different types of messages
    and commands received by the Telegram bot. It manages message processing,
    error handling, and response generation.

    Attributes:
        config (RunnableConfig): Configuration for message processing with callbacks
        bot (telebot.TeleBot): Reference to the Telegram bot instance for sending messages
        _image_context (dict[int, bytes]): Temporary storage for image data by chat ID
    """

    def __init__(self, bot: telebot.TeleBot) -> None:
        """Initialize the message handler.

        Args:
            bot (telebot.TeleBot): Reference to the Telegram bot instance
                                  for sending responses
        """
        self.bot: telebot.TeleBot = bot
        self._ensure_temp_dir()
        self._image_context: dict[int, bytes] = {}

    def _ensure_temp_dir(self) -> None:
        """Ensure temporary directory for image storage exists."""
        os.makedirs(settings.TEMP_IMAGE_DIR, exist_ok=True)

    def handle_photo(self, message: Message) -> None:
        """Handle incoming photo messages from users.

        Downloads and processes photos sent by users, storing them temporarily
        and generating appropriate responses.

        Args:
            message (Message): Telegram message object containing the photo
                             and metadata
        """
        try:
            if not message.photo:
                logger.warning("Received photo message with no photo content")
                return

            photos = cast(list[PhotoSize], message.photo)
            photo = max(photos, key=lambda x: x.file_size or 0)

            if not photo or not photo.file_id:
                logger.warning("No valid photo found in message")
                return

            file_info = self.bot.get_file(photo.file_id)
            if not file_info or not file_info.file_path:
                logger.error("Could not get file info for photo")
                return

            downloaded_file = self.bot.download_file(file_info.file_path)

            self._image_context[message.chat.id] = downloaded_file

            file_name = f"{message.chat.id}_{photo.file_id}.jpg"
            file_path = os.path.join(settings.TEMP_IMAGE_DIR, file_name)

            with open(file_path, "wb") as new_file:
                new_file.write(downloaded_file)

            logger.info(f"Saved image to {file_path}")

            self._send_response(
                message.chat.id,
                "I've received your image. Please provide any additional context or questions about it.",
            )

            # Clean up old files
            self._cleanup_old_images()

        except Exception as e:
            logger.error(f"Error processing photo: {str(e)}", exc_info=True)
            self._send_error_message(message.chat.id)

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

            logger.info(
                f"Processing message: {message.text} from chat {message.chat.id}"
            )

            # Create config with required checkpoint keys
            config: RunnableConfig = RunnableConfig(
                callbacks=None,
                tags=["telegram"],
                metadata={"source": "telegram"},
                configurable={
                    "thread_id": str(message.chat.id),
                    "checkpoint_ns": "telegram",
                    "checkpoint_id": f"chat_{message.chat.id}",
                },
            )

            image_data: Optional[bytes] = self._image_context.pop(message.chat.id, None)

            response_data: dict[str, Any] = process_user_input(
                message.text, config=config, image=image_data
            )

            logger.info(f"Received response data: {response_data}")

            # Extract the AI message from the response
            if "messages" in response_data:
                messages = response_data["messages"]
                if isinstance(messages, list) and messages:
                    for msg in messages:
                        if isinstance(msg, tuple) and len(msg) == 2:
                            msg_type, msg_content = msg
                            if msg_type == "ai" and msg_content:
                                self._send_response(message.chat.id, msg_content)
                                return

            logger.error(f"Invalid response format: {response_data}")
            self._send_error_message(message.chat.id)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            self._send_error_message(message.chat.id)

    def _cleanup_old_images(self) -> None:
        """Clean up old temporary image files.

        Removes image files older than the configured retention period.
        """
        try:
            current_time = time.time()
            for filename in os.listdir(settings.TEMP_IMAGE_DIR):
                file_path = os.path.join(settings.TEMP_IMAGE_DIR, filename)
                if (
                    os.path.getmtime(file_path)
                    < current_time - settings.IMAGE_RETENTION_PERIOD
                ):
                    os.remove(file_path)
                    logger.info(f"Cleaned up old image: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up images: {str(e)}")

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
            "You can send me text descriptions of your symptoms or concerns, "
            "and you can also share relevant images for better assessment.\n\n"
            "Please describe your symptoms or concerns, or share an image along "
            "with context about what you'd like me to examine."
        )

        self.handle_location(message)
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

    def handle_location(self, message: Message) -> None:
        """Handle incoming location messages from users.

        Processes the user's location and provides a response based on it.

        Args:
            message (Message): Telegram message object containing location data
                               and user metadata
        """
        try:
            location = message.get("location", {})

            # Store the location in the global user_locations dictionary
            user_location["latitude"] = location.get("latitude", None)
            user_location["longitude"] = location.get("longitude", None)

        except Exception as e:
            logger.error(f"Error handling location message: {str(e)}")
            # self._send_error_message(message.chat.id)
