import pytest

from bookstore_api.resources import BooksApi
from tests.assertions import assert_book_shape, assert_status

pytestmark = pytest.mark.books


def test_list_books_returns_the_catalog(books_api: BooksApi) -> None:
    response = books_api.list_all()
    assert_status(response, 200)
    books = response.json()
    assert len(books) == 200
    assert len({book["id"] for book in books}) == 200
    for book in books:
        assert_book_shape(book)
    assert books[0]["id"] == 1
    assert books[0]["title"] == "Book 1"
    assert books[0]["pageCount"] == 100
