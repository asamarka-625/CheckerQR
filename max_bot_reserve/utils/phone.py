from typing import Optional


def normalize_phone(raw: str) -> Optional[str]:
    """11 цифр, ведущая 8 -> 7. None, если формат неверный."""
    digits = "".join(ch for ch in raw if ch.isdigit())

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    if len(digits) != 11 or not digits.startswith("7"):
        return None

    return digits