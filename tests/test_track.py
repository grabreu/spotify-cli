from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from spotify_cli.track import map_tracks


def _track_item(**overrides: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "added_at": "2024-03-01T12:00:00Z",
        "is_local": False,
        "item": {
            "type": "track",
            "is_local": False,
            "is_playable": True,
            "name": "Song Title",
            "artists": [{"name": "Artist One"}, {"name": "Artist Two"}],
            "album": {"name": "Album Name"},
            "duration_ms": 65000,
            "track_number": 3,
            "external_ids": {"isrc": "USRC17607839"},
            "external_urls": {"spotify": "https://open.spotify.com/track/abc123"},
        },
    }
    item.update(overrides)
    return item


def test_map_tracks_builds_track_from_item() -> None:
    tracks, skipped = map_tracks([_track_item()])

    assert skipped == 0
    assert len(tracks) == 1
    track = tracks[0]
    assert track.title == "Song Title"
    assert track.artist == ["Artist One", "Artist Two"]
    assert track.album == "Album Name"
    assert track.duration == "1:05"
    assert track.isrc == "USRC17607839"
    assert track.track_number == 3
    assert track.added_at == datetime(2024, 3, 1, 12, 0, 0, tzinfo=UTC)
    assert track.spotify_url == "https://open.spotify.com/track/abc123"


def test_map_tracks_formats_duration_under_ten_seconds() -> None:
    item = _track_item()
    item["item"]["duration_ms"] = 3_000

    tracks, _ = map_tracks([item])

    assert tracks[0].duration == "0:03"


def test_map_tracks_handles_missing_isrc() -> None:
    item = _track_item()
    del item["item"]["external_ids"]

    tracks, _ = map_tracks([item])

    assert tracks[0].isrc is None


def test_map_tracks_skips_local_file() -> None:
    item = _track_item(is_local=True)

    tracks, skipped = map_tracks([item])

    assert tracks == []
    assert skipped == 1


def test_map_tracks_skips_episode() -> None:
    item = _track_item()
    item["item"]["type"] = "episode"

    tracks, skipped = map_tracks([item])

    assert tracks == []
    assert skipped == 1


def test_map_tracks_skips_removed_track() -> None:
    item = _track_item(item=None)

    tracks, skipped = map_tracks([item])

    assert tracks == []
    assert skipped == 1


def test_map_tracks_skips_unplayable_track() -> None:
    item = _track_item()
    item["item"]["is_playable"] = False

    tracks, skipped = map_tracks([item])

    assert tracks == []
    assert skipped == 1


def test_map_tracks_counts_mixed_items() -> None:
    items = [_track_item(), _track_item(is_local=True), _track_item(item=None)]

    tracks, skipped = map_tracks(items)

    assert len(tracks) == 1
    assert skipped == 2
