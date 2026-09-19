"""Turn B one-shot complete I/O. No network."""

from types import SimpleNamespace
from unittest.mock import Mock

from classifier import MODEL_NAME
from complete import complete
from tools import tools as twin_tools


def _completion(content: str | None, finish_reason: str = "stop") -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=None)
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice])


def _fake_client(return_value: object) -> tuple[SimpleNamespace, Mock]:
    create = Mock(return_value=return_value)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    return client, create


def test_complete_one_shot_uses_tools_and_model() -> None:
    client, create = _fake_client(_completion("Alberto's last role is described in his profile."))
    reply = complete("What was Alberto's last role?", [], client)
    assert reply == "Alberto's last role is described in his profile."
    assert create.call_count == 1
    kwargs = create.call_args.kwargs
    assert kwargs["model"] == MODEL_NAME
    assert kwargs["tools"] == twin_tools
