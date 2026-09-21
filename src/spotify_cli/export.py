from __future__ import annotations

import csv
import io
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

from spotify_cli.track import Track

_FIELD_GETTERS: dict[str, Callable[[Track], object]] = {
    "title": lambda track: track.title,
    "artist": lambda track: track.artist,
    "album": lambda track: track.album,
    "duration": lambda track: track.duration,
    "isrc": lambda track: track.isrc,
    "track_number": lambda track: track.track_number,
    "added_at": lambda track: track.added_at.isoformat(),
    "spotify_url": lambda track: track.spotify_url,
}

ALL_COLUMNS = tuple(_FIELD_GETTERS)
DEFAULT_COLUMNS = ("title", "artist", "album", "duration")


@dataclass(frozen=True)
class Export:
    playlist_id: str
    playlist_name: str
    exported_at: datetime
    tracks: list[Track]


def export_json(export: Export, columns: Sequence[str] = DEFAULT_COLUMNS) -> str:
    _validate_columns(columns)
    payload = {
        "playlist_id": export.playlist_id,
        "playlist_name": export.playlist_name,
        "exported_at": export.exported_at.isoformat(),
        "tracks": [
            {column: _FIELD_GETTERS[column](track) for column in columns} for track in export.tracks
        ],
    }
    return json.dumps(payload, indent=2)


def export_csv(export: Export, columns: Sequence[str] = DEFAULT_COLUMNS) -> str:
    _validate_columns(columns)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    for track in export.tracks:
        writer.writerow([_csv_field(track, column) for column in columns])
    return buffer.getvalue()


def _validate_columns(columns: Sequence[str]) -> None:
    unknown = [column for column in columns if column not in _FIELD_GETTERS]
    if unknown:
        raise ValueError(f"Unknown column(s): {', '.join(unknown)}")


def _csv_field(track: Track, column: str) -> str:
    value = _FIELD_GETTERS[column](track)
    if isinstance(value, list):
        return ", ".join(value)
    if value is None:
        return ""
    return str(value)
