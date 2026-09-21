# spotify-cli

[![CI](https://github.com/grabreu/spotify-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/grabreu/spotify-cli/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/grabreu/spotify-cli?style=flat-square)](LICENSE)

Interactive CLI that exports a public Spotify playlist's tracks as CSV or JSON.

## Tech stack

Python · Typer · questionary · Spotify Web API (Client Credentials) · Ruff · mypy · pytest · uv

## Features

- **Interactive wizard** — prompts for playlist, format, columns, and output whenever a flag isn't passed, Vite-style.
- **Fully scriptable** — every prompt has a matching flag (`--format`, `--columns`, `--output`), so it runs with zero prompts once everything's provided.
- **CSV/JSON export** — JSON wraps tracks in playlist metadata (`playlist_id`, `playlist_name`, `exported_at`); CSV is a flat table.

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
