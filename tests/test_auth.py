from __future__ import annotations

from pathlib import Path

from spotipy.oauth2 import SpotifyPKCE

from spotify_cli.auth import create_spotify_client
from spotify_cli.settings import Settings


def test_create_spotify_client_configures_pkce_from_settings(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        spotify_client_id="the-id",
        spotify_redirect_uri="http://127.0.0.1:9999/callback",
        spotify_scope="playlist-read-private",
    )
    cache_path = tmp_path / "token.json"

    spotify = create_spotify_client(settings, cache_path=cache_path)

    auth_manager = spotify.auth_manager
    assert isinstance(auth_manager, SpotifyPKCE)
    assert auth_manager.client_id == "the-id"
    assert auth_manager.redirect_uri == "http://127.0.0.1:9999/callback"
    assert cache_path.parent.exists()
