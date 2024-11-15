import os
import streamlit as st
from PIL import Image
from google.cloud import vision
import google.generativeai as genai


genai.configure(api_key=GEMINI_API_KEY)

# Configure Google Cloud Vision client for label detection
SERVICE_ACCOUNT_FILE = "src/credential_cloud.json"  # Replace with your correct path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE
vision_client = vision.ImageAnnotatorClient()

def get_top_labels_with_vision(image_path):
    """Get the top 3 high-confidence labels using Google Cloud Vision."""
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = vision_client.label_detection(image=image)
    labels = response.label_annotations

    # Sort labels by confidence and get the top 3
    top_labels = sorted(labels, key=lambda x: x.score, reverse=True)[:3]
    return [label.description for label in top_labels]

def generate_detailed_description_with_gemini(image, context_text):
    """Generate a detailed description using Gemini with text and image input."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Generate content using text and image as inputs
        response = model.generate_content([f"Describe this scene: {context_text}", image])
        return response.text  # Adjust if response structure differs
    except Exception as e:
        return f"Error generating description with Gemini: {e}"

# Streamlit app integration
st.title("Enhanced Image Description with Gemini LLM and Vision API")

uploaded_file = st.file_uploader("Upload an image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
if uploaded_file:
    # Save and display the uploaded image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Save the uploaded file locally
    image_path = uploaded_file.name
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Get top labels using Google Cloud Vision
    with st.spinner("Analyzing image with Google Cloud Vision..."):
        top_labels = get_top_labels_with_vision(image_path)
        st.write("Top Labels Detected:")
        st.write(", ".join(top_labels))

    # Generate detailed description using Gemini
    with st.spinner("Generating detailed description with Gemini..."):
        detailed_description = generate_detailed_description_with_gemini(image, ", ".join(top_labels))

    st.write("Generated Detailed Description:")
    st.write(detailed_description)
