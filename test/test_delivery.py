import datetime
import unittest
from unittest.mock import patch

from src import Delivery


class TestDeliveryModule(unittest.TestCase):
    """Юнит-тесты для модуля Delivery (расчёт стоимости и даты доставки)."""

    # ==================================================================
    # ГРУППА 1. Валидация входных данных (границы веса/дистанции/типа)
    # ==================================================================

    # Тест 1. Нижняя граница веса (0.1 кг) принимается, ниже — отклоняется.
    def test_weight_boundaries(self):
        self.assertNotEqual(
            Delivery.calculate_delivery_cost(0.1, 100, "обычный")[0], -1
        )
        self.assertEqual(
            Delivery.calculate_delivery_cost(0.09, 100, "обычный"),
            (-1, "0000-00-00")
        )

    # Тест 2. Верхняя граница веса (50.0 кг) принимается, выше — отклоняется.
    def test_weight_upper_boundary(self):
        self.assertNotEqual(
            Delivery.calculate_delivery_cost(50.0, 100, "обычный")[0], -1
        )
        self.assertFalse(
            Delivery.calculate_delivery_cost(50.01, 100, "обычный")[0] != -1
        )

    # Тест 3. Границы дистанции: 1 и 5000 км принимаются, 0 и 5001 — нет.
    def test_distance_boundaries(self):
        self.assertNotEqual(
            Delivery.calculate_delivery_cost(1.0, 1, "обычный")[0], -1
        )
        self.assertEqual(
            Delivery.calculate_delivery_cost(1.0, 0, "обычный"),
            (-1, "0000-00-00")
        )
        self.assertNotEqual(
            Delivery.calculate_delivery_cost(1.0, 5000, "обычный")[0], -1
        )
        self.assertEqual(
            Delivery.calculate_delivery_cost(1.0, 5001, "обычный")[0], -1
        )

    # Тест 4. Неизвестный, пустой и регистрозависимый тип упаковки отклоняются.
    def test_invalid_package_types_are_rejected(self):
        self.assertEqual(
            Delivery.calculate_delivery_cost(1.0, 100, "стеклянный"),
            (-1, "0000-00-00")
        )
        self.assertEqual(
            Delivery.calculate_delivery_cost(1.0, 100, "")[0], -1
        )
        self.assertEqual(
            Delivery.calculate_delivery_cost(1.0, 100, "Обычный")[1],
            "0000-00-00"
        )

    # ==================================================================
    # ГРУППА 2. Базовая стоимость и надбавки за тип упаковки
    # ==================================================================

    # Тест 5. Базовая стоимость: 200 + distance * 5.
    def test_base_cost_calculation(self):
        cost, _ = Delivery.calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    # Тест 6. Надбавки за тип упаковки: хрупкий +300, опасный +1000.
    def test_package_type_surcharges(self):
        fragile, _ = Delivery.calculate_delivery_cost(1.0, 100, "хрупкий")
        dangerous, _ = Delivery.calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(fragile, 1000)
        self.assertEqual(dangerous, 1700)

    # ==================================================================
    # ГРУППА 3. Весовые коэффициенты
    # ==================================================================

    # Тест 7. Вес ровно 5 кг — коэффициент не применяется.
    def test_weight_exactly_5_no_multiplier(self):
        cost, _ = Delivery.calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 700)

    # Тест 8. Вес 10 кг — коэффициент 1.2.
    def test_medium_weight_multiplier(self):
        cost, _ = Delivery.calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)

    # Тест 9. Вес 20 кг — коэффициент 1.5.
    def test_heavy_weight_multiplier(self):
        cost, _ = Delivery.calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    # ==================================================================
    # ГРУППА 4. Экспресс-доставка (проверка багов)
    # ==================================================================

    # Тест 10. БАГ: экспресс-доставка должна быть дороже обычной.
    def test_express_should_be_more_expensive(self):
        normal, _ = Delivery.calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        express, _ = Delivery.calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        self.assertGreater(express, normal,
                           "Экспресс-доставка должна быть дороже обычной")

    # Тест 11. Экспресс-доставка быстрее обычной.
    def test_express_is_faster(self):
        _, normal_date = Delivery.calculate_delivery_cost(1.0, 2000, "обычный", is_express=False)
        _, express_date = Delivery.calculate_delivery_cost(1.0, 2000, "обычный", is_express=True)
        normal_dt = datetime.datetime.strptime(normal_date, "%Y-%m-%d")
        express_dt = datetime.datetime.strptime(express_date, "%Y-%m-%d")
        self.assertLess(express_dt, normal_dt)

    # Тест 12. БАГ: экспресс не может дать дату доставки == дате отправки.
    def test_express_never_zero_days(self):
        _, date_str = Delivery.calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        start = datetime.date(2026, 9, 3)
        delivery = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        self.assertGreaterEqual(
            (delivery - start).days, 1,
            "Дата доставки не может совпадать с датой отправки"
        )

    # ==================================================================
    # ГРУППА 5. Расчёт даты доставки (обычная)
    # ==================================================================

    # Тест 13. Минимальный срок — 1 день при короткой дистанции.
    def test_minimum_delivery_days_is_one(self):
        _, date_str = Delivery.calculate_delivery_cost(1.0, 100, "обычный")
        expected = datetime.date(2026, 9, 3) + datetime.timedelta(days=1)
        self.assertEqual(date_str, expected.strftime("%Y-%m-%d"))

    # Тест 14. Дистанция 5000 км — 10 дней доставки.
    def test_delivery_days_for_max_distance(self):
        _, date_str = Delivery.calculate_delivery_cost(1.0, 5000, "обычный")
        expected = datetime.date(2026, 9, 3) + datetime.timedelta(days=10)
        self.assertEqual(date_str, expected.strftime("%Y-%m-%d"))

    # ==================================================================
    # ГРУППА 6. Формат результата и изоляция через мок
    # ==================================================================

    # Тест 15. Успешный результат — кортеж (int, str) с корректным форматом даты.
    def test_result_format_and_date_parsing(self):
        result = Delivery.calculate_delivery_cost(1.0, 100, "обычный")
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], int)
        # Парсинг выбросит ValueError, если формат даты неверный
        datetime.datetime.strptime(result[1], "%Y-%m-%d")
        self.assertEqual(len(result[1]), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)