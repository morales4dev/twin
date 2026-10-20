from collections.abc import Callable

from context import TWIN_SYSTEM_PROMPT
from tools import handle_tool_calls, tools

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def complete(message: str, history: list, llm_completion: Callable) -> str:
    messages = system + history + [{"role": "user", "content": message}]
    response = llm_completion(messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(assistant_message)
        messages.extend(results)
        response = llm_completion(messages, tools=tools)
    return response.choices[0].message.content
