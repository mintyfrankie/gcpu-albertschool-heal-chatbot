import gradio as gr
import ollama

MODEL_NAME = "llama3.1:8b"


def generate_request(message: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": message}]


def reply(message: str, history: list[list[str]]) -> str:
    messages = []
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return response["message"]["content"]


demo = gr.ChatInterface(reply, type="messages")

if __name__ == "__main__":
    demo.launch()
