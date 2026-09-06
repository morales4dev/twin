"""Typed email extract. No network."""

from unittest.mock import patch

from email_capture import capture_typed_email, extract_typed_email


def test_extract_typed_email_present() -> None:
    text = "Please follow up at recruiter@example.com thanks"
    assert extract_typed_email(text) == "recruiter@example.com"


def test_extract_typed_email_absent() -> None:
    assert extract_typed_email("What was Alberto's last role?") is None


def test_extract_does_not_infer_from_other_string() -> None:
    latest = "/exit now"
    other = "sandbox email morales4dev@gmail.com"
    assert extract_typed_email(latest) is None
    assert extract_typed_email(other) == "morales4dev@gmail.com"


@patch("email_capture.record_user_details")
def test_capture_records_first_typed_email(record_user_details) -> None:
    capture_typed_email("I am jane@corp.io and also other@corp.io")
    record_user_details.assert_called_once_with("jane@corp.io")


@patch("email_capture.record_user_details")
def test_capture_records_nothing_when_absent(record_user_details) -> None:
    capture_typed_email("No address here")
    record_user_details.assert_not_called()
