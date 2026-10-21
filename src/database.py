import sqlite3


class TriangleDatabase:
    """Работа с SQLite. В тестах — ':memory:', в проде — файл."""

    def __init__(self, db_path="triangles.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS triangles (
                a REAL NOT NULL,
                b REAL NOT NULL,
                c REAL NOT NULL,
                triangle_type TEXT,
                error TEXT,
                PRIMARY KEY (a, b, c)
            )
        """)
        self.conn.commit()

    def add(self, a, b, c, triangle_type, error):
        """Добавить запись. Если уже есть — игнорировать (idempotent)."""
        try:
            self.conn.execute(
                "INSERT INTO triangles (a, b, c, triangle_type, error) "
                "VALUES (?, ?, ?, ?, ?)",
                (a, b, c, triangle_type, error),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # запись уже существует — не ошибка

    def get(self, a, b, c):
        """Вернуть dict или None, если записи нет."""
        cur = self.conn.execute(
            "SELECT a, b, c, triangle_type, error FROM triangles "
            "WHERE a=? AND b=? AND c=?",
            (a, b, c),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def delete(self, a, b, c):
        """Удалить запись. Вернуть True, если что-то удалено."""
        cur = self.conn.execute(
            "DELETE FROM triangles WHERE a=? AND b=? AND c=?",
            (a, b, c),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def close(self):
        self.conn.close()