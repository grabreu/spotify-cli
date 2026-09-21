from __future__ import annotations

from collections.abc import Callable
from typing import Any

from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError

from spotify_cli.auth import DEFAULT_CACHE_PATH


class PlaylistNotFoundError(RuntimeError):
    pass


class PlaylistAccessError(RuntimeError):
    pass


def fetch_playlist(spotify: Spotify, playlist_id: str) -> tuple[str, list[dict[str, Any]]]:
    playlist = _call(spotify.playlist, playlist_id, playlist_id)

    if "items" not in playlist:
        raise _ownership_error(playlist_id)

    items: list[dict[str, Any]] = playlist["items"]["items"]
    next_page = playlist["items"]["next"]

    while next_page:
        page = _call(spotify.next, playlist_id, {"next": next_page})
        items.extend(page["items"])
        next_page = page["next"]

    name: str = playlist["name"]
    return name, items


def _call(fn: Callable[..., dict[str, Any]], playlist_id: str, *args: Any) -> dict[str, Any]:
    try:
        return fn(*args)
    except SpotifyOauthError as error:
        raise PlaylistAccessError(f"Spotify login failed: {error}") from error
    except SpotifyException as error:
        raise _translate_error(error, playlist_id) from error


def _translate_error(error: SpotifyException, playlist_id: str) -> RuntimeError:
    if error.http_status == 404:
        return PlaylistNotFoundError(f"Playlist not found: {playlist_id}")
    if error.http_status == 403:
        return _ownership_error(playlist_id)
    if error.http_status == 401:
        return PlaylistAccessError(
            "Spotify rejected the access token (401). Try deleting the cached token at "
            f"{DEFAULT_CACHE_PATH} and running again to log in fresh."
        )
    return PlaylistAccessError(f"Spotify API error for playlist {playlist_id!r}: {error}")


def _ownership_error(playlist_id: str) -> PlaylistAccessError:
    return PlaylistAccessError(
        f"Playlist {playlist_id!r} isn't accessible: Spotify's API only returns track data "
        "for playlists you own or collaborate on, regardless of whether the playlist is public."
    )
