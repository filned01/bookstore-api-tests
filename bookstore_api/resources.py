from typing import Any

import requests

from bookstore_api.http_client import HttpClient


class ResourceApi:
    """CRUD calls for one FakeRestAPI collection, such as Books or Authors."""

    def __init__(self, client: HttpClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    def list_all(self) -> requests.Response:
        return self._client.request("GET", f"/api/v1/{self._collection}")

    def get_by_id(self, item_id: int | str) -> requests.Response:
        return self._client.request("GET", f"/api/v1/{self._collection}/{item_id}")

    def create(self, payload: dict[str, Any]) -> requests.Response:
        return self._client.request("POST", f"/api/v1/{self._collection}", json_body=payload)

    def update(self, item_id: int | str, payload: dict[str, Any]) -> requests.Response:
        return self._client.request("PUT", f"/api/v1/{self._collection}/{item_id}", json_body=payload)

    def delete(self, item_id: int | str) -> requests.Response:
        return self._client.request("DELETE", f"/api/v1/{self._collection}/{item_id}")


class BooksApi(ResourceApi):
    def __init__(self, client: HttpClient) -> None:
        super().__init__(client, "Books")


class AuthorsApi(ResourceApi):
    def __init__(self, client: HttpClient) -> None:
        super().__init__(client, "Authors")
