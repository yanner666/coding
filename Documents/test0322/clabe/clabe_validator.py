"""Utilities for validating 18-digit CLABE numbers.

CLABE (Clave Bancaria Estandarizada) is a Mexican bank account identifier.
The 18th digit is a checksum calculated from the first 17 digits with the
weight pattern 3, 7, 1 repeated.
"""

from __future__ import annotations

import sys
from typing import Iterable


CLABE_LENGTH = 18
_WEIGHTS = (3, 7, 1)
_ASCII_DIGITS = frozenset("0123456789")


def _normalize_clabe(value: str) -> str:
    """Trim surrounding whitespace from a user-provided CLABE string."""
    return value.strip()


def _has_only_ascii_digits(value: str) -> bool:
    """Return True when *value* contains only ASCII digits."""
    return all(char in _ASCII_DIGITS for char in value)


def _ensure_digit_string(value: str, expected_length: int, label: str) -> str:
    """Normalize and validate a CLABE-like digit string."""
    normalized = _normalize_clabe(value)

    if len(normalized) != expected_length:
        raise ValueError(f"{label} must contain exactly {expected_length} digits.")
    if not _has_only_ascii_digits(normalized):
        raise ValueError(f"{label} must contain only ASCII digits (0-9).")

    return normalized


def calculate_check_digit(clabe17: str) -> int:
    """Return the checksum digit for the first 17 digits of a CLABE."""
    normalized = _ensure_digit_string(clabe17, CLABE_LENGTH - 1, "CLABE prefix")

    total = sum((int(digit) * _WEIGHTS[index % len(_WEIGHTS)]) % 10 for index, digit in enumerate(normalized))
    return (10 - (total % 10)) % 10


def is_valid_clabe(clabe: str) -> bool:
    """Return True when *clabe* is a valid 18-digit CLABE."""
    try:
        normalized = _ensure_digit_string(clabe, CLABE_LENGTH, "CLABE")
    except ValueError:
        return False

    expected_digit = calculate_check_digit(normalized[: CLABE_LENGTH - 1])
    return expected_digit == int(normalized[-1])


def validate_clabe(clabe: str) -> None:
    """Raise ValueError when *clabe* is not a valid 18-digit CLABE."""
    normalized = _ensure_digit_string(clabe, CLABE_LENGTH, "CLABE")
    if not is_valid_clabe(normalized):
        raise ValueError("Invalid CLABE checksum.")


def validate_clabes(clabes: Iterable[str]) -> list[tuple[str, bool]]:
    """Return validation results for multiple CLABEs."""
    return [(clabe, is_valid_clabe(clabe)) for clabe in clabes]


def load_clabes_from_file(path: str) -> list[str]:
    """Load CLABEs from a text file, ignoring blank lines."""
    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def _parse_cli_inputs(args: list[str]) -> list[str]:
    """Parse CLI arguments into a combined list of CLABEs."""
    clabes: list[str] = []
    index = 0

    while index < len(args):
        arg = args[index]
        if arg == "--file":
            if index + 1 >= len(args):
                raise ValueError("Missing file path after --file.")
            clabes.extend(load_clabes_from_file(args[index + 1]))
            index += 2
            continue

        clabes.append(arg)
        index += 1

    return clabes


def main(argv: list[str] | None = None) -> int:
    """CLI for validating CLABEs passed as arguments or loaded from a file."""
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print(
            "Usage: python clabe_validator.py <18-digit-clabe> [more-clabes...]\n"
            "   or: python clabe_validator.py [--file <path-to-text-file>] [more-clabes...]"
        )
        return 1

    try:
        clabes = _parse_cli_inputs(args)
    except ValueError as exc:
        print(f"Invalid arguments: {exc}")
        return 1
    except OSError as exc:
        print(f"Failed to read file: {exc}")
        return 1

    if not clabes:
        print("No CLABEs were provided.")
        return 1

    results = validate_clabes(clabes)
    if len(results) == 1:
        print("Valid CLABE" if results[0][1] else "Invalid CLABE")
        return 0 if results[0][1] else 1

    has_invalid = False
    for clabe, is_valid in results:
        status = "Valid" if is_valid else "Invalid"
        print(f"{clabe}: {status}")
        has_invalid = has_invalid or not is_valid

    return 1 if has_invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
