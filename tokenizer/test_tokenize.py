from pathlib import Path
import subprocess
import sys

import pytest

from main import tokenize


def test_all_separators():
    assert tokenize("(){},;") == [
        ("SEP", "(", 1, 1),
        ("SEP", ")", 1, 2),
        ("SEP", "{", 1, 3),
        ("SEP", "}", 1, 4),
        ("SEP", ",", 1, 5),
        ("SEP", ";", 1, 6),
    ]


def test_positions_after_whitespace():
    assert tokenize(" (\n\n\t )") == [("SEP", "(", 1, 2), ("SEP", ")", 3, 3)]


def test_whitespace_produces_no_tokens():
    assert tokenize(" \t\n") == []


@pytest.mark.parametrize("word", ["if", "else", "while", "return", "for", "def"])
def test_keywords(word):
    assert tokenize(f" {word}") == [("KEYWORD", word, 1, 2)]


def test_identifiers():
    assert tokenize("if_count _x2 for2") == [
        ("IDENT", "if_count", 1, 1),
        ("IDENT", "_x2", 1, 10),
        ("IDENT", "for2", 1, 14),
    ]


def test_integer_literals():
    assert tokenize("0 007 -42") == [
        ("INT", "0", 1, 1),
        ("INT", "007", 1, 3),
        ("OP", "-", 1, 7),
        ("INT", "42", 1, 8),
    ]


def test_float_literals():
    assert tokenize("0.5\n  12.50;") == [
        ("FLOAT", "0.5", 1, 1),
        ("FLOAT", "12.50", 2, 3),
        ("SEP", ";", 2, 8),
    ]


@pytest.mark.parametrize(
    ("source", "value"),
    [('""', ""), ('"привет мир"', "привет мир"), ('"a#b ( )"', "a#b ( )")],
)
def test_string_literals(source, value):
    assert tokenize(f"  {source};") == [
        ("STRING", value, 1, 3),
        ("SEP", ";", 1, len(source) + 3),
    ]


def test_all_operators():
    assert tokenize("+-*/=<> ==<=>=") == [
        ("OP", "+", 1, 1),
        ("OP", "-", 1, 2),
        ("OP", "*", 1, 3),
        ("OP", "/", 1, 4),
        ("OP", "=", 1, 5),
        ("OP", "<", 1, 6),
        ("OP", ">", 1, 7),
        ("OP", "==", 1, 9),
        ("OP", "<=", 1, 11),
        ("OP", ">=", 1, 13),
    ]


def test_comments_are_skipped_to_end_of_line():
    assert tokenize('if# @ "\n\treturn # 3.14') == [
        ("KEYWORD", "if", 1, 1),
        ("KEYWORD", "return", 2, 2),
    ]


@pytest.mark.parametrize(
    ("source", "position"),
    [
        ("if\n  @", "2:3"),
        ("12.3.4", "1:5"),
        ('  "abc', "1:3"),
        ('\n "abc\ndef"', "2:2"),
    ],
)
def test_lexical_errors(source, position):
    with pytest.raises(ValueError, match=rf"^lexical: {position}: "):
        tokenize(source)


def test_cli_prints_tokens_from_file(tmp_path):
    source_file = tmp_path / "input example.txt"
    source_file.write_text("return 3.14", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, Path(__file__).with_name("main.py"), source_file],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        "(KEYWORD, return, 1:1)",
        "(FLOAT, 3.14, 1:8)",
    ]


def test_cli_reports_lexical_error(tmp_path):
    source_file = tmp_path / "invalid.txt"
    source_file.write_text("if\n  @", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, Path(__file__).with_name("main.py"), source_file],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.startswith("lexical: 2:3: ")

def test_cli_reports_missing_file(tmp_path):
    result = subprocess.run(
        [sys.executable, Path(__file__).with_name("main.py"), tmp_path / "missing.txt"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Ошибка чтения файла" in result.stderr
