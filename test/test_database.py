import unittest
import sqlite3

from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):
    def setUp(self):
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repo.close()

    def test_add_success(self):
        result = self.repo.add(1, "alice", "Hello, world!")
        self.assertTrue(result)
        row = self.repo.get_by_id(1)
        self.assertEqual(row["name"], "alice")
        self.assertEqual(row["message"], "Hello, world!")

    def test_add_duplicate_id_raises(self):
        self.repo.add(1, "alice", "first")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add(1, "bob", "second")

    def test_add_username_too_long(self):
        long_name = "x" * 257
        with self.assertRaises(ValueError):
            self.repo.add(1, long_name, "msg")

    def test_add_message_too_long(self):
        long_msg = "x" * 8097
        with self.assertRaises(ValueError):
            self.repo.add(1, "alice", long_msg)

    def test_add_wrong_type(self):
        with self.assertRaises(ValueError):
            self.repo.add("1", "alice", "msg")

    def test_get_by_id_existing(self):
        self.repo.add(42, "bob", "test message")
        row = self.repo.get_by_id(42)
        self.assertIsNotNone(row)
        self.assertEqual(row["id"], 42)
        self.assertEqual(row["name"], "bob")

    def test_get_by_id_missing(self):
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_name_existing_multiple(self):
        self.repo.add(1, "alice", "first")
        self.repo.add(2, "alice", "second")
        self.repo.add(3, "bob", "other")
        rows = self.repo.get_by_name("alice")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["name"] == "alice" for r in rows))

    def test_get_by_name_missing(self):
        self.repo.add(1, "alice", "msg")
        self.assertEqual(self.repo.get_by_name("charlie"), [])

    def test_update_success(self):
        self.repo.add(1, "alice", "old")
        result = self.repo.update(1, "new message")
        self.assertTrue(result)
        self.assertEqual(self.repo.get_by_id(1)["message"], "new message")

    def test_update_missing_id(self):
        result = self.repo.update(999, "new")
        self.assertFalse(result)

    def test_update_message_too_long(self):
        self.repo.add(1, "alice", "old")
        with self.assertRaises(ValueError):
            self.repo.update(1, "x" * 8097)

    def test_delete_success(self):
        self.repo.add(1, "alice", "msg")
        result = self.repo.delete(1)
        self.assertTrue(result)
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_id(self):
        result = self.repo.delete(999)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()