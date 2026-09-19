CANNED_REFUSAL = (
    "As the digital twin of Alberto Morales, I am only authorized to discuss "
    "his professional background, experience, and the specific personal "
    "interests listed on his profile."
)

LEAD_ACK = (
    "Thanks — I have recorded {email} so Alberto can follow up. I can still "
    "only discuss his professional background, experience, and the interests "
    "on his profile. What would you like to know about that?"
)


def format_lead_ack(email: str) -> str:
    return LEAD_ACK.format(email=email)


def fail_closed_reply(email: str | None) -> str:
    if email is not None:
        return format_lead_ack(email)
    return CANNED_REFUSAL
