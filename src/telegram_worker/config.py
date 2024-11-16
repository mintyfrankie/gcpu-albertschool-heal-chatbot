import os
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
assert (
    TELEGRAM_TOKEN and GOOGLE_API_KEY
), "TELEGRAM_TOKEN and GOOGLE_API_KEY must be set"


class Settings(BaseSettings):
    """Configuration settings for the Telegram bot application."""

    TELEGRAM_TOKEN: str
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-pro"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 500

    class Config:
        """Pydantic configuration class."""

        env_file = ".env"
        extra = "ignore"


settings = Settings(
    TELEGRAM_TOKEN=TELEGRAM_TOKEN,
    GOOGLE_API_KEY=GOOGLE_API_KEY,
)
