from classifier import MODEL_NAME
from context import TWIN_SYSTEM_PROMPT
from tools import handle_tool_calls, tools

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def complete(message: str, history: list, client) -> str:
    messages = system + history + [{"role": "user", "content": message}]
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(assistant_message)
        messages.extend(results)
        response = client.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    return response.choices[0].message.content
