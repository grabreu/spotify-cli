from __future__ import annotations

import httpx
import pytest

from spotify_cli.client import (
    PlaylistAccessError,
    PlaylistNotFoundError,
    fetch_playlist_name,
    iter_playlist_items,
)


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_fetch_playlist_name_returns_name() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/playlists/abc123"
        assert request.headers["Authorization"] == "Bearer the-token"
        return httpx.Response(200, json={"name": "Road Trip"})

    with _client(httpx.MockTransport(handler)) as client:
        name = fetch_playlist_name(client, "the-token", "abc123")

    assert name == "Road Trip"


def test_fetch_playlist_name_raises_on_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": {"message": "Not found"}})

    with _client(httpx.MockTransport(handler)) as client, pytest.raises(PlaylistNotFoundError):
        fetch_playlist_name(client, "the-token", "missing")


def test_fetch_playlist_name_raises_on_401() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "Bad token"}})

    with _client(httpx.MockTransport(handler)) as client, pytest.raises(PlaylistAccessError):
        fetch_playlist_name(client, "bad-token", "abc123")


def test_iter_playlist_items_follows_pagination() -> None:
    page_two_url = "https://api.spotify.com/v1/playlists/abc123/tracks?offset=50"

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == page_two_url:
            return httpx.Response(200, json={"items": [{"track": {"name": "b"}}], "next": None})
        return httpx.Response(200, json={"items": [{"track": {"name": "a"}}], "next": page_two_url})

    with _client(httpx.MockTransport(handler)) as client:
        items = list(iter_playlist_items(client, "the-token", "abc123"))

    assert [item["track"]["name"] for item in items] == ["a", "b"]


def test_get_retries_on_429_honoring_retry_after() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return httpx.Response(200, json={"name": "Road Trip"})

    sleeps: list[float] = []

    with _client(httpx.MockTransport(handler)) as client:
        name = fetch_playlist_name(client, "the-token", "abc123", sleep=sleeps.append)

    assert name == "Road Trip"
    assert sleeps == [2.0]


def test_get_gives_up_after_max_retries() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "0"})

    sleeps: list[float] = []

    with (
        _client(httpx.MockTransport(handler)) as client,
        pytest.raises(PlaylistAccessError),
    ):
        fetch_playlist_name(client, "the-token", "abc123", sleep=sleeps.append)

    assert len(sleeps) == 5
