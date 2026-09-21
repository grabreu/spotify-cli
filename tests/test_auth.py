from __future__ import annotations

import httpx
import pytest

from spotify_cli import auth
from spotify_cli.auth import (
    MissingCredentialsError,
    SpotifyAuthError,
    fetch_access_token,
    load_credentials,
)


@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    monkeypatch.setattr(auth, "load_dotenv", lambda: None)


def test_load_credentials_reads_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "the-id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "the-secret")

    assert load_credentials() == ("the-id", "the-secret")


def test_load_credentials_missing_raises() -> None:
    with pytest.raises(MissingCredentialsError):
        load_credentials()


def test_fetch_access_token_returns_token_on_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/token"
        assert request.headers["Authorization"].startswith("Basic ")
        return httpx.Response(200, json={"access_token": "the-token", "token_type": "Bearer"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        token = fetch_access_token(client, "id", "secret")

    assert token == "the-token"


def test_fetch_access_token_raises_on_401() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid_client"})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(SpotifyAuthError),
    ):
        fetch_access_token(client, "bad-id", "bad-secret")


def test_fetch_access_token_raises_when_access_token_missing() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"token_type": "Bearer"})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(SpotifyAuthError),
    ):
        fetch_access_token(client, "id", "secret")
