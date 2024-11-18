"""Image processing utilities for the Streamlit application.

This module provides utilities for handling and processing images uploaded
through the Streamlit interface.
"""

from typing import Optional, Any
import logging
from PIL import Image
import io
import base64
from io import BytesIO

logger = logging.getLogger(__name__)


def process_uploaded_image(image_file: Any) -> Optional[Image.Image]:
    """Process an uploaded image file from Streamlit.

    Takes an uploaded image file from Streamlit's file uploader and processes
    it for use in the application. Converts the uploaded file to a PIL Image.

    Args:
        image_file: The uploaded image file from Streamlit's file_uploader

    Returns:
        Optional PIL Image if successful, None otherwise

    Raises:
        Exception: If image processing fails
    """
    if image_file is None:
        return None

    try:
        # Read the file into bytes and create PIL Image
        image_bytes = image_file.getvalue()
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary (handles PNG with alpha channel)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        logger.info(f"Successfully processed image: {image_file.name}")
        return image
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise


def image_to_bytes(image: Image.Image) -> bytes:
    """Convert PIL Image to bytes for serialization.

    Args:
        image: PIL Image to convert

    Returns:
        Bytes representation of the image
    """
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()


def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """Convert bytes back to PIL Image.

    Args:
        image_bytes: Bytes representation of the image

    Returns:
        PIL Image object
    """
    return Image.open(io.BytesIO(image_bytes))


def convert_image_to_base64(image: Image.Image) -> Optional[str]:
    """Convert a PIL Image to base64 string.

    Args:
        image: PIL Image object to convert

    Returns:
        Base64 encoded string of the image or None if conversion fails
    """
    try:
        # Convert PIL image to bytes
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Error converting image to base64: {str(e)}")
        return None
