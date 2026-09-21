"""Typer CLI entry point for spotify-cli."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="spotify-cli",
    help="Export a public Spotify playlist's tracks as CSV or JSON.",
    add_completion=False,
)


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
    """Export a public Spotify playlist's tracks as CSV or JSON."""
    raise NotImplementedError
