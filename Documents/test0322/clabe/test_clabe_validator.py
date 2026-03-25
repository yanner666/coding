import tempfile
import unittest
from pathlib import Path

from clabe_validator import (
    _parse_cli_inputs,
    calculate_check_digit,
    is_valid_clabe,
    load_clabes_from_file,
    validate_clabe,
    validate_clabes,
)


class ClabeValidatorTests(unittest.TestCase):
    def test_calculate_check_digit(self) -> None:
        self.assertEqual(calculate_check_digit("03218000011835971"), 9)

    def test_is_valid_clabe_accepts_valid_value(self) -> None:
        self.assertTrue(is_valid_clabe("032180000118359719"))

    def test_is_valid_clabe_rejects_invalid_checksum(self) -> None:
        self.assertFalse(is_valid_clabe("032180000118359718"))

    def test_is_valid_clabe_rejects_fullwidth_digits(self) -> None:
        self.assertFalse(is_valid_clabe("０３２１８００００１１８３５９７１９"))

    def test_validate_clabe_accepts_surrounding_whitespace(self) -> None:
        validate_clabe(" 032180000118359719 ")

    def test_validate_clabe_raises_on_invalid_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "checksum"):
            validate_clabe("032180000118359718")

    def test_validate_clabes_returns_batch_results(self) -> None:
        self.assertEqual(
            validate_clabes(["032180000118359719", "032180000118359718"]),
            [("032180000118359719", True), ("032180000118359718", False)],
        )

    def test_load_clabes_from_file_ignores_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "clabes.txt"
            path.write_text("032180000118359719\n\n032180000118359718\n", encoding="utf-8")
            self.assertEqual(
                load_clabes_from_file(str(path)),
                ["032180000118359719", "032180000118359718"],
            )

    def test_parse_cli_inputs_merges_files_and_inline_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "clabes.txt"
            path.write_text("032180000118359719\n", encoding="utf-8")
            self.assertEqual(
                _parse_cli_inputs(["--file", str(path), "032180000118359718"]),
                ["032180000118359719", "032180000118359718"],
            )

    def test_parse_cli_inputs_requires_path_after_file_flag(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing file path"):
            _parse_cli_inputs(["--file"])


if __name__ == "__main__":
    unittest.main()
