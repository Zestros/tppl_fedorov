import pytest
from main import main

from main import add, subtract, multiply, divide, tilda, evaluate


@pytest.mark.parametrize("x, y, expected", [(2, 3, 5), (-2, 2, 0), (0.1, 0.2, 0.3)])
def test_add(x, y, expected):
    assert add(x, y) == pytest.approx(expected)


@pytest.mark.parametrize("x, y, expected", [(8, 3, 5), (3, 8, -5), (-2, -2, 0)])
def test_subtract(x, y, expected):
    assert subtract(x, y) == pytest.approx(expected)


@pytest.mark.parametrize("x, y, expected", [(2, 3, 6), (-2, 3, -6), (0, 5, 0)])
def test_multiply(x, y, expected):
    assert multiply(x, y) == pytest.approx(expected)


@pytest.mark.parametrize("x, y, expected", [(7, 2, 3.5), (-6, 2, -3), (0, 5, 0)])
def test_divide(x, y, expected):
    assert divide(x, y) == pytest.approx(expected)


@pytest.mark.parametrize("x", [5, -5, 0])
def test_divide_by_zero(x):
    with pytest.raises(ValueError, match="Делить на ноль нельзя"):
        divide(x, 0)


@pytest.mark.parametrize("x, y, stack, expected, remaining", [
    (3, 7, [10], 4, [10]),
    (-3, 7, [], 10, []),
    (4, 4, [], 0, []),
    (0, 4, [3, 2], 81, []),
    (4, 0, [3], 49, []),
    (0, 0, [3], 9, []),
    (0, 0, [], 0, []),
])
def test_tilda(x, y, stack, expected, remaining):
    stack = stack.copy()
    assert tilda(x, y, stack) == pytest.approx(expected)
    assert stack == remaining


@pytest.mark.parametrize("expression, expected", [
    ("2 3 +", 5),
    ("8 3 -", 5),
    ("2 3 *", 6),
    ("7 2 /", 3.5),
    ("3 7 ~", 4),
    ("3 0 4 ~", 49),
    ("3 4 0 ~", 49),
    ("0 3 4 ~ +", 1),
    ("3 0 4 ~ 2 ~", 47),
    ("2 2 + 4 - 4 ~ 2 3 * +", 22),
    ("8 4 3 + -", 1),
    ("-2 0.5 *", -1),
    ("0.1 0.2 +", 0.3),
    ("  2   3\t+  ", 5),
    ("42", 42),
])
def test_evaluate(expression, expected):
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize("expression, message", [
    ("5 0 /", "Делить на ноль нельзя"),
    ("2 +", "нужны два числа"),
    ("~", "нужны два числа"),
    ("abc", "неконвертируемое в число"),
    ("2 3", "должно остаться одно число"),
    ("", "должно остаться одно число"),
    ("   ", "должно остаться одно число"),
])
def test_evaluate_error(expression, message):
    with pytest.raises(ValueError, match=message):
        evaluate(expression)


def test_main_success(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "2 3 +"])
    assert main() == 0


def test_main_without_expression(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py"])
    assert main() == 1


def test_main_with_error(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "5 0 /"])
    assert main() == 1
