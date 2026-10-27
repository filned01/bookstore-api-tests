import requests

BOOK_FIELDS = {"id", "title", "description", "pageCount", "excerpt", "publishDate"}
AUTHOR_FIELDS = {"id", "idBook", "firstName", "lastName"}


def assert_status(response: requests.Response, expected: int) -> None:
    assert response.status_code == expected, response.text


def assert_problem(response: requests.Response, expected: int) -> dict:
    assert_status(response, expected)
    body = response.json()
    assert body["status"] == expected
    assert body["title"]
    return body


def assert_book_shape(book: dict) -> None:
    assert set(book) == BOOK_FIELDS
    assert isinstance(book["id"], int)
    assert isinstance(book["pageCount"], int)
    assert isinstance(book["publishDate"], str)


def assert_same_stored_book(actual: dict, expected: dict) -> None:
    """Compare catalog fields. publishDate is stamped again on every response."""
    for field in ("id", "title", "description", "pageCount", "excerpt"):
        assert actual[field] == expected[field]


def assert_author_shape(author: dict) -> None:
    assert set(author) == AUTHOR_FIELDS
    assert isinstance(author["id"], int)
    assert isinstance(author["idBook"], int)
