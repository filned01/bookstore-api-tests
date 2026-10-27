import pytest

from bookstore_api.resources import BooksApi
from tests.assertions import assert_problem, assert_same_stored_book, assert_status

pytestmark = pytest.mark.books


def test_delete_book_returns_no_content_and_leaves_the_catalog(books_api: BooksApi) -> None:
    original = books_api.get_by_id(1).json()

    response = books_api.delete(1)
    assert_status(response, 200)
    assert response.text == ""

    stored = books_api.get_by_id(1)
    assert_status(stored, 200)
    assert_same_stored_book(stored.json(), original)


def test_delete_missing_book_returns_success(books_api: BooksApi) -> None:
    response = books_api.delete(99999)
    assert_status(response, 200)
    assert response.text == ""


def test_delete_book_rejects_a_non_numeric_id(books_api: BooksApi) -> None:
    response = books_api.delete("abc")
    body = assert_problem(response, 400)
    assert "not valid" in body["errors"]["id"][0]
