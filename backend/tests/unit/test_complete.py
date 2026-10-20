"""Turn B one-shot complete I/O. No network."""

from types import SimpleNamespace
from unittest.mock import Mock

from complete import complete
from tools import tools as twin_tools


def _completion(content: str | None, finish_reason: str = "stop") -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=None)
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice])


def test_complete_one_shot_uses_tools() -> None:
    llm_completion = Mock(return_value=_completion("Alberto's last role is described in his profile."))
    reply = complete("What was Alberto's last role?", [], llm_completion)
    assert reply == "Alberto's last role is described in his profile."
    assert llm_completion.call_count == 1
    kwargs = llm_completion.call_args.kwargs
    assert kwargs["tools"] == twin_tools
