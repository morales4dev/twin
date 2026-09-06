import re

IN_SCOPE = "IN_SCOPE"
OUT_OF_SCOPE = "OUT_OF_SCOPE"
ALLOWED_LABELS = frozenset({IN_SCOPE, OUT_OF_SCOPE})
THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def parse_scope_label(raw: str | None) -> str | None:
    """Parse Turn A content to IN_SCOPE or OUT_OF_SCOPE; else None."""
    if raw is None:
        return None
    cleaned = THINK_BLOCK.sub("", raw)
    for line in cleaned.strip().splitlines():
        token = line.strip()
        if not token:
            continue
        upper = token.upper()
        if upper in ALLOWED_LABELS:
            return upper
        return None
    return None
