from telebot.types import Message
from telegram_worker.services.chat_service import ChatService


class MessageHandler:
    """Handler class for processing Telegram messages."""

    def __init__(self) -> None:
        """Initialize the message handler with required services."""
        self.chat_service = ChatService()

    def handle_start(self, message: Message) -> str:
        """
        Handle the /start command.

        Args:
            message (Message): Telegram message object

        Returns:
            str: Welcome message
        """
        return (
            "👋 Welcome! I'm your AI assistant powered by Gemini.\n\n"
            "You can:\n"
            "- Ask me any question\n"
            "- Use /reset to start a new conversation\n"
            "- Use /help to see this message again"
        )

    def handle_reset(self, message: Message) -> str:
        """
        Handle the /reset command.

        Args:
            message (Message): Telegram message object

        Returns:
            str: Reset confirmation message
        """
        if message.from_user and message.from_user.id:
            self.chat_service.reset_conversation(message.from_user.id)
            return "Conversation has been reset. Let's start fresh!"
        return "Error: Could not identify user."

    def handle_message(self, message: Message) -> str:
        """
        Handle regular messages.

        Args:
            message (Message): Telegram message object

        Returns:
            str: AI response
        """
        if not message.from_user or not message.from_user.id or not message.text:
            return "Error: Invalid message format."

        return self.chat_service.get_response(
            user_id=message.from_user.id, message=message.text
        )
