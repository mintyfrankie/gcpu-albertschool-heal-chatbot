"""Configuration module for the Telegram bot application.

This module handles loading environment variables and defining application settings
using Pydantic BaseSettings. It manages configuration for both Telegram and Google API
integrations.

Attributes:
    TELEGRAM_TOKEN (str): The Telegram bot API token from environment variables
    GOOGLE_API_KEY (str): The Google API key from environment variables
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import tempfile

load_dotenv("./credentials/.env")

TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
assert (
    TELEGRAM_TOKEN and GOOGLE_API_KEY
), "TELEGRAM_TOKEN and GOOGLE_API_KEY must be set"


class Settings(BaseSettings):
    """Configuration settings for the Telegram bot application.

    This class defines the configuration schema using Pydantic BaseSettings.
    It includes API tokens, model configuration, and generation parameters.
    All settings can be overridden using environment variables.

    Attributes:
        TELEGRAM_TOKEN (str): Telegram bot API token for authentication
        GOOGLE_API_KEY (str): Google API key for Gemini model access
        MODEL_NAME (str): Name of the Gemini model to use for generation
        TEMPERATURE (float): Temperature parameter for controlling response randomness
        MAX_TOKENS (int): Maximum number of tokens for generated responses
        TEMP_IMAGE_DIR (str): Directory for temporary image storage
        IMAGE_RETENTION_PERIOD (int): How long to keep temporary images (in seconds)
    """

    TELEGRAM_TOKEN: str
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-pro"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 500
    TEMP_IMAGE_DIR: str = os.path.join(tempfile.gettempdir(), "telegram_bot_images")
    IMAGE_RETENTION_PERIOD: int = 3600  # 1 hour

    class Config:
        """Pydantic configuration class.

        Defines configuration for environment variable loading and validation.

        Attributes:
            env_file (str): Path to the environment file
            extra (str): How to handle extra fields in the settings
        """

        env_file: str = ".env"
        extra: str = "ignore"


settings: Settings = Settings(
    TELEGRAM_TOKEN=TELEGRAM_TOKEN,
    GOOGLE_API_KEY=GOOGLE_API_KEY,
)
