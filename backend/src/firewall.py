import re

DENY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore\s+previous", re.IGNORECASE),
    re.compile(r"important\s+system", re.IGNORECASE),
    re.compile(r"\bsystem:", re.IGNORECASE),
    re.compile(r"/exit", re.IGNORECASE),
    re.compile(r"/resume", re.IGNORECASE),
    re.compile(r"show\s+your\s+prompt", re.IGNORECASE),
    re.compile(r"show\s+your\s+memory", re.IGNORECASE),
    re.compile(r"for\s+debugging", re.IGNORECASE),
)


def matches_firewall(message: str) -> bool:
    """Return True if the latest user string matches a deny-list family."""
    return any(pattern.search(message) for pattern in DENY_PATTERNS)
