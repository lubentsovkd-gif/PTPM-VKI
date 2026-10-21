from src.calculator import TriangleCalculator


class TriangleController:
    """
    Связывает UI + БД + Calculator + NotificationService.
    Это главный объект для интеграционных тестов.
    """

    def __init__(self, db, ui, notifier):
        self.db = db
        self.ui = ui
        self.notifier = notifier

    def process(self):
        """Сквозной сценарий: ввод → результат."""
        a, b, c = self.ui.get_triangle_sides()
        return self.process_values(a, b, c)

    def process_values(self, a, b, c):
        """
        Отдельный метод — чтобы тестировать без input().
        Логика: БД → если нет, вычислить → сохранить → отправить → вернуть.
        """
        # 1. Проверка в БД
        existing = self.db.get(a, b, c)
        if existing:
            result = existing
        else:
            # 2. Вычисление
            triangle_type, error = TriangleCalculator.validate(a, b, c)
            result = {
                "a": a, "b": b, "c": c,
                "triangle_type": triangle_type,
                "error": error,
            }
            # 3. Сохранение
            self.db.add(a, b, c, triangle_type, error)

        # 4. Внешнее уведомление
        message = (
            f"Треугольник ({a}, {b}, {c}): "
            f"{result['triangle_type'] or result['error']}"
        )
        self.notifier.send(message)

        # 5. Показ пользователю
        self.ui.show_result(result)
        return result