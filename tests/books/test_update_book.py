import pytest

from bookstore_api.payloads import book_payload
from bookstore_api.resources import BooksApi
from tests.assertions import assert_problem, assert_same_stored_book, assert_status

pytestmark = pytest.mark.books


def test_update_book_echoes_the_submitted_payload(books_api: BooksApi) -> None:
    original = books_api.get_by_id(1).json()
    payload = book_payload(title="Synthetic Fixture Book Revised", pageCount=256)

    response = books_api.update(1, payload)
    assert_status(response, 200)
    assert response.json() == payload

    stored = books_api.get_by_id(1)
    assert_status(stored, 200)
    assert_same_stored_book(stored.json(), original)


def test_update_missing_book_still_echoes_the_payload(books_api: BooksApi) -> None:
    payload = book_payload(id=9002)
    response = books_api.update(99999, payload)
    assert_status(response, 200)
    assert response.json() == payload


def test_update_book_rejects_a_non_numeric_id(books_api: BooksApi) -> None:
    response = books_api.update("abc", book_payload())
    body = assert_problem(response, 400)
    assert "not valid" in body["errors"]["id"][0]


def test_update_with_an_empty_object_returns_defaults(books_api: BooksApi) -> None:
    response = books_api.update(1, {})
    assert_status(response, 200)
    body = response.json()
    assert body["id"] == 0
    assert body["title"] is None
    assert body["pageCount"] == 0
    assert body["publishDate"] == "0001-01-01T00:00:00"
