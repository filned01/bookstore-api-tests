import pytest

from bookstore_api.payloads import author_payload
from bookstore_api.resources import AuthorsApi
from tests.assertions import assert_problem, assert_status

pytestmark = pytest.mark.authors


def test_create_author_echoes_the_submitted_payload(authors_api: AuthorsApi) -> None:
    payload = author_payload()
    response = authors_api.create(payload)
    assert_status(response, 200)
    assert response.json() == payload


def test_created_author_is_not_added_to_the_catalog(authors_api: AuthorsApi) -> None:
    payload = author_payload(id=9001)
    created = authors_api.create(payload)
    assert_status(created, 200)

    fetched = authors_api.get_by_id(payload["id"])
    body = assert_problem(fetched, 404)
    assert body["title"] == "Not Found"


def test_empty_author_object_is_accepted_with_defaults(authors_api: AuthorsApi) -> None:
    response = authors_api.create({})
    assert_status(response, 200)
    body = response.json()
    assert body["id"] == 0
    assert body["idBook"] == 0
    assert body["firstName"] is None
    assert body["lastName"] is None
