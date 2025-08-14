from __future__ import annotations

import secrets


ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def generate_code(length: int = 6) -> str:
    if length <= 0:
        raise ValueError("length must be positive")
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


__all__ = ["generate_code", "ALPHABET"]


