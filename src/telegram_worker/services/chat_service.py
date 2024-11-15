from typing import Any
import google.generativeai as genai
from ..config import settings


class ChatService:
    """Service class for handling chat interactions with Gemini."""

    def __init__(self) -> None:
        """Initialize the chat service with Gemini components."""
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.MODEL_NAME,
            generation_config={
                "temperature": settings.TEMPERATURE,
                "max_output_tokens": settings.MAX_TOKENS,
            },
        )
        # Store chat sessions for each user
        self.conversations: dict[int, Any] = {}

    def get_response(self, user_id: int, message: str) -> str:
        """
        Get a response from Gemini model.

        Args:
            user_id (int): Telegram user ID for maintaining conversation history
            message (str): User's input message

        Returns:
            str: AI response
        """
        # Create new chat for user if doesn't exist
        if user_id not in self.conversations:
            chat = self.model.start_chat(history=[])
            # Set initial context
            chat.send_message(
                "You are a helpful assistant. Be concise and clear in your responses."
            )
            self.conversations[user_id] = chat

        # Get response from the model
        response = self.conversations[user_id].send_message(message)

        return response.text

    def reset_conversation(self, user_id: int) -> None:
        """
        Reset the conversation history for a user.

        Args:
            user_id (int): Telegram user ID
        """
        chat = self.model.start_chat(history=[])
        chat.send_message(
            "You are a helpful assistant. Be concise and clear in your responses."
        )
        self.conversations[user_id] = chat
