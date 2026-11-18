import unittest
import os
from unittest.mock import patch, Mock

from src.parser import ForumParser
from src.database import DatabaseRepository


class TestForumParser(unittest.TestCase):
    def setUp(self):
        self.parser = ForumParser()
        self.fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "habr_comments.html"
        )

    def _get_fixture_html(self) -> str:
        with open(self.fixture_path, "r", encoding="utf-8") as f:
            return f.read()

    @patch("src.parser.requests.get")
    def test_parse_page_from_real_fixture(self, mock_get):
        """Тест на извлечение данных из реального HTML-слепка Хабра"""
        mock_response = Mock()
        mock_response.text = self._get_fixture_html()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = "https://habr.com/ru/articles/782332/comments/"
        result = self.parser.parse_page(url)

        mock_get.assert_called_once_with(url, headers=self.parser.headers, timeout=15)

        self.assertGreater(len(result), 0)

        first_comment = next((c for c in result if c["id"] == 26292034), None)
        self.assertIsNotNone(first_comment, "Комментарий с id 26292034 не найден")
        self.assertEqual(first_comment["name"], "Kriminalist")
        self.assertIn("Пересказывать теперь тоже нельзя?", first_comment["message"])

    @patch("src.parser.requests.get")
    def test_parse_page_empty_comments(self, mock_get):
        """Тест на ситуацию, когда комментариев на странице нет"""
        mock_response = Mock()
        mock_response.text = "<html><body><div class='tm-comments__empty'>Нет комментов</div></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.parser.parse_page("https://habr.com/ru/articles/1108814/comments/")
        self.assertEqual(result, [])

    def test_save_to_db(self):
        repo = DatabaseRepository(":memory:")
        data = [
            {"id": 1, "name": "alice", "message": "msg1"},
            {"id": 2, "name": "bob", "message": "msg2"},
        ]
        self.parser.save_to_db(data, repo)

        self.assertEqual(repo.get_by_id(1)["name"], "alice")
        self.assertEqual(repo.get_by_id(2)["message"], "msg2")
        repo.close()

    def test_save_to_db_skips_duplicates(self):
        repo = DatabaseRepository(":memory:")
        data = [
            {"id": 1, "name": "alice", "message": "first"},
            {"id": 1, "name": "bob", "message": "duplicate"},
        ]
        self.parser.save_to_db(data, repo)
        self.assertEqual(repo.get_by_id(1)["name"], "alice")
        repo.close()


if __name__ == "__main__":
    unittest.main()