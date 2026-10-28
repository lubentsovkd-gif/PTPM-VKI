import unittest
from src.converter import Converter


class TestConverter(unittest.TestCase):

    """
    Положительные и отрицательные сценарии
    """
    def test_large_positive(self):
        # x >> 100.7
        self.assertEqual(Converter.do(9999.9), 1000)

    def test_multiple_values_above_100_7(self):
        # x >= 100.7
        for value in (150.0, 500.5):
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), 1000)

    def test_positive_fractional(self):
        # 0 < x < 100.7
        self.assertEqual(Converter.do(65.7), 65)

    def test_positive_integer_like(self):
        # 0 < x < 100.7
        self.assertEqual(Converter.do(1.0), 1)

    def test_multiple_values_in_positive_range(self):
        # 0 < x < 100.7
        for value, expected in [(0.1, 0), (50.0, 50), (99.9, 99)]:
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), expected)

    def test_negative_fractional(self):
        # -30.4 < x < 0
        self.assertEqual(Converter.do(-15.5), -20)

    def test_near_zero_negative(self):
        # -30.4 < x < 0
        self.assertEqual(Converter.do(-0.1), -5)

    def test_multiple_values_in_negative_mid_range(self):
        # -30.4 < x < 0
        for value, expected in [(-15.5, -20), (-1.2, -6)]:
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), expected)

    def test_large_negative(self):
        # x << -30.5
        self.assertEqual(Converter.do(-1000.0), -2000)

    def test_multiple_values_at_or_below_minus_30_5(self):
        # x < -30.5
        for value in (-31.0, -500.0):
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), -2000)

    def test_return_type_is_int(self):
        # int type
        for x in (50.0, -10.0, 200.0, -100.0):
            with self.subTest(x=x):
                self.assertIsInstance(Converter.do(x), int)

    """
    Граничные значения диапазонов
    """
    def test_upper_boundary_100_7(self):
        # x == 100.7
        self.assertEqual(Converter.do(100.7), 1000)

    def test_just_below_upper_boundary(self):
        # x == 100.6
        self.assertEqual(Converter.do(100.6), 100)

    def test_lower_boundary_minus_30_4(self):
        # x == -30.4
        self.assertEqual(Converter.do(-30.4), -35)

    def test_upper_boundary_minus_30_5(self):
        # x == -30.5
        self.assertEqual(Converter.do(-30.5), -2000)

    """
    Проверка генерации исключения при x == 0
    """
    def test_zero_raises_value_error(self):
        # x == 0.0
        self.assertRaises(ValueError, Converter.do, 0.0)


if __name__ == "__main__":
    unittest.main()