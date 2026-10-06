import contextlib
import io
import logging
import unittest
from unittest.mock import MagicMock, patch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src import lab1main


class TestLab1Main(unittest.TestCase):
    """Юнит-тесты для модуля lab1main (проверка и отрисовка треугольника)."""

    def setUp(self):
        """Перед каждым тестом: закрываем все фигуры и сбрасываем счётчик тестов."""
        plt.close("all")
        lab1main.tests_count = 1

        self._log_patcher = patch.object(logging.root, "handle")
        self._log_patcher.start()
        self.addCleanup(self._log_patcher.stop)

    def _patch(self, target, **kwargs):
        """Хелпер: запускает patch, регистрирует остановку и возвращает мок."""
        p = patch(target, **kwargs)
        self.addCleanup(p.stop)
        return p.start()

    # ==================================================================
    # ГРУППА 1. validate: отклонение невалидных данных
    # ==================================================================

    # Тест 1. validate возвращает 0 и не вызывает cords, если аргумент не число.
    def test_validate_rejects_non_numeric(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate("a", 3, 3)

        self.assertEqual(result, 0)
        mock_cords.assert_not_called()

    # Тест 2. validate отклоняет треугольник с отрицательной стороной.
    def test_validate_rejects_negative_side(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate(3, -3, 3)

        self.assertIs(result, 0)
        mock_cords.assert_not_called()

    # Тест 3. validate отклоняет треугольник с нулевой стороной.
    def test_validate_rejects_zero_side(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate(3, 3, 0)

        self.assertFalse(result)
        mock_cords.assert_not_called()

    # Тест 4. validate отклоняет вырожденный треугольник (a + b == c).
    def test_validate_rejects_triangle_inequality_equal(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate(1, 2, 3)

        self.assertEqual(result, 0)
        mock_cords.assert_not_called()

    # Тест 5. validate отклоняет треугольник, где нарушено неравенство (a + b < c).
    def test_validate_rejects_triangle_inequality_less(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate(2, 3, 6)

        self.assertIs(result, 0)
        mock_cords.assert_not_called()

    # Тест 6. validate отклоняет None в качестве стороны.
    def test_validate_rejects_none(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate(None, 3, 3)

        self.assertEqual(result, 0)
        mock_cords.assert_not_called()

    # Тест 7. validate отклоняет список в качестве стороны.
    def test_validate_rejects_list(self):
        mock_cords = self._patch("src.lab1main.cords", return_value="OK")

        result = lab1main.validate([3], 3, 3)

        self.assertIs(result, 0)
        mock_cords.assert_not_called()

    # ==================================================================
    # ГРУППА 2. validate: корректные треугольники и классификация типа
    # ==================================================================

    # Тест 8. validate определяет равносторонний треугольник и вызывает cords.
    def test_validate_accepts_equilateral(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate(3, 3, 3)

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("равносторонний", 3.0, 3.0, 3.0)

    # Тест 9. validate определяет равнобедренный (a == b).
    def test_validate_accepts_isosceles_ab(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate(3, 3, 4)

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("равнобедренный", 3.0, 3.0, 4.0)

    # Тест 10. validate определяет равнобедренный (a == c).
    def test_validate_accepts_isosceles_ac(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate(3, 4, 3)

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("равнобедренный", 3.0, 4.0, 3.0)

    # Тест 11. validate определяет равнобедренный (b == c).
    def test_validate_accepts_isosceles_bc(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate(4, 3, 3)

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("равнобедренный", 4.0, 3.0, 3.0)

    # Тест 12. validate определяет разносторонний треугольник.
    def test_validate_accepts_scalene(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate(3, 4, 5)

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("разносторонний", 3.0, 4.0, 5.0)

    # Тест 13. validate корректно преобразует строки в float.
    def test_validate_converts_strings_to_float(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate("3", "4", "5")

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("разносторонний", 3.0, 4.0, 5.0)

    # Тест 14. validate принимает дробные стороны.
    def test_validate_accepts_float_sides(self):
        sentinel = object()
        mock_cords = self._patch("src.lab1main.cords", return_value=sentinel)

        result = lab1main.validate(3.5, 4.5, 5.5)

        self.assertIs(result, sentinel)
        mock_cords.assert_called_once_with("разносторонний", 3.5, 4.5, 5.5)

    # Тест 15. validate пишет в лог результат проверки и завершение валидации.
    def test_validate_logs_success_kind(self):
        mock_info = self._patch("src.lab1main.logs.logging.info")
        self._patch("src.lab1main.cords", return_value=None)

        lab1main.validate(3, 3, 3)

        mock_info.assert_any_call("Результат проверки: %s", "равносторонний")
        mock_info.assert_any_call("Валидация данных успешно окончена.")

    # ==================================================================
    # ГРУППА 3. cords: расчёт координат вершин
    # ==================================================================

    # Тест 16. cords корректно считает точки для египетского треугольника (3,4,5).
    def test_cords_computes_points_for_345(self):
        mock_draw = self._patch("src.lab1main.draw", return_value="DRAWN")

        result = lab1main.cords("разносторонний", 3, 4, 5)

        self.assertEqual(result, "DRAWN")
        mock_draw.assert_called_once_with(
            "разносторонний",
            [(0, 0), (48, 0), (48, 64)]
        )

    # Тест 17. cords масштабирует равносторонний треугольник до 80 по стороне.
    def test_cords_scales_equilateral(self):
        mock_draw = self._patch("src.lab1main.draw", return_value=None)

        result = lab1main.cords("равносторонний", 3, 3, 3)

        self.assertIsNone(result)
        mock_draw.assert_called_once_with(
            "равносторонний",
            [(0, 0), (80, 0), (40, 69)]
        )

    # Тест 18. cords передаёт в draw правильный тип треугольника и 3 точки.
    def test_cords_calls_draw_with_kind(self):
        mock_draw = self._patch("src.lab1main.draw", return_value="OK")

        lab1main.cords("равнобедренный", 5, 5, 6)

        called_kind = mock_draw.call_args[0][0]
        called_points = mock_draw.call_args[0][1]

        self.assertEqual(called_kind, "равнобедренный")
        self.assertEqual(len(called_points), 3)
        self.assertIsInstance(called_points[0], tuple)

    # ==================================================================
    # ГРУППА 4. draw: отрисовка треугольника
    # ==================================================================

    # Тест 19. draw рисует замкнутый контур треугольника синей линией.
    def test_draw_plots_triangle(self):
        mock_ax = MagicMock()
        mock_fig = MagicMock()
        self._patch("src.lab1main.plt.subplots", return_value=(mock_fig, mock_ax))
        mock_show = self._patch("src.lab1main.plt.show")

        lab1main.tests_count = 3
        lab1main.draw("разносторонний", [(0, 0), (10, 0), (5, 8)])

        mock_ax.plot.assert_called_once_with(
            [0, 10, 5, 0],
            [0, 0, 8, 0],
            "b-"
        )
        mock_show.assert_called_once()

    # Тест 20. draw устанавливает лимиты осей, равный масштаб и заголовок с номером.
    def test_draw_sets_title_and_limits(self):
        mock_ax = MagicMock()
        mock_fig = MagicMock()
        self._patch("src.lab1main.plt.subplots", return_value=(mock_fig, mock_ax))
        self._patch("src.lab1main.plt.show")

        lab1main.tests_count = 7
        lab1main.draw("равнобедренный", [(0, 0), (1, 0), (0, 1)])

        mock_ax.set_xlim.assert_called_once_with(-5, 105)
        mock_ax.set_ylim.assert_called_once_with(-5, 105)
        mock_ax.set_aspect.assert_called_once_with("equal")
        mock_ax.set_title.assert_called_once_with(
            "Рисунок теста №7: равнобедренный"
        )

    # ==================================================================
    # ГРУППА 5. triangle и run_test: делегирование и учёт тестов
    # ==================================================================

    # Тест 21. triangle просто делегирует вызов в validate.
    def test_triangle_delegates_to_validate(self):
        mock_validate = self._patch("src.lab1main.validate", return_value="VALID")

        result = lab1main.triangle(1, 2, 3)

        self.assertEqual(result, "VALID")
        mock_validate.assert_called_once_with(1, 2, 3)

    # Тест 22. run_test вызывает triangle и увеличивает счётчик на 1.
    def test_run_test_calls_triangle_and_increments_counter(self):
        mock_triangle = self._patch("src.lab1main.triangle")
        lab1main.tests_count = 1

        lab1main.run_test("Имя теста", 3, 4, 5)

        mock_triangle.assert_called_once_with(3, 4, 5)
        self.assertEqual(lab1main.tests_count, 2)

    # Тест 23. run_test печатает заголовок с номером теста в stdout.
    def test_run_test_prints_header(self):
        self._patch("src.lab1main.triangle")
        lab1main.tests_count = 2

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            lab1main.run_test("Мой тест", 1, 2, 2)

        self.assertIn("Тест №2: Мой тест: a = 1, b = 2, c = 2", buf.getvalue())

    # Тест 24. run_test пишет в лог сообщение о завершении теста.
    def test_run_test_logs_completion(self):
        self._patch("src.lab1main.triangle")
        mock_info = self._patch("src.lab1main.logs.logging.info")
        lab1main.tests_count = 4

        lab1main.run_test("Лог", 3, 3, 3)

        mock_info.assert_any_call("Тест №4 завершён.")

    # Тест 25. run_test не увеличивает счётчик, если triangle бросил исключение.
    def test_run_test_does_not_increment_on_triangle_exception(self):
        mock_triangle = self._patch(
            "src.lab1main.triangle",
            side_effect=RuntimeError("boom")
        )
        lab1main.tests_count = 5

        with self.assertRaises(RuntimeError):
            lab1main.run_test("Ошибка", 3, 3, 3)

        self.assertEqual(lab1main.tests_count, 5)
        mock_triangle.assert_called_once_with(3, 3, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)