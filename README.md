# spotify-cli

[![CI](https://github.com/grabreu/spotify-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/grabreu/spotify-cli/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/grabreu/spotify-cli?style=flat-square)](LICENSE)

Interactive CLI that exports a Spotify playlist you own or collaborate on, or your Liked Songs, as CSV or JSON.

```bash
pip install git+https://github.com/grabreu/spotify-cli
```

## Tech stack

Python · Typer · questionary · spotipy (Spotify Web API, Authorization Code + PKCE) · pydantic-settings · Ruff · mypy · pytest · uv

## Usage

```bash
spotify-cli <playlist> --format csv
spotify-cli <playlist> --format json --columns title,artist,isrc --output tracks.json
spotify-cli --liked --format csv --output liked-songs.csv
```

`<playlist>` accepts a playlist ID, an `open.spotify.com/playlist/...` URL, or a `spotify:playlist:...` URI; `--liked` exports your Liked Songs instead (the two are mutually exclusive). Run with no arguments for an interactive wizard that prompts for whatever wasn't passed via flags; see [Configuration](#configuration) below for credentials.

Spotify's Web API only returns track data for playlists you own or collaborate on, a playlist being public isn't enough. Exporting someone else's playlist (even a public, well-known one) fails with a clear error explaining this.

## Features

- **Interactive wizard**: omit any of `playlist`/`--format`/`--columns`/`--output` and it's prompted for (playlist-or-Liked-Songs → playlist → format → columns checkbox, pre-checked with the defaults → save-to-file y/n); pass all of them for a fully non-interactive run.
- **Liked Songs export**: `--liked` exports your saved tracks instead of a playlist.
- **CSV/JSON export**: JSON wraps tracks in playlist metadata (`playlist_id`, `playlist_name`, `exported_at`); CSV is a flat table.
- **Column selection**: `--columns` picks which fields to include (default: `title`, `artist`, `album`, `duration`).
- **Fail-fast errors**: a bad playlist reference, missing/invalid credentials, a playlist that doesn't exist, or one you don't own/collaborate on all exit immediately with a clear message and exit code 1; 429s retry automatically, honoring `Retry-After`.

See [docs/architecture.md](docs/architecture.md) for the domain model and export flow, and [docs/adr/](docs/adr/) for the reasoning behind these decisions.

## Configuration

Requires a Spotify app's Client ID (Authorization Code with PKCE, no client secret needed). Create one at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), add `http://127.0.0.1:8080/callback` under its Redirect URIs, then copy `.env.example` to `.env` and fill in `SPOTIFY_CLIENT_ID`, or export it directly.

The first run opens a browser to log in and authorize the app; the resulting token is cached to `~/.cache/spotify-cli/token.json` and refreshed automatically, so later runs don't need a fresh login.

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
