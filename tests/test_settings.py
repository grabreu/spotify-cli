from __future__ import annotations

import pytest

from spotify_cli.settings import MissingCredentialsError, load_settings


def test_load_settings_reads_client_id_and_applies_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "the-id")
    monkeypatch.delenv("SPOTIFY_REDIRECT_URI", raising=False)
    monkeypatch.delenv("SPOTIFY_SCOPE", raising=False)

    settings = load_settings(env_file=None)

    assert settings.spotify_client_id == "the-id"
    assert settings.spotify_redirect_uri == "http://127.0.0.1:8080/callback"
    assert settings.spotify_scope == "playlist-read-private user-library-read"


def test_load_settings_missing_client_id_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)

    with pytest.raises(MissingCredentialsError):
        load_settings(env_file=None)
