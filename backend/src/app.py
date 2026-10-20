from collections.abc import Callable

from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from context import get_absolute_path
from classifier import classify
from complete import complete
from email_capture import capture_typed_email
from input_guardrail import matches_input_guardrail
from refusal import CANNED_REFUSAL, fail_closed_reply
import llm

print(get_absolute_path())
load_dotenv(override=True)


def chat(message: str, history: list, llm_completion: Callable | None = None) -> str:
    llm_completion = llm_completion or llm.completion
    email = capture_typed_email(message)
    if matches_input_guardrail(message):
        return CANNED_REFUSAL
    result = classify(message, llm_completion)
    if not result.allowed_for_turn_b:
        return fail_closed_reply(email)
    return complete(message, history, llm_completion)


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
