"""
Integration with Langfuse
"""

import os

from langfuse.callback import CallbackHandler

# from dotenv import load_dotenv


# load_dotenv()


def get_langfuse_callback_handler():
    return CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
