import json
from pathlib import Path
from typing import Any

REQUESTS_DIR = Path(__file__).resolve().parent.parent / "requests"


def load_template(file_name: str) -> dict[str, Any]:
    path = REQUESTS_DIR / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def book_payload(**overrides: Any) -> dict[str, Any]:
    """Load requests/book.json and replace fields from the test context."""
    payload = load_template("book.json")
    payload.update(overrides)
    return payload


def author_payload(**overrides: Any) -> dict[str, Any]:
    """Load requests/author.json and replace fields from the test context."""
    payload = load_template("author.json")
    payload.update(overrides)
    return payload
