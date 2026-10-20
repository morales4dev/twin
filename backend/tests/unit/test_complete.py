"""Turn B one-shot complete I/O. No network."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

from complete import complete
from context import TWIN_SYSTEM_PROMPT
from refusal import CANNED_REFUSAL
from tools import tools as twin_tools

CURRENT = "What was Alberto's last role?"
REPLY = "Alberto's last role is described in his profile."


def _completion(content: str | None, finish_reason: str = "stop") -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=None)
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice])


def _prior_turns(count: int) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for i in range(count):
        history.append({"role": "user", "content": f"user-{i}"})
        history.append({"role": "assistant", "content": f"assistant-{i}"})
    return history


def _first_messages(llm_completion: Mock) -> list:
    return llm_completion.call_args_list[0].args[0]


def _assert_turn_b_payload(messages: list, history: list[dict[str, str]], current: str) -> None:
    assert messages[0] == {"role": "system", "content": TWIN_SYSTEM_PROMPT}
    assert messages[-1] == {"role": "user", "content": current}
    sent = messages[1:-1]
    assert sent == history
    assert all(item["role"] in {"user", "assistant"} for item in sent)


def test_complete_one_shot_uses_tools() -> None:
    llm_completion = Mock(return_value=_completion(REPLY))
    reply = complete(CURRENT, [], llm_completion)
    assert reply == REPLY
    assert llm_completion.call_count == 1
    kwargs = llm_completion.call_args.kwargs
    assert kwargs["tools"] == twin_tools


def test_complete_sends_all_history_at_or_under_cap() -> None:
    history = _prior_turns(8)
    llm_completion = Mock(return_value=_completion(REPLY))
    complete(CURRENT, history, llm_completion)
    _assert_turn_b_payload(_first_messages(llm_completion), history, CURRENT)


def test_complete_drops_oldest_turns_over_cap() -> None:
    history = _prior_turns(9)
    llm_completion = Mock(return_value=_completion(REPLY))
    complete(CURRENT, history, llm_completion)
    _assert_turn_b_payload(_first_messages(llm_completion), history[2:], CURRENT)
    assert history[0] not in _first_messages(llm_completion)
    assert history[1] not in _first_messages(llm_completion)


def test_complete_does_not_mutate_history() -> None:
    history = _prior_turns(9)
    original = list(history)
    llm_completion = Mock(return_value=_completion(REPLY))
    complete(CURRENT, history, llm_completion)
    assert history == original
    assert len(history) == 18


def test_complete_refusals_follow_the_window() -> None:
    recent = _prior_turns(8)
    recent[-1] = {"role": "assistant", "content": CANNED_REFUSAL}
    llm_completion = Mock(return_value=_completion(REPLY))
    complete(CURRENT, recent, llm_completion)
    assert any(item["content"] == CANNED_REFUSAL for item in _first_messages(llm_completion))

    old = _prior_turns(9)
    old[1] = {"role": "assistant", "content": CANNED_REFUSAL}
    llm_completion = Mock(return_value=_completion(REPLY))
    complete(CURRENT, old, llm_completion)
    assert all(item.get("content") != CANNED_REFUSAL for item in _first_messages(llm_completion))


def test_complete_tool_loop_keeps_same_window() -> None:
    history = _prior_turns(9)
    windowed = history[2:]
    tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="record_unknown_question", arguments='{"question":"x"}'),
    )
    first = _completion(None, finish_reason="tool_calls")
    first.choices[0].message.tool_calls = [tool_call]
    captured: list[list] = []
    responses = iter([first, _completion(REPLY)])

    def llm_completion(messages: list, *, tools=None):
        captured.append(list(messages))
        return next(responses)

    tool_result = {"role": "tool", "content": '"OK"', "tool_call_id": "call_1"}

    with patch("complete.handle_tool_calls", return_value=[tool_result]):
        reply = complete(CURRENT, history, llm_completion)

    assert reply == REPLY
    assert len(captured) == 2
    _assert_turn_b_payload(captured[0], windowed, CURRENT)
    assert captured[1][1 : 1 + len(windowed)] == windowed
    assert history[0] not in captured[0]
    assert history[0] not in captured[1]
    assert history[1] not in captured[0]
    assert history[1] not in captured[1]
