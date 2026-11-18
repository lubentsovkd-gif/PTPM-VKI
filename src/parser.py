import requests
from bs4 import BeautifulSoup


class ForumParser:
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    }

    def __init__(self, headers: dict | None = None):
        self.headers = headers or self.DEFAULT_HEADERS

    def parse_page(self, url: str) -> list[dict]:
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        comments = []

        for item in soup.select("article.tm-comment-thread__comment"):
            raw_id = item.get("id", "")
            try:
                comment_id = int(raw_id)
            except ValueError:
                continue

            author_tag = item.select_one(".tm-user-info__username")
            username = author_tag.get_text(strip=True) if author_tag else "unknown"

            message_tag = item.select_one(".tm-comment__body-content")
            message_html = message_tag.decode_contents().strip() if message_tag else ""

            comments.append({
                "id": comment_id,
                "name": username,
                "message": message_html,
            })

        return comments

    def save_to_db(self, parsed_data: list[dict], repository) -> None:
        for item in parsed_data:
            try:
                repository.add(
                    comment_id=item["id"],
                    username=item["name"],
                    message=item["message"],
                )
            except Exception as e:
                print(f"Не удалось сохранить комментарий {item.get('id')}: {e}")