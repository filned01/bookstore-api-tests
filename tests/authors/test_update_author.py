import pytest

from bookstore_api.payloads import author_payload
from bookstore_api.resources import AuthorsApi
from tests.assertions import assert_problem, assert_status

pytestmark = pytest.mark.authors


def test_update_author_echoes_the_payload_and_leaves_the_stored_record(authors_api: AuthorsApi) -> None:
    original = authors_api.get_by_id(1).json()
    payload = author_payload(firstName="Fake", lastName="Person")

    response = authors_api.update(1, payload)
    assert_status(response, 200)
    assert response.json() == payload

    stored = authors_api.get_by_id(1)
    assert_status(stored, 200)
    assert stored.json() == original


def test_update_missing_author_still_echoes_the_payload(authors_api: AuthorsApi) -> None:
    payload = author_payload(id=9002)
    response = authors_api.update(99999, payload)
    assert_status(response, 200)
    assert response.json() == payload


def test_update_author_rejects_a_non_numeric_id(authors_api: AuthorsApi) -> None:
    response = authors_api.update("abc", author_payload())
    body = assert_problem(response, 400)
    assert "not valid" in body["errors"]["id"][0]
