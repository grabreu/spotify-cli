from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from typing import Any

import httpx

_API_BASE = "https://api.spotify.com/v1"
_MAX_RETRIES = 5


class PlaylistNotFoundError(RuntimeError):
    pass


class PlaylistAccessError(RuntimeError):
    pass


def fetch_playlist_name(
    client: httpx.Client,
    access_token: str,
    playlist_id: str,
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    response = _get(
        client,
        access_token,
        f"{_API_BASE}/playlists/{playlist_id}",
        playlist_id,
        params={"fields": "name"},
        sleep=sleep,
    )
    name = response.json().get("name")
    if not isinstance(name, str):
        raise PlaylistAccessError(f"Spotify's playlist response for {playlist_id!r} had no name.")
    return name


def iter_playlist_items(
    client: httpx.Client,
    access_token: str,
    playlist_id: str,
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> Iterator[dict[str, Any]]:
    url: str | None = f"{_API_BASE}/playlists/{playlist_id}/tracks"
    params: dict[str, str] | None = {"limit": "50"}

    while url:
        response = _get(client, access_token, url, playlist_id, params=params, sleep=sleep)
        payload = response.json()
        yield from payload.get("items", [])
        url = payload.get("next")
        params = None


def _get(
    client: httpx.Client,
    access_token: str,
    url: str,
    playlist_id: str,
    *,
    params: dict[str, str] | None,
    sleep: Callable[[float], None],
) -> httpx.Response:
    headers = {"Authorization": f"Bearer {access_token}"}

    for _ in range(_MAX_RETRIES):
        response = client.get(url, headers=headers, params=params)

        if response.status_code == 429:
            sleep(float(response.headers.get("Retry-After", "1")))
            continue
        if response.status_code == 404:
            raise PlaylistNotFoundError(f"Playlist not found or not public: {playlist_id}")
        if response.status_code == 401:
            raise PlaylistAccessError("Spotify rejected the access token (401).")
        response.raise_for_status()
        return response

    raise PlaylistAccessError(
        f"Gave up on {playlist_id!r} after {_MAX_RETRIES} retries due to repeated 429s."
    )
