from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Track:
    title: str
    artist: list[str]
    album: str
    duration: str
    isrc: str | None
    track_number: int
    added_at: datetime
    spotify_url: str


def map_tracks(items: Iterable[dict[str, Any]]) -> tuple[list[Track], int]:
    tracks = []
    skipped = 0
    for item in items:
        if _is_excluded(item):
            skipped += 1
            continue
        tracks.append(_build_track(item))
    return tracks, skipped


def _is_excluded(item: dict[str, Any]) -> bool:
    track = item.get("item")
    if track is None:
        return True
    if item.get("is_local") or track.get("is_local"):
        return True
    if track.get("type") == "episode":
        return True
    return track.get("is_playable") is False


def _build_track(item: dict[str, Any]) -> Track:
    track = item["item"]
    minutes, seconds = divmod(track["duration_ms"] // 1000, 60)
    return Track(
        title=track["name"],
        artist=[artist["name"] for artist in track["artists"]],
        album=track["album"]["name"],
        duration=f"{minutes}:{seconds:02d}",
        isrc=track.get("external_ids", {}).get("isrc"),
        track_number=track["track_number"],
        added_at=datetime.fromisoformat(item["added_at"].replace("Z", "+00:00")),
        spotify_url=track["external_urls"]["spotify"],
    )
