from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from spotify_cli import cli
from spotify_cli.cli import app
from spotify_cli.export import DEFAULT_COLUMNS
from spotify_cli.settings import MissingCredentialsError, Settings

runner = CliRunner()


def _item(**overrides: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "added_at": "2024-03-01T12:00:00Z",
        "is_local": False,
        "item": {
            "type": "track",
            "is_local": False,
            "is_playable": True,
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


@pytest.fixture(autouse=True)
def _mock_spotify(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cli, "load_settings", lambda: Settings(_env_file=None, spotify_client_id="id")
    )
    monkeypatch.setattr(cli, "create_spotify_client", lambda settings: object())
    monkeypatch.setattr(
        cli, "fetch_playlist", lambda spotify, playlist_id: ("Road Trip", [_item()])
    )


@pytest.fixture(autouse=True)
def _mock_wizard_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_prompt_playlist", lambda: None)
    monkeypatch.setattr(cli, "_prompt_format", lambda: None)
    monkeypatch.setattr(cli, "_prompt_columns", lambda: list(DEFAULT_COLUMNS))
    monkeypatch.setattr(cli, "_prompt_output", lambda: None)


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
    def _raise() -> Settings:
        raise MissingCredentialsError("missing")

    monkeypatch.setattr(cli, "load_settings", _raise)

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
    monkeypatch.setattr(
        cli,
        "fetch_playlist",
        lambda spotify, playlist_id: ("Road Trip", [_item(), _item(is_local=True)]),
    )

    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 0
    assert "Skipped 1" in result.output


def test_wizard_prompts_for_missing_playlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_prompt_playlist", lambda: "abc123")

    result = runner.invoke(app, ["--format", "csv"])

    assert result.exit_code == 0
    assert "Song Title" in result.output


def test_wizard_cancelled_playlist_prompt_exits_with_error() -> None:
    result = runner.invoke(app, ["--format", "csv"])

    assert result.exit_code == 1
    assert "playlist" in result.output.lower()


def test_wizard_prompts_for_missing_format(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_prompt_format", lambda: "json")

    result = runner.invoke(app, ["abc123"])

    assert result.exit_code == 0
    assert '"title": "Song Title"' in result.output


def test_wizard_prompts_for_missing_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_prompt_columns", lambda: ["title", "isrc"])

    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 0
    assert "title,isrc" in result.output
    assert "Song Title,USRC17607839" in result.output


def test_wizard_empty_columns_selection_exits_with_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_prompt_columns", lambda: [])

    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 1
    assert "column" in result.output.lower()


def test_wizard_prompts_for_output_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    output_file = tmp_path / "export.csv"
    monkeypatch.setattr(cli, "_prompt_output", lambda: str(output_file))

    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 0
    assert "Song Title" in output_file.read_text(encoding="utf-8")


def test_wizard_output_prompt_declined_prints_to_stdout() -> None:
    result = runner.invoke(app, ["abc123", "--format", "csv"])

    assert result.exit_code == 0
    assert "Song Title" in result.output


def test_flags_skip_all_wizard_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _fail() -> str:
        raise AssertionError("should not prompt")

    monkeypatch.setattr(cli, "_prompt_playlist", _fail)
    monkeypatch.setattr(cli, "_prompt_format", _fail)
    monkeypatch.setattr(cli, "_prompt_columns", _fail)
    monkeypatch.setattr(cli, "_prompt_output", _fail)
    output_file = tmp_path / "export.csv"

    result = runner.invoke(
        app, ["abc123", "--format", "csv", "--columns", "title", "--output", str(output_file)]
    )

    assert result.exit_code == 0
    assert "Song Title" in output_file.read_text(encoding="utf-8")
