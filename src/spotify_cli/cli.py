from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import questionary
import typer

from spotify_cli.auth import create_spotify_client
from spotify_cli.client import fetch_liked_songs, fetch_playlist
from spotify_cli.export import ALL_COLUMNS, DEFAULT_COLUMNS, Export, export_csv, export_json
from spotify_cli.playlist import parse_playlist_id
from spotify_cli.settings import load_settings
from spotify_cli.track import map_tracks

_LIKED_SONGS_ID = "liked_songs"
_LIKED_SONGS_NAME = "Liked Songs"

app = typer.Typer(
    name="spotify-cli",
    help="Export a Spotify playlist you own/collaborate on, or your Liked Songs, as CSV or JSON.",
    add_completion=False,
)


def _ensure_utf8_stdout() -> None:
    # avoids mangled accented characters on legacy Windows console codepages
    encoding = sys.stdout.encoding
    if encoding is not None and encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]


def _prompt_source() -> str | None:
    choice = questionary.select(
        "What do you want to export?",
        choices=[
            questionary.Choice("A playlist", value="playlist"),
            questionary.Choice("My Liked Songs", value="liked"),
        ],
    ).ask()
    return cast(str | None, choice)


def _prompt_playlist() -> str | None:
    return cast(str | None, questionary.text("Playlist ID, URL, or URI:").ask())


def _prompt_format() -> str | None:
    return cast(str | None, questionary.select("Export format:", choices=["csv", "json"]).ask())


def _prompt_columns() -> list[str] | None:
    choices = [
        questionary.Choice(column, checked=column in DEFAULT_COLUMNS) for column in ALL_COLUMNS
    ]
    return cast(
        "list[str] | None", questionary.checkbox("Columns to include:", choices=choices).ask()
    )


def _prompt_output() -> str | None:
    if not questionary.confirm("Save to a file?", default=False).ask():
        return None
    return cast(str | None, questionary.text("Output file path:").ask())


@app.command()
def main(
    playlist: str | None = typer.Argument(
        None, help="Playlist ID, URL, or URI. Prompted for if omitted (and --liked isn't set)."
    ),
    format: str | None = typer.Option(
        None, "--format", help="Export format: csv or json. Prompted for if omitted."
    ),
    columns: str | None = typer.Option(
        None, "--columns", help="Comma-separated columns to include. Prompted for if omitted."
    ),
    output: str | None = typer.Option(
        None, "--output", help="File to write to. Prompted for if omitted (default: stdout)."
    ),
    liked: bool = typer.Option(
        False, "--liked", help="Export your Liked Songs instead of a playlist."
    ),
) -> None:
    """Export a Spotify playlist you own/collaborate on, or your Liked Songs, as CSV or JSON."""
    _ensure_utf8_stdout()

    if liked and playlist is not None:
        typer.echo("Pass either a playlist or --liked, not both.", err=True)
        raise typer.Exit(code=1)

    if not liked and playlist is None:
        source = _prompt_source()
        if source == "liked":
            liked = True
        elif source == "playlist":
            playlist = _prompt_playlist()

    if not liked and not playlist:
        typer.echo("A playlist ID, URL, or URI is required.", err=True)
        raise typer.Exit(code=1)

    if format is None:
        format = _prompt_format()
    if format not in ("csv", "json"):
        typer.echo(f"--format must be 'csv' or 'json', got {format!r}.", err=True)
        raise typer.Exit(code=1)

    selected_columns: list[str] | None
    if columns is not None:
        selected_columns = [column.strip() for column in columns.split(",") if column.strip()]
    else:
        selected_columns = _prompt_columns()
    if not selected_columns:
        typer.echo("At least one column is required.", err=True)
        raise typer.Exit(code=1)

    if output is None:
        output = _prompt_output()

    try:
        settings = load_settings()
        spotify = create_spotify_client(settings)
        if liked:
            playlist_id = _LIKED_SONGS_ID
            playlist_name = _LIKED_SONGS_NAME
            items = fetch_liked_songs(spotify)
        else:
            if not playlist:
                typer.echo("A playlist ID, URL, or URI is required.", err=True)
                raise typer.Exit(code=1)
            playlist_id = parse_playlist_id(playlist)
            playlist_name, items = fetch_playlist(spotify, playlist_id)
    except (ValueError, RuntimeError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    tracks, skipped = map_tracks(items)
    if skipped:
        typer.echo(
            f"Skipped {skipped} local file(s)/podcast episode(s)/unavailable track(s).",
            err=True,
        )

    export = Export(
        playlist_id=playlist_id,
        playlist_name=playlist_name,
        exported_at=datetime.now(UTC),
        tracks=tracks,
    )

    try:
        content = (
            export_csv(export, columns=selected_columns)
            if format == "csv"
            else export_json(export, columns=selected_columns)
        )
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        typer.echo(content)
