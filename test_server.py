"""Unit tests for the calculator functions."""

import unittest
from server import add, subtract, multiply, divide, power, sqrt, modulo, percentage, calculate


class TestCalculator(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(add(10, 5), 15)
        self.assertEqual(subtract(10, 5), 5)
        self.assertEqual(multiply(10, 5), 50)
        self.assertEqual(divide(10, 2), 5)
        self.assertEqual(power(2, 3), 8)
        self.assertEqual(sqrt(16), 4)
        self.assertEqual(modulo(10, 3), 1)
        self.assertEqual(percentage(25, 100), 25.0)

    def test_large_numbers_exact_precision(self):
        # 1,232,483,204 * 8,435,639,485,639 = 10396783981049266707356
        self.assertEqual(
            multiply("1,232,483,204", "8,435,639,485,639"),
            10396783981049266707356
        )
        self.assertEqual(
            calculate("1,232,483,204 by 8,435,639,485,639"),
            10396783981049266707356
        )
        # 3242 * 435 = 1410270
        self.assertEqual(
            calculate("3242 times 435"),
            1410270
        )
        self.assertEqual(
            multiply("3,242", "435"),
            1410270
        )

    def test_natural_language_and_commas(self):
        self.assertEqual(calculate("1,000 plus 2,500"), 3500)
        self.assertEqual(calculate("10,000 divided by 4"), 2500)
        self.assertEqual(calculate("2 ^ 10"), 1024)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)

    def test_sqrt_negative(self):
        with self.assertRaises(ValueError):
            sqrt(-4)

    def test_calculate_expression(self):
        self.assertEqual(calculate("2 + 2 * 2"), 6)
        self.assertEqual(calculate("(10 + 5) / 3"), 5)
        self.assertEqual(calculate("sqrt(25) * 2"), 10)
        self.assertEqual(calculate("sin(0) + cos(0)"), 1)
        self.assertGreater(calculate("pi * 2"), 6.28)
        self.assertEqual(calculate("abs(-42)"), 42)
        self.assertEqual(calculate("floor(4.9)"), 4)
        self.assertEqual(calculate("ceil(4.1)"), 5)

    def test_calculate_safety(self):
        with self.assertRaises(ValueError):
            calculate("__import__('os').system('ls')")

        with self.assertRaises(ValueError):
            calculate("open('file.txt').read()")


if __name__ == "__main__":
    unittest.main()
