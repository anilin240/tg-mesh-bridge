from __future__ import annotations

import re

from common.shortcode import generate_code, ALPHABET


def test_alphabet_no_ambiguous():
    # Ensure ambiguous chars are not present
    ambiguous = set("0O1IL")
    assert not (set(ALPHABET) & ambiguous)


def test_length_and_charset():
    for length in [4, 6, 8, 12]:
        code = generate_code(length)
        assert len(code) == length
        assert all(ch in ALPHABET for ch in code)


