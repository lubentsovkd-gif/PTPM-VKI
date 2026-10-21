from calculator import TriangleCalculator
from database import TriangleDatabase
from user_io import ConsoleUserInterface
from external_service import NotificationService
from controller import TriangleController


def main():
    db = TriangleDatabase("triangles.db")
    ui = ConsoleUserInterface()
    notifier = NotificationService()

    controller = TriangleController(db, ui, notifier)
    controller.process()
    db.close()


if __name__ == "__main__":
    main()