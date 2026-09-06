import re

from tools import record_user_details

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def extract_typed_email(message: str) -> str | None:
    """Return the first typed email in the latest user string, or None."""
    match = EMAIL_RE.search(message)
    if match is None:
        return None
    return match.group(0)


def capture_typed_email(message: str) -> str | None:
    """Record the first typed email from the latest user string, if any."""
    email = extract_typed_email(message)
    if email is None:
        return None
    record_user_details(email)
    return email
