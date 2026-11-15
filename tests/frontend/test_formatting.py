"""Tests of the number formatting used by the screens."""
import unittest

from app.frontend.formatting import (
    EMPTY,
    format_hours,
    format_number,
    format_with_unit,
)


class FormattingTests(unittest.TestCase):

    def test_format_number_trims_zeros(self):
        self.assertEqual(format_number(37.25), "37.2")
        self.assertEqual(format_number(30.0), "30")
        self.assertEqual(format_number(0.1, 2), "0.1")

    def test_format_number_without_value(self):
        self.assertEqual(format_number(None), EMPTY)

    def test_format_with_unit(self):
        self.assertEqual(format_with_unit(37.2, "°C"), "37.2 °C")
        self.assertEqual(format_with_unit(10, "/100"), "10/100")
        self.assertEqual(format_with_unit(None, "kg"), EMPTY)

    def test_format_hours(self):
        self.assertEqual(format_hours(7.5), "7:30 hr")
        self.assertEqual(format_hours(6.62), "6:37 hr")
        self.assertEqual(format_hours(None), EMPTY)


if __name__ == "__main__":
    unittest.main()
