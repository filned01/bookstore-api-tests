import pytest

from bookstore_api.http_client import HttpClient
from bookstore_api.payloads import book_payload
from bookstore_api.resources import BooksApi
from tests.assertions import assert_problem, assert_status

pytestmark = pytest.mark.books


def test_create_book_echoes_the_submitted_payload(books_api: BooksApi) -> None:
    payload = book_payload()
    response = books_api.create(payload)
    assert_status(response, 200)
    assert response.json() == payload


def test_created_book_is_not_added_to_the_catalog(books_api: BooksApi) -> None:
    payload = book_payload(id=9001)
    created = books_api.create(payload)
    assert_status(created, 200)

    fetched = books_api.get_by_id(payload["id"])
    body = assert_problem(fetched, 404)
    assert body["title"] == "Not Found"


def test_empty_book_object_is_accepted_with_defaults(books_api: BooksApi) -> None:
    response = books_api.create({})
    assert_status(response, 200)
    body = response.json()
    assert body["id"] == 0
    assert body["title"] is None
    assert body["description"] is None
    assert body["pageCount"] == 0
    assert body["excerpt"] is None
    assert body["publishDate"] == "0001-01-01T00:00:00"


def test_create_book_rejects_wrong_field_types(books_api: BooksApi) -> None:
    response = books_api.create({"title": 12, "pageCount": "lots"})
    body = assert_problem(response, 400)
    assert any(key.startswith("$.") for key in body["errors"])


def test_create_book_rejects_malformed_json(http_client: HttpClient) -> None:
    response = http_client.request("POST", "/api/v1/Books", raw_body="not-json")
    body = assert_problem(response, 400)
    assert body["errors"]["$"]
