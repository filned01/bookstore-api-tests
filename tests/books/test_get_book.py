import pytest

from bookstore_api.resources import BooksApi
from tests.assertions import assert_book_shape, assert_problem, assert_same_stored_book, assert_status

pytestmark = pytest.mark.books


def test_get_book_by_id(books_api: BooksApi) -> None:
    listed = books_api.list_all().json()
    book_id = listed[0]["id"]

    response = books_api.get_by_id(book_id)
    assert_status(response, 200)
    book = response.json()
    assert_book_shape(book)
    assert_same_stored_book(book, listed[0])


def test_get_last_catalog_book(books_api: BooksApi) -> None:
    response = books_api.get_by_id(200)
    assert_status(response, 200)
    book = response.json()
    assert book["id"] == 200
    assert book["title"] == "Book 200"
    assert book["pageCount"] == 20000


@pytest.mark.parametrize("book_id", [0, -1, 201])
def test_get_missing_book_returns_not_found(books_api: BooksApi, book_id: int) -> None:
    response = books_api.get_by_id(book_id)
    body = assert_problem(response, 404)
    assert body["title"] == "Not Found"


def test_get_book_rejects_a_non_numeric_id(books_api: BooksApi) -> None:
    response = books_api.get_by_id("abc")
    body = assert_problem(response, 400)
    assert "not valid" in body["errors"]["id"][0]
