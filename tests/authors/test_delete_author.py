import pytest

from bookstore_api.resources import AuthorsApi
from tests.assertions import assert_problem, assert_status

pytestmark = pytest.mark.authors


def test_delete_author_returns_no_content_and_leaves_the_catalog(authors_api: AuthorsApi) -> None:
    original = authors_api.get_by_id(1).json()

    response = authors_api.delete(1)
    assert_status(response, 200)
    assert response.text == ""

    stored = authors_api.get_by_id(1)
    assert_status(stored, 200)
    assert stored.json() == original


def test_delete_missing_author_returns_success(authors_api: AuthorsApi) -> None:
    response = authors_api.delete(99999)
    assert_status(response, 200)
    assert response.text == ""


def test_delete_author_rejects_a_non_numeric_id(authors_api: AuthorsApi) -> None:
    response = authors_api.delete("abc")
    body = assert_problem(response, 400)
    assert "not valid" in body["errors"]["id"][0]
