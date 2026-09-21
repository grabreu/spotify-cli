from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import typer

from spotify_cli.auth import create_spotify_client
from spotify_cli.client import fetch_playlist
from spotify_cli.export import DEFAULT_COLUMNS, Export, export_csv, export_json
from spotify_cli.playlist import parse_playlist_id
from spotify_cli.settings import load_settings
from spotify_cli.track import map_tracks

app = typer.Typer(
    name="spotify-cli",
    help="Export a Spotify playlist you own or collaborate on as CSV or JSON.",
    add_completion=False,
)


def _ensure_utf8_stdout() -> None:
    # avoids mangled accented characters on legacy Windows console codepages
    encoding = sys.stdout.encoding
    if encoding is not None and encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]


@app.command()
def main(
    playlist: str | None = typer.Argument(
        None, help="Playlist ID, URL, or URI. Prompted for if omitted."
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
) -> None:
    """Export a Spotify playlist you own or collaborate on as CSV or JSON."""
    _ensure_utf8_stdout()
    if playlist is None or format is None:
        typer.echo(
            "playlist and --format are required (the interactive wizard isn't implemented yet).",
            err=True,
        )
        raise typer.Exit(code=1)
    if format not in ("csv", "json"):
        typer.echo(f"--format must be 'csv' or 'json', got {format!r}.", err=True)
        raise typer.Exit(code=1)

    selected_columns = (
        [column.strip() for column in columns.split(",") if column.strip()]
        if columns
        else list(DEFAULT_COLUMNS)
    )

    try:
        playlist_id = parse_playlist_id(playlist)
        settings = load_settings()
        spotify = create_spotify_client(settings)
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
