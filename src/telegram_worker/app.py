import os
import telebot
from telebot.types import Message


class YesNoBot:
    """A simple yes/no Telegram bot implementation."""

    def __init__(self, token: str) -> None:
        """
        Initialize the YesNoBot.

        Args:
            token (str): Telegram bot token obtained from BotFather
        """
        self.bot = telebot.TeleBot(token)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up message handlers for the bot."""
        self.bot.message_handler(commands=["start", "help"])(self._handle_start)
        self.bot.message_handler(func=lambda message: True)(self._handle_message)

    def _handle_start(self, message: Message) -> None:
        """
        Handle /start and /help commands.

        Args:
            message (Message): Telegram message object
        """
        welcome_text = (
            "👋 Hi! I'm a Yes/No bot!\n\n"
            "Ask me any question that can be answered with Yes or No.\n"
            "I'll do my best to give you a clear answer!"
        )
        self.bot.reply_to(message, welcome_text)

    def _handle_message(self, message: Message) -> None:
        """
        Handle incoming messages and respond with yes or no.

        Args:
            message (Message): Telegram message object
        """
        # Simple logic to determine yes/no response
        text = message.text.lower() if message.text else ""

        # Skip empty messages
        if not text:
            return

        # Simple logic to generate yes/no response
        if "?" not in text:
            self.bot.reply_to(
                message, "Please ask a question! Don't forget the question mark (?)"
            )
            return

        # Very simple alternating response based on message length
        response = "Yes! 👍" if len(text) % 2 == 0 else "No! 👎"
        self.bot.reply_to(message, response)

    def run(self) -> None:
        """Start the bot."""
        print("Bot is running...")
        self.bot.infinity_polling()


def create_bot(token: str | None = None) -> YesNoBot:
    """
    Create and return a YesNoBot instance.

    Args:
        token (Optional[str]): Telegram bot token. If not provided, will try to get from environment variable.

    Returns:
        YesNoBot: Initialized bot instance

    Raises:
        ValueError: If no token is provided and TELEGRAM_TOKEN environment variable is not set
    """
    bot_token = token or os.getenv("TELEGRAM_TOKEN")
    if not bot_token:
        raise ValueError(
            "Telegram token not provided. Set TELEGRAM_TOKEN environment variable or pass token directly."
        )

    return YesNoBot(bot_token)


def main() -> None:
    """Main entry point for the bot."""
    bot = create_bot()
    bot.run()


if __name__ == "__main__":
    main()
