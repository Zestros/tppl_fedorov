import argparse
from pathlib import Path


KEYWORDS = {"if", "else", "while", "return", "for", "def"}


def tokenize(source: str) -> list[tuple[str, str, int, int]]:
    tokens = []

    for line, text in enumerate(source.split("\n"), start=1):
        string_start = None
        skip_chars = 0

        for column, char in enumerate(text, start=1):
            if skip_chars > 0:
                skip_chars -= 1
                continue

            if string_start is not None:
                if char == '"':
                    value = text[string_start:column - 1]
                    tokens.append(("STRING", value, line, string_start))
                    string_start = None
                continue

            if char == '"':
                string_start = column
            elif char == "#":
                break
            elif char in " \t":
                continue
            elif char in "(){},;":
                tokens.append(("SEP", char, line, column))
            elif char in "+-*/=<>":
                pair = text[column - 1:column + 1]
                if pair in ("==", "<=", ">="):
                    tokens.append(("OP", pair, line, column))
                    skip_chars = 1
                else:
                    tokens.append(("OP", char, line, column))
            elif char.isdecimal():
                start = column - 1
                end = column

                while end < len(text) and text[end].isdecimal():
                    end += 1

                kind = "INT"
                if end + 1 < len(text) and text[end] == "." and text[end + 1].isdecimal():
                    kind = "FLOAT"
                    end += 2
                    while end < len(text) and text[end].isdecimal():
                        end += 1

                value = text[start:end]
                tokens.append((kind, value, line, column))
                skip_chars = len(value) - 1
            elif char.isalpha() or char == "_":
                start = column - 1
                end = column

                while end < len(text):
                    next_char = text[end]
                    if not (next_char.isalpha() or next_char.isdigit() or next_char == "_"):
                        break
                    end += 1

                word = text[start:end]
                kind = "KEYWORD" if word in KEYWORDS else "IDENT"
                tokens.append((kind, word, line, column))
                skip_chars = len(word) - 1
            else:
                raise ValueError(f"lexical: {line}:{column}: неожиданный символ {char!r}")

        if string_start is not None:
            raise ValueError(f"lexical: {line}:{string_start}: незакрытая строка")

    return tokens


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    try:
        source = args.file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"Ошибка чтения файла {args.file}: {exc}\n")

    try:
        tokens = tokenize(source)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")

    for kind, value, line, column in tokens:
        print(f"({kind}, {value}, {line}:{column})")


if __name__ == "__main__":
    main()
