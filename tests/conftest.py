import pytest

from bookstore_api.config import Settings
from bookstore_api.http_client import HttpClient
from bookstore_api.resources import AuthorsApi, BooksApi


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def http_client(settings: Settings):
    client = HttpClient(settings)
    yield client
    client.close()


@pytest.fixture
def books_api(http_client: HttpClient) -> BooksApi:
    return BooksApi(http_client)


@pytest.fixture
def authors_api(http_client: HttpClient) -> AuthorsApi:
    return AuthorsApi(http_client)
