import pytest

from bookstore_api.resources import AuthorsApi
from tests.assertions import assert_author_shape, assert_problem, assert_status

pytestmark = pytest.mark.authors


def test_list_authors_returns_a_catalog(authors_api: AuthorsApi) -> None:
    response = authors_api.list_all()
    assert_status(response, 200)
    authors = response.json()
    assert authors
    assert len({author["id"] for author in authors}) == len(authors)
    for author in authors:
        assert_author_shape(author)


def test_get_author_by_id(authors_api: AuthorsApi) -> None:
    response = authors_api.get_by_id(1)
    assert_status(response, 200)
    author = response.json()
    assert_author_shape(author)
    assert author["id"] == 1
    assert author["idBook"] == 1
    assert author["firstName"] == "First Name 1"
    assert author["lastName"] == "Last Name 1"


@pytest.mark.parametrize("author_id", [0, 99999])
def test_get_missing_author_returns_not_found(authors_api: AuthorsApi, author_id: int) -> None:
    response = authors_api.get_by_id(author_id)
    body = assert_problem(response, 404)
    assert body["title"] == "Not Found"


def test_get_author_rejects_a_non_numeric_id(authors_api: AuthorsApi) -> None:
    response = authors_api.get_by_id("abc")
    body = assert_problem(response, 400)
    assert "not valid" in body["errors"]["id"][0]
