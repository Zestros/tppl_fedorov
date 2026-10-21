import sys
import os

def add(x: float, y: float) -> float:
    return x + y

def subtract(x: float, y: float) -> float:
    return x - y

def multiply(x: float, y: float) -> float:
    return x * y

def divide(x: float, y: float) -> float:
    if y == 0:
        raise ValueError("Делить на ноль нельзя")
    return x / y

def tilda(x: float, y: float, stack: list[float]) -> float:
    if x != 0 and y != 0:
        return abs(x - y)

    result = (sum(stack) + x + y) ** 2
    stack.clear()
    return result


def evaluate(expression: str) -> float:
    """Вычислить выражение и вывести состояние стека после каждого шага"""

    stack: list[float] = []

    expression_list: list[str]= expression.split()

    operations = {
        "+": add,
        "-": subtract,
        "*": multiply,
        "/": divide,
        "~": tilda,
    }

    for token in expression_list:
        if token not in operations:
            try:
                number = float(token)
            except ValueError:
                raise ValueError(f"{token} - что-то непонятное и неконвертируемое в число")

            stack.append(number)
        else:
            if len(stack) < 2:
                raise ValueError(f"Для операции {token} нужны два числа")

            y = stack.pop()  # Правый операнд
            x = stack.pop()  # Левый операнд

            if token == "~":
                result = operations[token](x, y, stack)
            else:
                result = operations[token](x, y)

            stack.append(result)

        print(f"{token} -> {stack}")

    if len(stack) != 1:
        raise ValueError("После вычисления в стеке должно остаться одно число")

    return stack[0]


def main() -> int:
    """Прочитать выражение из аргументов командной строки"""
    args = sys.argv[1:]
    if not args:
        print('Укажите выражение, например: python3 main.py "3 0 4 ~ 2 ~"',
              file=sys.stderr)
        return 1

    args = [
        "~" if arg == os.path.expanduser("~") else arg
        for arg in args
    ]

    expression = " ".join(args)

    try:
        result = evaluate(expression)
    except (ValueError, ZeroDivisionError, NotImplementedError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(f"{expression} = {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
