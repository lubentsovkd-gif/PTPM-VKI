import sqlite3


class DatabaseRepository:

    def __init__(self, db_path: str = ':memory:'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL CHECK(length(name) <= 256),
                    message TEXT NOT NULL CHECK(length(message) <= 8096)
                )
            """)

    def get_by_id(self, comment_id: int):
        cur = self.conn.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_by_name(self, username: str):
        cur = self.conn.execute(
            "SELECT id, name, message FROM comments WHERE name = ?",
            (username,)
        )
        return [dict(row) for row in cur.fetchall()]

    def add(self, comment_id: int, username: str, message: str) -> bool:
        if not isinstance(comment_id, int):
            raise ValueError("comment_id должен быть целым числом")
        if not isinstance(username, str):
            raise ValueError("username должен быть строкой")
        if not isinstance(message, str):
            raise ValueError("message должен быть строкой")
        if len(username) > 256:
            raise ValueError("Длина username не должна превышать 256 символов")
        if len(message) > 8096:
            raise ValueError("Длина message не должна превышать 8096 символов")

        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                    (comment_id, username, message)
                )
            return True
        except sqlite3.IntegrityError:
            raise

    def update(self, comment_id: int, new_message: str) -> bool:
        if not isinstance(new_message, str):
            raise ValueError("new_message должен быть строкой")
        if len(new_message) > 8096:
            raise ValueError("Длина message не должна превышать 8096 символов")

        with self.conn:
            cur = self.conn.execute(
                "UPDATE comments SET message = ? WHERE id = ?",
                (new_message, comment_id)
            )
            return cur.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        with self.conn:
            cur = self.conn.execute(
                "DELETE FROM comments WHERE id = ?",
                (comment_id,)
            )
            return cur.rowcount > 0

    def close(self):
        self.conn.close()