import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import MagicMock, patch

from src.database import TriangleDatabase
from src.user_io import ConsoleUserInterface
from src.external_service import NotificationService, NotificationInterface
from src.controller import TriangleController


class TestTriangleIntegration(unittest.TestCase):

    def setUp(self):
        self.db = TriangleDatabase(":memory:")
        self.ui = MagicMock(spec=ConsoleUserInterface)
        self.notifier = MagicMock(spec=NotificationInterface)
        self.controller = TriangleController(self.db, self.ui, self.notifier)

    def tearDown(self):
        self.db.close()

    # ---------- ИНТЕГРАЦИОННЫЕ ----------

    def test_new_triangle_computes_and_saves(self):
        """Новые данные → вычисление + сохранение в БД + отправка."""
        result = self.controller.process_values(3, 3, 3)

        self.assertEqual(result["triangle_type"], "равносторонний")
        self.assertIsNone(result["error"])
        # БД реально сохранила
        self.assertIsNotNone(self.db.get(3, 3, 3))
        # Уведомление отправлено ровно один раз
        self.notifier.send.assert_called_once()

    def test_existing_triangle_uses_db(self):
        self.db.add(3, 4, 5, "разносторонний", None)

        with patch("src.controller.TriangleCalculator") as mock_calc:
            result = self.controller.process_values(3, 4, 5)

        self.assertEqual(result["triangle_type"], "разносторонний")
        mock_calc.validate.assert_not_called()  # ключевая проверка
        self.notifier.send.assert_called_once()

    def test_invalid_triangle_saves_error(self):
        """Невалидные данные → в БД пишется error, уведомление всё равно уходит."""
        result = self.controller.process_values(1, 1, 10)

        self.assertIsNone(result["triangle_type"])
        self.assertIn("не существует", result["error"])
        saved = self.db.get(1, 1, 10)
        self.assertIn("не существует", saved["error"])
        self.notifier.send.assert_called_once()

    def test_process_end_to_end_with_real_ui(self):
        """
        Сквозной сценарий через публичный API контроллера:
        process() -> ConsoleUserInterface (реальный) -> БД -> калькулятор -> notifier.
        """
        real_ui = ConsoleUserInterface()
        controller = TriangleController(self.db, real_ui, self.notifier)

        with patch("builtins.input", side_effect=["6", "6", "6"]), \
                patch("builtins.print"): # перечисление через / (синтаксический сахар крч)
            result = controller.process()

        self.assertEqual(result["triangle_type"], "равносторонний")
        self.assertIsNone(result["error"])
        self.assertIsNotNone(self.db.get(6.0, 6.0, 6.0))
        self.notifier.send.assert_called_once()

        sent_message = self.notifier.send.call_args[0][0] # в сути тоже, что и call_args.args[0]
        self.assertIn("равносторонний", sent_message)
        self.assertIn("6", sent_message)

    def test_controller_integrates_with_real_notifier(self):
        """
        Интеграция: Controller + реальная БД + реальный калькулятор
        + реальный NotificationService. Мокаем только ui (пользователь)
        и print (граница notifier'а с консолью).
        """
        from src.external_service import NotificationService

        real_notifier = NotificationService()
        controller = TriangleController(self.db, self.ui, real_notifier)

        with patch("builtins.print") as mock_print:
            result = controller.process_values(7, 8, 9)

        self.assertEqual(result["triangle_type"], "разносторонний")
        self.assertIsNone(result["error"])
        self.assertIsNotNone(self.db.get(7, 8, 9))

        mock_print.assert_called_once()
        printed = mock_print.call_args.args[0]
        self.assertIn("[УВЕДОМЛЕНИЕ]", printed)
        self.assertIn("разносторонний", printed)
        self.assertIn("7", printed)

        # 4. UI-мок получил результат, как требует сценарий
        self.ui.show_result.assert_called_once()

    # ---------- ЮНИТ-ТЕСТЫ ----------

    def test_ui_input_is_patched(self):
        """Подмена input() при полном сквозном сценарии."""
        self.ui.get_triangle_sides.return_value = (2, 2, 3)

        with patch("builtins.input", side_effect=["2", "2", "3"]):
            real_ui = ConsoleUserInterface()
            a, b, c = real_ui.get_triangle_sides()

        self.assertEqual((a, b, c), (2.0, 2.0, 3.0))

    def test_database_delete(self):
        """Метод delete()"""
        self.db.add(5, 5, 5, "равносторонний", None)
        self.assertTrue(self.db.delete(5, 5, 5))
        self.assertIsNone(self.db.get(5, 5, 5))
        self.assertFalse(self.db.delete(5, 5, 5))


if __name__ == "__main__":
    unittest.main()