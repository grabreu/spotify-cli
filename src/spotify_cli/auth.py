"""Spotify Client Credentials auth: read app credentials and fetch an access token."""

from __future__ import annotations

import os

import httpx
from dotenv import load_dotenv

_TOKEN_URL = "https://accounts.spotify.com/api/token"


class MissingCredentialsError(RuntimeError):
    """Raised when SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET aren't set."""


class SpotifyAuthError(RuntimeError):
    """Raised when the Client Credentials token request fails."""


def load_credentials() -> tuple[str, str]:
    """Read SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET from the environment, with a .env fallback."""
    load_dotenv()
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise MissingCredentialsError(
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set (env or .env)."
        )
    return client_id, client_secret


def fetch_access_token(client: httpx.Client, client_id: str, client_secret: str) -> str:
    """Fetch a fresh app-only access token via the Client Credentials flow. Never cached."""
    response = client.post(
        _TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )

    if response.status_code == 401:
        raise SpotifyAuthError("Spotify rejected the client credentials (401).")
    response.raise_for_status()

    token = response.json().get("access_token")
    if not isinstance(token, str) or not token:
        raise SpotifyAuthError("Spotify's token response didn't include an access_token.")
    return token
