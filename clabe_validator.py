"""CLABE validator.

Usage:
    python clabe_validator.py
Then input an 18-digit CLABE number when prompted.
"""


def is_valid_clabe(clabe: str) -> bool:
    """Return True if a CLABE string is valid, otherwise False."""
    if len(clabe) != 18 or not clabe.isdigit():
        return False

    weights = [3, 7, 1] * 6
    weighted_sum = sum((int(digit) * weight) % 10 for digit, weight in zip(clabe[:17], weights))
    check_digit = (10 - (weighted_sum % 10)) % 10

    return check_digit == int(clabe[17])


def main() -> None:
    clabe = input("请输入18位CLABE卡号: ").strip()
    if is_valid_clabe(clabe):
        print("合法")
    else:
        print("不合法")


if __name__ == "__main__":
    main()
