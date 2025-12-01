"""
Lightweight guardrail stubs.

Currently allows all input; extend with filters/policies as needed.
"""

from typing import Tuple

from config import settings

def check_input(user_input: str) -> Tuple[bool, str]:
    """
    Returns (allowed, message). If not allowed, message explains why.
    Uses settings.app.guardrail_policy; default is allow_all.
    """
    policy = getattr(settings.app, "guardrail_policy", "allow_all")

    if policy == "allow_all":
        return True, ""

    # Placeholder for future policies; currently fallback to allow.
    return True, ""
