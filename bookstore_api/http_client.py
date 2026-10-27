import logging
from typing import Any

import requests

from bookstore_api.config import Settings

logger = logging.getLogger("bookstore_api")


class HttpClient:
    """Sends HTTP calls and retries once when the server or the network fails."""

    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self._settings = settings
        self._session = session or requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def close(self) -> None:
        self._session.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        raw_body: str | None = None,
    ) -> requests.Response:
        if json_body is not None and raw_body is not None:
            raise ValueError("Pass json_body or raw_body, not both.")

        url = f"{self._settings.base_url}{path}"
        max_attempts = 2 if method.upper() in {"GET", "HEAD", "OPTIONS"} else 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._send(method, url, json_body, raw_body)
            except (requests.Timeout, requests.ConnectionError) as error:
                logger.warning("%s %s attempt %s failed: %s", method, url, attempt, error)
                if attempt == max_attempts:
                    raise
                continue

            if response.status_code < 500 or attempt == max_attempts:
                self._log(method, url, response)
                return response

            logger.warning(
                "%s %s attempt %s returned %s; retrying once",
                method,
                url,
                attempt,
                response.status_code,
            )

        raise RuntimeError("HTTP request loop exited without a response.")

    def _send(
        self,
        method: str,
        url: str,
        json_body: dict[str, Any] | None,
        raw_body: str | None,
    ) -> requests.Response:
        kwargs: dict[str, Any] = {"timeout": self._settings.timeout_seconds}
        if json_body is not None:
            kwargs["json"] = json_body
        elif raw_body is not None:
            kwargs["data"] = raw_body
            kwargs["headers"] = {"Content-Type": "application/json"}
        return self._session.request(method, url, **kwargs)

    @staticmethod
    def _log(method: str, url: str, response: requests.Response) -> None:
        snippet = response.text[:300].replace("\n", " ")
        logger.info("%s %s -> %s %s", method, url, response.status_code, snippet)
