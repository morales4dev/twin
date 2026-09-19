from openai import OpenAI
from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from context import get_absolute_path
from classifier import MODEL_NAME, classify
from complete import complete
from email_capture import capture_typed_email
from firewall import matches_firewall
from refusal import CANNED_REFUSAL, fail_closed_reply

print(get_absolute_path())
load_dotenv(override=True)

openai = OpenAI()


def chat(message: str, history: list, client=None) -> str:
    client = client or openai
    email = capture_typed_email(message)
    if matches_firewall(message):
        return CANNED_REFUSAL
    result = classify(message, client)
    if not result.allowed_for_turn_b:
        return fail_closed_reply(email)
    return complete(message, history, client)


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
