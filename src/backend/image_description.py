"""Image analysis and description generation module.

This module provides functionality to analyze images using Google Cloud Vision
and generate detailed descriptions using Google's Gemini model. It combines
label detection and generative AI to provide comprehensive image understanding.
"""

from typing import List, Optional
import base64
import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from google.cloud import vision
from google.cloud.vision_v1.types import Image
from PIL import Image as PILImage

load_dotenv()
# Configure Gemini API
GEMINI_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# Configure Google Cloud Vision client for label detection
vision_client = vision.ImageAnnotatorClient()


def get_top_labels_with_vision(image_data: bytes) -> List[str]:
    """Get the top 3 high-confidence labels using Google Cloud Vision.

    Args:
        image_data: Raw image bytes to analyze

    Returns:
        List of top 3 label descriptions sorted by confidence

    Raises:
        google.api_core.exceptions.GoogleAPIError: If Vision API request fails
    """
    image = vision.Image(content=image_data)

    response = vision_client.label_detection(image=image)
    labels = response.label_annotations

    # Sort labels by confidence and get the top 3
    top_labels = sorted(labels, key=lambda x: x.score, reverse=True)[:3]
    return [label.description for label in top_labels]


def generate_detailed_description_with_gemini(
    image: PILImage.Image, image_data: bytes
) -> str:
    """Generate a detailed description using Gemini with text and image input.

    Combines Vision API label detection with Gemini's generative capabilities
    to create a comprehensive description of the image.

    Args:
        image: PIL Image object for Gemini processing
        image_data: Raw image bytes for Vision API processing

    Returns:
        Detailed description of the image

    Raises:
        Exception: If description generation fails
    """
    top_labels = get_top_labels_with_vision(image_data)
    context_text = f"The image may include {', '.join(top_labels)}."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Generate content using text and image as inputs
        response = model.generate_content(
            [f"Describe this scene: {context_text}", image]
        )
        return response.text  # Adjust if response structure differs
    except Exception as e:
        return f"Error generating description with Gemini: {e}"
