from __future__ import annotations

from pathlib import Path

from spotipy import Spotify
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyPKCE

from spotify_cli.settings import Settings

DEFAULT_CACHE_PATH = Path.home() / ".cache" / "spotify-cli" / "token.json"


def create_spotify_client(settings: Settings, *, cache_path: Path = DEFAULT_CACHE_PATH) -> Spotify:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    auth_manager = SpotifyPKCE(
        client_id=settings.spotify_client_id,
        redirect_uri=settings.spotify_redirect_uri,
        scope=settings.spotify_scope,
        open_browser=True,
        cache_handler=CacheFileHandler(cache_path=str(cache_path)),
    )
    return Spotify(auth_manager=auth_manager, retries=5)
