"""Telegram bot application entry point.

This module initializes and runs the Telegram bot, setting up message handlers
and managing bot interactions. It provides the main interface between Telegram
users and the chat service.

Attributes:
    logger (logging.Logger): Module level logger instance for application-wide logging
"""

import logging
from typing import Optional
import telebot
from telebot.types import Message
from telegram_worker.config import settings
from telegram_worker.handlers.message_handler import MessageHandler

# Configure logging
logger: logging.Logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot application class.

    This class initializes the Telegram bot, sets up message handlers,
    and manages the bot's lifecycle. It provides the core functionality
    for receiving and responding to Telegram messages.

    Attributes:
        bot (telebot.TeleBot): Initialized Telegram bot instance for handling messages
        message_handler (MessageHandler): Handler instance for processing different message types
    """

    def __init__(self, token: str) -> None:
        """Initialize the Telegram bot with configured settings.

        Args:
            token (str): Telegram bot API token for authentication
        """
        try:
            logger.info("Initializing Telegram bot...")
            self.bot: telebot.TeleBot = telebot.TeleBot(token)
            self.message_handler: MessageHandler = MessageHandler(self.bot)
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

        @self.bot.message_handler(commands=["start"])
        def handle_start(message: Message) -> None:
            """Handle the /start command from users.

            Args:
                message (Message): Telegram message object containing the start command
                                 and metadata about the sender
            """
            self.message_handler.handle_start(message)

        @self.bot.message_handler(content_types=["text"])
        def handle_text(message: Message) -> None:
            """Handle incoming text messages from users.

            Args:
                message (Message): Telegram message object containing the user's text
                                 and metadata about the sender
            """
            self.message_handler.handle_text(message)

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
            self.bot.polling(none_stop=True, interval=0, timeout=20, skip_pending=True)
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
    bot.run()


if __name__ == "__main__":
    main()
