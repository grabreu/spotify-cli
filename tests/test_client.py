from __future__ import annotations

from typing import Any

import pytest
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError

from spotify_cli.client import PlaylistAccessError, PlaylistNotFoundError, fetch_playlist


class _FakeSpotify:
    def __init__(self, pages: list[dict[str, Any]]) -> None:
        self._pages = pages
        self.next_calls: list[dict[str, Any]] = []

    def playlist(self, playlist_id: str) -> dict[str, Any]:
        return self._pages[0]

    def next(self, previous: dict[str, Any]) -> dict[str, Any]:
        self.next_calls.append(previous)
        return self._pages[len(self.next_calls)]


class _RaisingSpotify:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def playlist(self, playlist_id: str) -> dict[str, Any]:
        raise self._error

    def next(self, previous: dict[str, Any]) -> dict[str, Any]:
        raise self._error


def test_fetch_playlist_returns_name_and_items_for_single_page() -> None:
    spotify = _FakeSpotify(
        [{"name": "Road Trip", "items": {"items": [{"track": {"name": "a"}}], "next": None}}]
    )

    name, items = fetch_playlist(spotify, "abc123")

    assert name == "Road Trip"
    assert items == [{"track": {"name": "a"}}]


def test_fetch_playlist_follows_pagination() -> None:
    spotify = _FakeSpotify(
        [
            {
                "name": "Road Trip",
                "items": {"items": [{"track": {"name": "a"}}], "next": "page2"},
            },
            {"items": [{"track": {"name": "b"}}], "next": None},
        ]
    )

    name, items = fetch_playlist(spotify, "abc123")

    assert name == "Road Trip"
    assert [item["track"]["name"] for item in items] == ["a", "b"]
    assert spotify.next_calls == [{"next": "page2"}]


def test_fetch_playlist_raises_not_found_on_404() -> None:
    spotify = _RaisingSpotify(SpotifyException(404, -1, "Not Found"))

    with pytest.raises(PlaylistNotFoundError):
        fetch_playlist(spotify, "missing")


def test_fetch_playlist_raises_ownership_error_on_403() -> None:
    spotify = _RaisingSpotify(SpotifyException(403, -1, "denied"))

    with pytest.raises(PlaylistAccessError, match="own or collaborate on"):
        fetch_playlist(spotify, "abc123")


def test_fetch_playlist_raises_ownership_error_when_items_key_missing() -> None:
    spotify = _FakeSpotify([{"name": "Someone Else's Playlist"}])

    with pytest.raises(PlaylistAccessError, match="own or collaborate on"):
        fetch_playlist(spotify, "abc123")


def test_fetch_playlist_raises_access_error_on_401() -> None:
    spotify = _RaisingSpotify(SpotifyException(401, -1, "denied"))

    with pytest.raises(PlaylistAccessError, match="cached token"):
        fetch_playlist(spotify, "abc123")


def test_fetch_playlist_raises_access_error_on_other_status() -> None:
    spotify = _RaisingSpotify(SpotifyException(500, -1, "server error"))

    with pytest.raises(PlaylistAccessError):
        fetch_playlist(spotify, "abc123")


def test_fetch_playlist_translates_oauth_error() -> None:
    spotify = _RaisingSpotify(SpotifyOauthError("login failed"))

    with pytest.raises(PlaylistAccessError):
        fetch_playlist(spotify, "abc123")
