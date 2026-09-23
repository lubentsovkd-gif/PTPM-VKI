import logging
import sys

# ANSI-коды для цветов
COLORS = {
    "DEBUG":    "\033[36m",   # голубой
    "INFO":     "\033[33m",   # жёлтый
    "WARNING":  "\033[35m",   # пурпурный
    "ERROR":    "\033[31m",   # красный
    "CRITICAL": "\033[41m",   # красный фон
}
RESET = "\033[0m"

# Классы для форматтеров логов (раскомментируйте нужный)
# Вариант 1: только уровень

class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = COLORS.get(record.levelname, "")
        # Подкрашиваем только уровень, чтобы остальное оставалось читаемым
        original = record.levelname
        record.levelname = f"{color}{original:<7}{RESET}"
        try:
            return super().format(record)
        finally:
            record.levelname = original  # восстанавливаем, чтобы не портить другие handlers
"""
#  Вариант 2: вся строка
class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelname, "")
        formatted = super().format(record)
        return f"{color}{formatted}{RESET}"
"""

# Формат без выравнивания уровня — выравнивание делаем сами в ColorFormatter
log_format = "%(asctime)s | [%(levelname)s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

formatter = ColorFormatter(fmt=log_format, datefmt=date_format)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs/file_txt.log", encoding="utf-8")
# В файл — без цветов, обычный форматтер
file_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))

logging.basicConfig(level=logging.DEBUG, handlers=[console_handler, file_handler])

# Меняем уровень логов matplotlib и pillow (plt обращается к нему), чтобы избавиться от лишних сообщений в lab1main
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)