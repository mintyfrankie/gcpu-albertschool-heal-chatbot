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

from langchain_core.runnables import RunnableConfig
from telegram import PhotoSize, Update
from telegram.ext import ContextTypes

from backend import platform, user_location
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

    def __init__(self, application) -> None:
        """Initialize the message handler.

        Args:
            bot: Reference to the Telegram bot instance for sending responses
        """
        self.application = application
        self._ensure_temp_dir()
        self._image_context: dict[int, bytes] = {}

    def _ensure_temp_dir(self) -> None:
        """Ensure temporary directory for image storage exists."""
        os.makedirs(settings.TEMP_IMAGE_DIR, exist_ok=True)

    async def handle_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming photo messages from users.

        Downloads and processes photos sent by users, storing them temporarily
        and generating appropriate responses.

        Args:
            update (Update): Telegram update object containing the photo
                            and metadata
            context (ContextTypes.DEFAULT_TYPE): Context for the message
        """
        try:
            print("Update Message:", update.message)
            if not update.message.photo:
                logger.warning("Received photo message with no photo content")
                return

            photos = cast(list[PhotoSize], update.message.photo)
            photo = max(photos, key=lambda x: x.file_size or 0)

            if not photo or not photo.file_id:
                logger.warning("No valid photo found in message")
                return

            file_info = await self.application.bot.get_file(photo.file_id)
            if not file_info or not file_info.file_path:
                logger.error("Could not get file info for photo")
                return

            downloaded_file = await file_info.download_as_bytearray()

            self._image_context[update.effective_chat.id] = downloaded_file

            file_name = f"{update.effective_chat.id}_{photo.file_id}.jpg"
            file_path = os.path.join(settings.TEMP_IMAGE_DIR, file_name)

            with open(file_path, "wb") as new_file:
                new_file.write(downloaded_file)

            logger.info(f"Saved image to {file_path}")

            if update.message.caption:
                logger.info(
                    f"Processing photo message with caption: {update.message.caption} from chat {update.effective_chat.id}"
                )

                # Create config with required checkpoint keys
                config: RunnableConfig = RunnableConfig(
                    callbacks=None,
                    tags=["telegram"],
                    metadata={"source": "telegram"},
                    configurable={
                        "thread_id": str(update.effective_chat.id),
                        "checkpoint_ns": "telegram",
                        "checkpoint_id": f"chat_{update.effective_chat.id}",
                    },
                )

                image_data: Optional[bytes] = self._image_context.pop(
                    update.effective_chat.id, None
                )
                response_data: dict[str, Any] = process_user_input(
                    update.message.caption, config=config, image=image_data
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
                                    await self._send_response(
                                        update.effective_chat.id, msg_content
                                    )
                                    # Clean up old files
                                    self._cleanup_old_images()
                                    return

            await self._send_response(
                update.effective_chat.id,
                "I've received your image. Please provide any additional context or questions about it.",
            )

            # Clean up old files
            self._cleanup_old_images()

        except Exception as e:
            logger.error(f"Error processing photo: {str(e)}", exc_info=True)
            await self._send_error_message(update.effective_chat.id)

    async def handle_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming text messages from users.

        Processes text messages from users and generates appropriate responses
        using the backend service. Handles any errors that occur during processing.

        Args:
            update (Update): Telegram update object containing the user's text
                            and metadata about the sender
            context (ContextTypes.DEFAULT_TYPE): Context for the message
        """
        try:
            if not update.message.text:
                logger.warning("Received message with no text content")
                return

            logger.info(
                f"Processing message: {update.message.text} from chat {update.effective_chat.id}"
            )

            # Create config with required checkpoint keys
            config: RunnableConfig = RunnableConfig(
                callbacks=None,
                tags=["telegram"],
                metadata={"source": "telegram"},
                configurable={
                    "thread_id": str(update.effective_chat.id),
                    "checkpoint_ns": "telegram",
                    "checkpoint_id": f"chat_{update.effective_chat.id}",
                },
            )

            image_data: Optional[bytes] = self._image_context.pop(
                update.effective_chat.id, None
            )

            response_data: dict[str, Any] = process_user_input(
                update.message.text, config=config, image=image_data
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
                                await self._send_response(
                                    update.effective_chat.id, msg_content
                                )
                                return

            logger.error(f"Invalid response format: {response_data}")
            await self._send_error_message(update.effective_chat.id)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await self._send_error_message(update.effective_chat.id)

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

    async def handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /start command from users.

        Sends a welcome message to new users starting the bot, explaining
        its capabilities and how to use it.

        Args:
            message (Message): Telegram message object containing the command
                             and user metadata
        """
        if platform == "web":
            welcome_message: str = (
                "👋 Bienvenue ! Je suis votre assistante médicale IA.\n\n"
                "Je peux vous aider à évaluer les situations médicales et vous donner des conseils.    "
                "Vous pouvez m'envoyer des descriptions textuelles de vos symptômes ou de vos préoccupations,"
                "et vous pouvez également partager des images pertinentes pour une meilleure évaluation.\n"
                "Veuillez décrire vos symptômes ou vos préoccupations, ou partager une image "
                "avec le contexte de ce que vous aimeriez que j'examine.\n"
                "Si vous souhaitez recevoir des recommandations de médecins, de pharmacies ou d'hôpitaux,  "
                "veuillez autoriser le partage de la localisation.\n\n"
                "\n👋 Welcome! I'm your AI medical assistant.\n\n"
                "I can help you assess medical situations and provide guidance. "
                "You can send me text descriptions of your symptoms or concerns, "
                "and you can also share relevant images for better assessment.\n\n"
                "Please describe your symptoms or concerns, or share an image along "
                "with context about what you'd like me to examine.\n"
                "If you want to receive recommendations for doctors, pharmacies or hospitals, "
                "please allow location sharing."
            )
        else:
            welcome_message: str = (
                "👋 Bienvenue ! Je suis votre assistante médicale IA.\n\n"
                "Je peux vous aider à évaluer les situations médicales et vous donner des conseils."
                "Vous pouvez m'envoyer des descriptions textuelles de vos symptômes ou de vos préoccupations,"
                "et vous pouvez également partager des images pertinentes pour une meilleure évaluation.\n"
                "Veuillez décrire vos symptômes ou vos préoccupations, ou partager une image "
                "avec le contexte de ce que vous aimeriez que j'examine.\n"
                "Si vous souhaitez recevoir des recommandations de médecins, de pharmacies ou d'hôpitaux,  "
                "veuillez indiquer votre position géographique.\n\n"
                "\n👋 Welcome! I'm your AI medical assistant.\n\n"
                "I can help you assess medical situations and provide guidance. "
                "You can send me text descriptions of your symptoms or concerns, "
                "and you can also share relevant images for better assessment.\n\n"
                "Please describe your symptoms or concerns, or share an image along "
                "with context about what you'd like me to examine.\n"
                "If you want to receive recommendations for doctors, pharmacies or hospitals, "
                "please share your location."
            )
        await self._send_response(update.effective_chat.id, welcome_message)

    async def _send_response(self, chat_id: int, text: str) -> None:
        """Send a response message to a specific chat.

        Args:
            chat_id (int): Telegram chat ID to send the message to
            text (str): Message text to send to the user

        Raises:
            Exception: If there's an error sending the message
        """
        try:
            await self.application.bot.send_message(chat_id, text)
            logger.info(f"Sent response to chat {chat_id}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def _send_error_message(self, chat_id: int) -> None:
        """Send an error message to a specific chat.

        Sends a user-friendly error message when message processing fails.

        Args:
            chat_id (int): Telegram chat ID to send the error message to
        """
        error_text: str = (
            "Sorry, I encountered an error processing your message. "
            "Please try again later."
        )
        await self._send_response(chat_id, error_text)

    async def handle_location(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming location messages from users.

        Processes the user's location and provides a response based on it.

        Args:
            message (Message): Telegram message object containing location data and user metadata
        """
        try:
            print("Update Message: ", update.message)
            print("Update Message Location: ", update.message.location)
            location = update.message.location

            if not location:
                logger.warning("Received location message with no location data")
                return

            logger.info(f"Received location: {location.latitude}, {location.longitude}")

            # Store the location in the global user_locations dictionary
            user_location["latitude"] = location.latitude
            user_location["longitude"] = location.longitude
        except Exception as e:
            logger.error(f"Error handling location : {str(e)}", exc_info=True)
            await self._send_error_message(update.effective_chat.id)
