"""Telegram bot application entry point.

This module initializes and runs the Telegram bot, setting up message handlers
and managing bot interactions. It provides the main interface between Telegram
users and the chat service.

Attributes:
    logger (logging.Logger): Module level logger instance for application-wide logging
"""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from backend import platform
from telegram_worker.config import settings
from telegram_worker.handlers.message_handler import (
    MessageHandler as TelegramMessageHandler,
)

platform = "telegram"

# Configure logging
logger: logging.Logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot application class.

    This class initializes the Telegram bot, sets up message handlers,
    and manages the bot's lifecycle. It provides the core functionality
    for receiving and responding to Telegram messages.

    Attributes:
        application (Application): Initialized Telegram bot instance for handling messages
        message_handler (MessageHandler): Handler instance for processing different message types
    """

    def __init__(self, token: str) -> None:
        """Initialize the Telegram bot with configured settings.

        Args:
            token (str): Telegram bot API token for authentication
        """
        try:
            logger.info("Initializing Telegram bot...")
            self.application = ApplicationBuilder().token(token).build()
            self.message_handler = TelegramMessageHandler(self.application)
            self._setup_handlers()
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}", exc_info=True)
            raise

    def _setup_handlers(self) -> None:
        """Set up message handlers for the bot.

        Configures handlers for different types of messages and commands
        that the bot can receive. This includes the start command and
        general text messages.
        """
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text)
        )
        self.application.add_handler(MessageHandler(filters.PHOTO, self._handle_photo))
        self.application.add_handler(
            MessageHandler(filters.LOCATION, self._handle_location)
        )

    async def _handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /start command from users.

        Args:
            message (Message): Telegram message object containing the start command
                             and metadata about the sender
        """
        await self.message_handler.handle_start(update, context)

    async def _handle_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming photo messages from users.

        Args:
            message (Message): Telegram message object containing the photo
                             and metadata about the sender
        """
        await self.message_handler.handle_photo(update, context)

    async def _handle_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming text messages from users.

        Args:
            message (Message): Telegram message object containing the user's text
                             and metadata about the sender
        """
        await self.message_handler.handle_text(update, context)

    async def _handle_location(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming location messages from users.

        Args:
            message (Message): Telegram message object containing the user's location
                             and metadata about the sender
        """
        await self.message_handler.handle_location(update, context)

    def run(self) -> None:
        """Start the bot and begin polling for messages.

        Starts the bot in polling mode and handles any exceptions that occur
        during operation. This method runs indefinitely until interrupted.

        Raises:
            Exception: If an error occurs while running the bot
        """
        try:
            logger.info("Starting Telegram bot polling...")
            # Add skip_pending=True to skip messages that arrived while the bot was offline
            self.application.run_polling(
                none_stop=True, interval=0, timeout=20, skip_pending=True
            )
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}", exc_info=True)
            raise e


def create_bot(token: Optional[str] = None) -> TelegramBot:
    """
    Create and return a TelegramBot instance.

    Args:
        token (Optional[str]): Telegram bot token. If not provided, will use from settings.

    Returns:
        LangChainBot: Initialized bot instance
    """
    bot_token = token or settings.TELEGRAM_TOKEN
    return TelegramBot(bot_token)


def main() -> None:
    """Main entry point for the bot."""
    bot = create_bot()
    bot.application.run_polling()


if __name__ == "__main__":
    main()
