from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls, record_user_details
from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from context import get_absolute_path
from classifier import build_classifier_messages
from email_capture import extract_typed_email
from firewall import matches_firewall
from refusal import CANNED_REFUSAL, format_lead_ack
from scope_label import IN_SCOPE, parse_scope_label

print(get_absolute_path())
load_dotenv(override=True)

# MODEL_NAME = "gpt-5.4-mini"
MODEL_NAME = "MiniMax-M2.5"

openai = OpenAI()

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def chat(message, history):
    email = extract_typed_email(message)
    if email is not None:
        record_user_details(email)

    if matches_firewall(message):
        return CANNED_REFUSAL

    try:
        classifier_response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=build_classifier_messages(message),
        )
        raw_label = classifier_response.choices[0].message.content
    except Exception:
        if email is not None:
            return format_lead_ack(email)
        return CANNED_REFUSAL

    if parse_scope_label(raw_label) != IN_SCOPE:
        if email is not None:
            return format_lead_ack(email)
        return CANNED_REFUSAL

    messages = system + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(assistant_message)
        messages.extend(results)
        response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    return response.choices[0].message.content


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
