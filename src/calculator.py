class TriangleCalculator:
    """Логика определения типа треугольника (перенос из Lab_2)."""

    @staticmethod
    def validate(a, b, c):
        """
        Возвращает кортеж (triangle_type, error).
        Если треугольник валиден — error=None.
        Если нет — triangle_type=None, error=описание.
        """
        # 1. Проверка на положительность
        if a <= 0 or b <= 0 or c <= 0:
            return None, "Стороны должны быть положительными"

        # 2. Проверка неравенства треугольника
        if a + b <= c or a + c <= b or b + c <= a:
            return None, "Треугольник с такими сторонами не существует"

        # 3. Определение типа
        if a == b == c:
            return "равносторонний", None
        if a == b or b == c or a == c:
            return "равнобедренный", None
        return "разносторонний", None