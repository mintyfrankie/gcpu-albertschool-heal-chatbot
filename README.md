# gcpu-albert-hackathon

WIP project for the GCPU Hackathon deliverable.

## Setup

I will recommend `rye` for the package manager and virtual environment management.

Execute the following command to install the dependencies:

```bash
rye sync
```

Then you can run the app with:

```bash
rye run gradio src/app.py
```

For the time being the backend is handled by ollama, so you need to have it installed and running (also check if your computer is capable of running local LLM models).

## How to Run - Streamlit

1. Set up environment variables in `src/chatbot/.env`.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the app using `streamlit run src/chatbot/app.py`.
