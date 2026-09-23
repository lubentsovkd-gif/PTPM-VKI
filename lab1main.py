import colored_logs as logs
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

logs.logging.info("Логгер успешно сконфигурирован")
logs.logging.info("Приложение запущено")

tests_count = 1

def validate(a, b, c):
    logs.logging.info("Начата валидация данных")
    try:
        logs.logging.info(f"Проверка существования треугольника со сторонами {a}, {b}, {c})")
        a = float(a)
        b = float(b)
        c = float(c)
    except Exception as ex:
        logs.logging.exception("Невалидные данные: %s", ex)
        # я отказался преобразовывать координаты в (-2, -2), так как отрисовки всё равно не будет
        return 0

    if (a <= 0 or b <= 0 or c <= 0) or (a + b <= c or a + c <= b or b + c <= a):
        logs.logging.info("Результат проверки: не треугольник")
        # я отказался преобразовывать координаты в (-1, -1), так как отрисовки всё равно не будет
        return 0

    if a == b == c:
        kind = "равносторонний"
    elif a == b or a == c or b == c:
        kind = "равнобедренный"
    else:
        kind = "разносторонний"
    logs.logging.info(f"Результат проверки: %s", kind)
    logs.logging.info("Валидация данных успешно окончена.")
    return cords(kind, a, b, c)

def cords(kind, a, b, c):
    logs.logging.info("Начат подсчёт координат")
    scale = 80.0 / max(a, b, c)
    A = (a * scale, b * scale, c * scale)
    x1, y1 = 0.0, 0.0
    x2, y2 = A[0], 0.0
    x3 = (A[2] ** 2 - A[1] ** 2 + A[0] ** 2) / (2 * A[0]) # третья координата вычисляется какой-то стрёмной формулой из теоремы косинусов
    y3 = (A[2] ** 2 - x3 ** 2) ** 0.5
    points = [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))]
    return draw(kind, points)
    logs.logging.info("Подсчёт координат окончен")

def draw(kind, points):
    logs.logging.info("Начато выполнение отрисовки")
    global tests_count
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect('equal')
    xs = [p[0] for p in points] + [points[0][0]]
    ys = [p[1] for p in points] + [points[0][1]]
    ax.plot(xs, ys, 'b-')
    ax.set_title(f"Рисунок теста №{tests_count}: {kind}")
    plt.show()
    logs.logging.info("Выполнение отрисовки окончено")

def triangle(a, b, c):
    return validate(a, b, c)

def run_test(test_name, a, b, c):
    global tests_count
    print(f"\n\033[33m| Тест №{tests_count}: {test_name}: a = {a}, b = {b}, c = {c} |\033[0m")
    triangle(a, b, c)
    logs.logging.info(f"Тест №{tests_count} завершён.")
    tests_count += 1

# Вызовы для существующих тестов
run_test('Невалидные данные', "a", 3, 3)
run_test('Отрицательная сторона', 3, -3, 3)
run_test('Нулевая сторона', 3, 3, 0)
run_test('Равносторонний треугольник', 3, 3, 3)
run_test('Равнобедренный треугольник', 3, 4, 3)
run_test('Разносторонний (египетский) треугольник', 3, 4, 5)

logs.logging.info("Программа завершила свою работу")