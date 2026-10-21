from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Абстрактный интерфейс пользователя."""

    @abstractmethod
    def get_triangle_sides(self):
        """Вернуть (a, b, c) — три числа."""
        pass

    @abstractmethod
    def show_result(self, result):
        """Показать результат пользователю."""
        pass


class ConsoleUserInterface(UserInterface):
    """Реализация через input()/print()."""

    def get_triangle_sides(self):
        a = float(input("Введите сторону a: "))
        b = float(input("Введите сторону b: "))
        c = float(input("Введите сторону c: "))
        return a, b, c

    def show_result(self, result):
        if result["error"]:
            print(f"Ошибка: {result['error']}")
        else:
            print(f"Тип треугольника: {result['triangle_type']}")