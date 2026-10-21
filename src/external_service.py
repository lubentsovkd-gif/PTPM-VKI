from abc import ABC, abstractmethod


class NotificationInterface(ABC):
    """
    Абстрактный интерфейс сторонней зависимости.
    По README класс сторонней зависимости должен быть через abc.
    """

    @abstractmethod
    def send(self, message: str) -> bool:
        """Отправить сообщение во внешнюю систему. Вернуть True при успехе."""
        pass


class NotificationService(NotificationInterface):
    """
    Имитация внешнего сервиса (например, email-сервер).
    В тестах подменяется через MagicMock(spec=NotificationInterface)
    или patch(...).
    """

    def send(self, message: str) -> bool:
        print(f"[УВЕДОМЛЕНИЕ]: {message}")
        return True