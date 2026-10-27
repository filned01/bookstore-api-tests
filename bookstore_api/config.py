import os
from dataclasses import dataclass


DEFAULT_BASE_URL = "https://fakerestapi.azurewebsites.net"


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        base_url = os.environ.get("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        timeout = float(os.environ.get("API_TIMEOUT_SECONDS", "30"))
        return cls(base_url=base_url, timeout_seconds=timeout)
