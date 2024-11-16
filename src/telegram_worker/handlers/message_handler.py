from telebot.types import Message
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from backend.services import process_user_input
import logging
from typing import Any, Union

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handler for processing telegram messages using LangGraph-based triage system."""

    def __init__(self) -> None:
        """Initialize the message handler."""
        self.config: RunnableConfig = {"configurable": {}}

    def handle_start(self, message: Message) -> str:
        """
        Handle the /start command.

        Args:
            message (Message): Telegram message object.

        Returns:
            str: Welcome message.
        """
        return (
            "👋 Hi! I'm a mental health triage bot powered by LangGraph. "
            "I can help assess the severity of your situation and provide appropriate guidance. "
            "Feel free to share what's on your mind."
        )

    def handle_reset(self, message: Message) -> str:
        """
        Handle the /reset command.

        Args:
            message (Message): Telegram message object.

        Returns:
            str: Reset confirmation message.
        """
        return "Conversation has been reset. You can start fresh."

    def _extract_content(self, message: Union[AIMessage, tuple, str, Any]) -> str:
        """
        Extract content from various message formats.

        Args:
            message: Message object that could be in various formats.

        Returns:
            str: Extracted content from the message.

        Raises:
            ValueError: If content cannot be extracted or is None.
        """
        if isinstance(message, AIMessage):
            return str(message.content)
        elif isinstance(message, tuple) and len(message) == 2:
            _, content = message
            return str(content)
        elif isinstance(message, str):
            return message
        else:
            content = getattr(message, "content", None)
            if content is None:
                raise ValueError("Could not extract content from message")
            return str(content)

    def handle_message(self, message: Message) -> str:
        """
        Process incoming messages using LangGraph triage system.

        Args:
            message (Message): Telegram message object.

        Returns:
            str: Response message.
        """
        if not message.text:
            return "I can only process text messages. Please send me a text message."

        try:
            result = process_user_input(
                user_input=message.text, thread_id=str(message.chat.id)
            )

            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if messages:
                    last_message = messages[-1]
                    try:
                        return self._extract_content(last_message)
                    except ValueError as e:
                        logger.warning(f"Failed to extract content: {e}")

            return (
                "I'm sorry, I couldn't process your message properly. Please try again."
            )

        except Exception as e:
            logger.error(f"Error in handle_message: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error processing your message: {str(e)}"
