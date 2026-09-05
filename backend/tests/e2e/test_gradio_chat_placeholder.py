"""v1 placeholder. Future Playwright suite drives Gradio ChatInterface. Do not call MiniMax."""

import pytest

pytestmark = pytest.mark.skip(
    reason="v1 Playwright slot only; target is Gradio ChatInterface, not a live MiniMax suite"
)


def test_gradio_chat_interface_placeholder():
    raise AssertionError("unreachable: skipped e2e placeholder")
