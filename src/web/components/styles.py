"""CSS styles for the Streamlit application."""

from typing import Final

CUSTOM_CSS: Final[str] = """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        .stApp > header {
            background-color: transparent;
        }
        
        [data-testid="stHeader"] {
            display: none;
        }
        
        .stDeployButton {
            display: none;
        }

        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 1000px;
        }

        .stApp {
            margin: 0 auto;
            overflow: hidden;
        }
        
        .stChatMessage {
            padding: 1.5rem;
            border-radius: 20px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .title-area {
            text-align: center;
            padding: 1rem 0;
            margin-top: -2rem;
            margin-bottom: 2rem;
        }

        h1 {
            color: #1565C0;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em;
        }

        .stChatInput {
            font-family: 'Inter', sans-serif !important;
        }
        
        input.stChatInput > div > input {
            font-family: 'Inter', sans-serif !important;
        }

        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
        .gemini-badge {
            background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 1rem;
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .powered-by {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1.5rem;
        }

        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 3rem; 
            background: white;
            z-index: 99;
        }

        .disclaimer-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 0.5rem 1rem;
            z-index: 99;
            border-top: 1px solid #f0f0f0;
        }
    </style>
"""

DISCLAIMER_HTML: Final[str] = """
    <div class='disclaimer-container'>
        <p style='
            font-size: 0.7rem;
            color: #666;
            margin: 0;
            line-height: 1.4;
        '>
            <strong>Medical Disclaimer:</strong> This chatbot is for informational purposes only and is not a substitute for professional medical advice. 
            In case of emergency, please call your local emergency services immediately.
        </p>
    </div>
"""
