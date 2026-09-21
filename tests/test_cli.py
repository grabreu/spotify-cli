from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from spotify_cli import cli
from spotify_cli.auth import MissingCredentialsError
from spotify_cli.cli import app

runner = CliRunner()


def _item(**overrides: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "added_at": "2024-03-01T12:00:00Z",
        "is_local": False,
        "track": {
            "type": "track",
            "is_local": False,
            "name": "Song Title",
            "artists": [{"name": "Artist One"}],
            "album": {"name": "Album Name"},
            "duration_ms": 65_000,
            "track_number": 1,
            "external_ids": {"isrc": "USRC17607839"},
            "external_urls": {"spotify": "https://open.spotify.com/track/abc123"},
        },
    }
    item.update(overrides)
    return item


def _iter_items(client: httpx.Client, token: str, playlist_id: str) -> Iterator[dict[str, Any]]:
    return iter([_item()])


@pytest.fixture(autouse=True)
def _mock_spotify(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "load_credentials", lambda: ("id", "secret"))
    monkeypatch.setattr(cli, "fetch_access_token", lambda client, cid, secret: "token")
    monkeypatch.setattr(cli, "fetch_playlist_name", lambda client, token, playlist_id: "Road Trip")
    monkeypatch.setattr(cli, "iter_playlist_items", _iter_items)


def test_help_exits_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_missing_playlist_and_format_exits_with_error() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 1


def test_rejects_invalid_format() -> None:
    result = runner.invoke(app, ["abc123", "--format", "xml"])

    assert result.exit_code == 1
    assert "--format" in result.output


def test_rejects_invalid_playlist_reference() -> None:
    result = runner.invoke(app, ["not a playlist reference!", "--format", "csv"])
    assert result.exit_code == 1


def test_fails_fast_on_missing_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise() -> tuple[str, str]:
        raise MissingCredentialsError("missing")

    monkeypatch.setattr(cli, "load_credentials", _raise)

    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 1


def test_exports_csv_to_stdout() -> None:
    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 0
    assert "title,artist,album,duration" in result.output
    assert "Song Title,Artist One,Album Name,1:05" in result.output


def test_exports_json_to_stdout() -> None:
    result = runner.invoke(app, ["abc123", "--format", "json"])

    assert result.exit_code == 0
    assert '"playlist_name": "Road Trip"' in result.output
    assert '"title": "Song Title"' in result.output


def test_exports_to_output_file(tmp_path: Path) -> None:
    output_file = tmp_path / "export.csv"

    result = runner.invoke(app, ["abc123", "--format", "csv", "--output", str(output_file)])

    assert result.exit_code == 0
    assert "Song Title" in output_file.read_text(encoding="utf-8")


def test_respects_custom_columns() -> None:
    result = runner.invoke(app, ["abc123", "--format", "csv", "--columns", "title,isrc"])

    assert result.exit_code == 0
    assert "title,isrc" in result.output
    assert "Song Title,USRC17607839" in result.output


def test_reports_skipped_items(monkeypatch: pytest.MonkeyPatch) -> None:
    def items(client: httpx.Client, token: str, playlist_id: str) -> Iterator[dict[str, Any]]:
        return iter([_item(), _item(is_local=True)])

    monkeypatch.setattr(cli, "iter_playlist_items", items)

    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 0
    assert "Skipped 1" in result.output
