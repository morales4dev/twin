"""Shared canned refusal constant. No network."""

from context import TWIN_SYSTEM_PROMPT
from refusal import CANNED_REFUSAL, fail_closed_reply, format_lead_ack

EXPECTED = (
    "As the digital twin of Alberto Morales, I am only authorized to discuss "
    "his professional background, experience, and the specific personal "
    "interests listed on his profile."
)


def test_canned_refusal_matches_hard_rejection_sentence():
    assert CANNED_REFUSAL == EXPECTED
    assert CANNED_REFUSAL in TWIN_SYSTEM_PROMPT


def test_lead_ack_contains_extracted_address_not_canned() -> None:
    email = "pepitogrillo@gmail.com"
    reply = format_lead_ack(email)
    assert email in reply
    assert reply != CANNED_REFUSAL


def test_fail_closed_reply_without_email_is_canned() -> None:
    assert fail_closed_reply(None) == CANNED_REFUSAL


def test_fail_closed_reply_with_email_is_lead_ack() -> None:
    email = "lead@example.com"
    assert fail_closed_reply(email) == format_lead_ack(email)
