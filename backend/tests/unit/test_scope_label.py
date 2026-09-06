"""Turn A label parse. No network."""

from scope_label import parse_scope_label

MIXED_TURN_LABEL = "OUT_OF_SCOPE"


def test_parse_in_scope() -> None:
    assert parse_scope_label("IN_SCOPE") == "IN_SCOPE"


def test_parse_out_of_scope() -> None:
    assert parse_scope_label("out_of_scope\n") == "OUT_OF_SCOPE"


def test_parse_mixed_turn_fixture_is_out_of_scope() -> None:
    assert parse_scope_label(MIXED_TURN_LABEL) == "OUT_OF_SCOPE"


def test_parse_empty_is_unparseable() -> None:
    assert parse_scope_label("") is None
    assert parse_scope_label(None) is None
    assert parse_scope_label("   \n") is None


def test_parse_essay_is_unparseable() -> None:
    assert parse_scope_label("Sure, IN_SCOPE because this is about Alberto.") is None


def test_parse_other_token_is_unparseable() -> None:
    assert parse_scope_label("LEAD") is None
    assert parse_scope_label('{"label": "IN_SCOPE"}') is None


def test_parse_think_then_in_scope() -> None:
    raw = (
        "<think>\n"
        "The user is asking about Alberto's experience with Python.\n"
        "This is clearly IN_SCOPE.\n"
        "</think>\n"
        "\n"
        "IN_SCOPE"
    )
    assert parse_scope_label(raw) == "IN_SCOPE"


def test_parse_think_then_out_of_scope() -> None:
    raw = (
        "<think>\n"
        "This is a skill trap, so OUT_OF_SCOPE.\n"
        "</think>\n"
        "OUT_OF_SCOPE"
    )
    assert parse_scope_label(raw) == "OUT_OF_SCOPE"


def test_parse_label_only_inside_think_is_unparseable() -> None:
    raw = "<think>\nThis is clearly IN_SCOPE.\n</think>\n"
    assert parse_scope_label(raw) is None
