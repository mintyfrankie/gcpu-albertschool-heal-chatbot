import gradio as gr
import random


def reply(message, history):
    return random.choice(["Yes", "No", "Maybe"])


demo = gr.ChatInterface(reply, type="messages")

if __name__ == "__main__":
    demo.launch()
