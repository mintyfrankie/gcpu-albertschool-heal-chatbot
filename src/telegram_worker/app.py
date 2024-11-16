from typing import Optional
import telebot
from telebot.types import Message
from telegram_worker.config import settings
from telegram_worker.handlers.message_handler import MessageHandler


class LangChainBot:
    """Telegram bot implementation using LangChain."""

    def __init__(self, token: str) -> None:
        """
        Initialize the LangChainBot.

        Args:
            token (str): Telegram bot token obtained from BotFather
        """
        self.bot = telebot.TeleBot(token)
        self.handler = MessageHandler()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up message handlers for the bot."""
        self.bot.message_handler(commands=["start", "help"])(self._handle_start)
        self.bot.message_handler(commands=["reset"])(self._handle_reset)
        self.bot.message_handler(func=lambda message: True)(self._handle_message)

    def _handle_start(self, message: Message) -> None:
        """
        Handle /start and /help commands.

        Args:
            message (Message): Telegram message object
        """
        response = self.handler.handle_start(message)
        self.bot.reply_to(message, response)

    def _handle_reset(self, message: Message) -> None:
        """
        Handle /reset command.

        Args:
            message (Message): Telegram message object
        """
        response = self.handler.handle_reset(message)
        self.bot.reply_to(message, response)

    def _handle_message(self, message: Message) -> None:
        """
        Handle incoming messages.

        Args:
            message (Message): Telegram message object
        """
        if not message.text:
            return

        try:
            response = self.handler.handle_message(message)
            self.bot.reply_to(message, response)
        except Exception as e:
            error_message = "Sorry, I encountered an error. Please try again later."
            self.bot.reply_to(message, error_message)
            print(f"Error processing message: {str(e)}")

    def run(self) -> None:
        """Start the bot."""
        print("Bot is running...")
        self.bot.infinity_polling()


def create_bot(token: Optional[str] = None) -> LangChainBot:
    """
    Create and return a LangChainBot instance.

    Args:
        token (Optional[str]): Telegram bot token. If not provided, will use from settings.

    Returns:
        LangChainBot: Initialized bot instance
    """
    bot_token = token or settings.TELEGRAM_TOKEN
    return LangChainBot(bot_token)


def main() -> None:
    """Main entry point for the bot."""
    bot = create_bot()
    bot.run()


if __name__ == "__main__":
    main()
