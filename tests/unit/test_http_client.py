import pytest
import requests

from bookstore_api.config import Settings
from bookstore_api.http_client import HttpClient

pytestmark = pytest.mark.unit


class _Response:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text


class _Session:
    def __init__(self, responses: list[_Response | Exception]) -> None:
        self._responses = list(responses)
        self.calls = 0
        self.headers: dict[str, str] = {}

    def request(self, method: str, url: str, **kwargs):
        self.calls += 1
        self.last_method = method
        self.last_url = url
        self.last_kwargs = kwargs
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self) -> None:
        return None


def test_retries_once_after_a_server_error() -> None:
    session = _Session([_Response(503, "unavailable"), _Response(200, "ok")])
    client = HttpClient(Settings("https://example.test", 5), session=session)

    response = client.request("GET", "/api/v1/Books")

    assert response.status_code == 200
    assert session.calls == 2
    assert session.last_url == "https://example.test/api/v1/Books"


@pytest.mark.parametrize(
    "error",
    [requests.Timeout("timed out"), requests.ConnectionError("connection lost")],
)
def test_retries_a_safe_request_after_a_network_error(error: Exception) -> None:
    session = _Session([error, _Response(200, "ok")])
    client = HttpClient(Settings("https://example.test", 5), session=session)

    response = client.request("GET", "/api/v1/Books")

    assert response.status_code == 200
    assert session.calls == 2


@pytest.mark.parametrize(
    "error",
    [requests.Timeout("timed out"), requests.ConnectionError("connection lost")],
)
def test_raises_after_a_safe_request_exhausts_network_retries(error: Exception) -> None:
    session = _Session([error, error])
    client = HttpClient(Settings("https://example.test", 5), session=session)

    with pytest.raises(type(error)):
        client.request("GET", "/api/v1/Books")

    assert session.calls == 2


def test_returns_the_final_server_error_after_retrying_a_safe_request() -> None:
    session = _Session([_Response(503, "unavailable"), _Response(502, "still unavailable")])
    client = HttpClient(Settings("https://example.test", 5), session=session)

    response = client.request("GET", "/api/v1/Books")

    assert response.status_code == 502
    assert session.calls == 2


def test_does_not_retry_a_client_error() -> None:
    session = _Session([_Response(404, "missing")])
    client = HttpClient(Settings("https://example.test", 5), session=session)

    response = client.request("GET", "/api/v1/Books/0")

    assert response.status_code == 404
    assert session.calls == 1


@pytest.mark.parametrize(
    "failure",
    [
        _Response(503, "unavailable"),
        requests.Timeout("timed out"),
        requests.ConnectionError("connection lost"),
    ],
)
def test_does_not_retry_a_write_request(failure: _Response | Exception) -> None:
    session = _Session([failure])
    client = HttpClient(Settings("https://example.test", 5), session=session)

    if isinstance(failure, Exception):
        with pytest.raises(type(failure)):
            client.request("POST", "/api/v1/Books", json_body={"title": "Example"})
    else:
        response = client.request("POST", "/api/v1/Books", json_body={"title": "Example"})
        assert response.status_code == 503

    assert session.calls == 1
