from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime

import pytest

from spotify_cli.export import Export, export_csv, export_json
from spotify_cli.track import Track


def _track(
    *,
    title: str = "Song Title",
    artist: list[str] | None = None,
    album: str = "Album Name",
    duration: str = "1:05",
    isrc: str | None = "USRC17607839",
    track_number: int = 3,
    added_at: datetime | None = None,
    spotify_url: str = "https://open.spotify.com/track/abc123",
) -> Track:
    return Track(
        title=title,
        artist=artist if artist is not None else ["Artist One", "Artist Two"],
        album=album,
        duration=duration,
        isrc=isrc,
        track_number=track_number,
        added_at=added_at if added_at is not None else datetime(2024, 3, 1, 12, 0, 0, tzinfo=UTC),
        spotify_url=spotify_url,
    )


def _export(*tracks: Track) -> Export:
    return Export(
        playlist_id="playlist123",
        playlist_name="Road Trip",
        exported_at=datetime(2024, 3, 2, 8, 30, 0, tzinfo=UTC),
        tracks=list(tracks),
    )


def test_export_json_default_columns() -> None:
    payload = json.loads(export_json(_export(_track())))

    assert payload["playlist_id"] == "playlist123"
    assert payload["playlist_name"] == "Road Trip"
    assert payload["exported_at"] == "2024-03-02T08:30:00+00:00"
    assert payload["tracks"] == [
        {
            "title": "Song Title",
            "artist": ["Artist One", "Artist Two"],
            "album": "Album Name",
            "duration": "1:05",
        }
    ]


def test_export_json_custom_columns() -> None:
    payload = json.loads(export_json(_export(_track()), columns=["isrc", "added_at"]))

    assert payload["tracks"] == [{"isrc": "USRC17607839", "added_at": "2024-03-01T12:00:00+00:00"}]


def test_export_json_rejects_unknown_column() -> None:
    with pytest.raises(ValueError, match="bogus"):
        export_json(_export(_track()), columns=["bogus"])


def test_export_csv_default_columns_joins_artist() -> None:
    csv_text = export_csv(_export(_track()))
    rows = list(csv.reader(io.StringIO(csv_text)))

    assert rows[0] == ["title", "artist", "album", "duration"]
    assert rows[1] == ["Song Title", "Artist One, Artist Two", "Album Name", "1:05"]


def test_export_csv_renders_missing_isrc_as_empty() -> None:
    csv_text = export_csv(_export(_track(isrc=None)), columns=["title", "isrc"])
    rows = list(csv.reader(io.StringIO(csv_text)))

    assert rows[1] == ["Song Title", ""]


def test_export_csv_quotes_values_with_commas() -> None:
    csv_text = export_csv(_export(_track(title="Comma, Title")), columns=["title"])
    rows = list(csv.reader(io.StringIO(csv_text)))

    assert rows[1] == ["Comma, Title"]


def test_export_csv_rejects_unknown_column() -> None:
    with pytest.raises(ValueError, match="bogus"):
        export_csv(_export(), columns=["bogus"])
