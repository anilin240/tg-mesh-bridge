from __future__ import annotations

from bridge.consumer import _extract_code_and_message


def test_parse_exact_prefix():
    code, text = _extract_code_and_message("@tg:ABCD hello")
    assert code == "ABCD"
    assert text == "hello"


def test_parse_embedded_prefix():
    code, text = _extract_code_and_message("Some text @tg:ZZZZ  hi there")
    assert code == "ZZZZ"
    assert text == "hi there"


def test_parse_no_prefix():
    code, text = _extract_code_and_message("no code here")
    assert code is None and text is None


