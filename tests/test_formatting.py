"""Tests for number formatting."""

from mybot.utils.formatting import number_format


def test_basic():
    assert number_format(1234567) == "1 234 567"


def test_small():
    assert number_format(123) == "123"


def test_thousands():
    assert number_format(1000) == "1 000"


def test_negative():
    assert number_format(-1234) == "-1 234"


def test_zero():
    assert number_format(0) == "0"


def test_empty_string():
    assert number_format("") == ""


def test_empty_null_to_zero():
    assert number_format("", null_to_zero=True) == "0"


def test_none():
    assert number_format(None) == ""


def test_none_null_to_zero():
    assert number_format(None, null_to_zero=True) == "0"
