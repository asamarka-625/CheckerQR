import re
import secrets

# Алфавит без неоднозначных символов (нет 0, O, 1, I, L)
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_RE = re.compile(r"^[ABCDEFGHJKMNPQRSTUVWXYZ2-9]{4}-[ABCDEFGHJKMNPQRSTUVWXYZ2-9]{4}$")


def generate_code(length: int = 8) -> str:
    raw = "".join(secrets.choice(ALPHABET) for _ in range(length))
    return f"{raw[:4]}-{raw[4:]}"  # Формат: XXXX-XXXX


def is_valid_code(value: str) -> bool:
    return bool(CODE_RE.fullmatch(value.strip().upper()))