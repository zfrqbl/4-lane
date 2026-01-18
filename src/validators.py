# src/validators.py
import re
from .config import CONFIG

def validate_input_specification(specification: str) -> tuple[bool, str]:
    """
    Validates the input specification.
    Returns (is_valid, error_message).
    """
    if not specification or not specification.strip():
        return False, "Specification cannot be empty."

    if len(specification) > CONFIG.system.input_char_limit:
        return False, f"Specification exceeds character limit of {CONFIG.system.input_char_limit}."

    # Add more checks if needed (e.g., for potentially harmful content)
    # For now, basic check is sufficient per instructions.

    return True, ""