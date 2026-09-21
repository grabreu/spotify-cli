# spotify-cli

[![CI](https://github.com/grabreu/spotify-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/grabreu/spotify-cli/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/grabreu/spotify-cli?style=flat-square)](LICENSE)

Interactive CLI that exports a public Spotify playlist's tracks as CSV or JSON.

```bash
pip install git+https://github.com/grabreu/spotify-cli
```

## Tech stack

Python · Typer · questionary · Spotify Web API (Client Credentials) · Ruff · mypy · pytest · uv

## Usage

```bash
spotify-cli <playlist> --format csv
spotify-cli <playlist> --format json --columns title,artist,isrc --output tracks.json
```

`<playlist>` accepts a playlist ID, an `open.spotify.com/playlist/...` URL, or a `spotify:playlist:...` URI. `playlist` and `--format` are required for now — see [Configuration](#configuration) below for credentials.

## Features

- **CSV/JSON export** — JSON wraps tracks in playlist metadata (`playlist_id`, `playlist_name`, `exported_at`); CSV is a flat table.
- **Column selection** — `--columns` picks which fields to include (default: `title`, `artist`, `album`, `duration`).
- **Fail-fast errors** — a bad playlist reference, missing/invalid credentials, or a 404/401 from Spotify exits immediately with a clear message and exit code 1; 429s retry automatically, honoring `Retry-After`.

TODO: interactive wizard, prompting for whatever isn't passed via flags — not implemented yet.

See [docs/architecture.md](docs/architecture.md) for the domain model and export flow, and [docs/adr/](docs/adr/) for the reasoning behind these decisions.

## Configuration

Requires a Spotify app's Client ID and Client Secret (Client Credentials flow). Get these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), then copy `.env.example` to `.env` and fill them in, or export `SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET` directly.

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff format .
uv run ruff check .
uv run mypy .
```

## License

Licensed under the [MIT License](LICENSE).
