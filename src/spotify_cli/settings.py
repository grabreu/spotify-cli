from __future__ import annotations

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class MissingCredentialsError(RuntimeError):
    pass


class Settings(BaseSettings):
    spotify_client_id: str
    spotify_redirect_uri: str = "http://127.0.0.1:8080/callback"
    spotify_scope: str = "playlist-read-private user-library-read"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def load_settings(*, env_file: str | None = ".env") -> Settings:
    try:
        return Settings(_env_file=env_file)
    except ValidationError as error:
        raise MissingCredentialsError("SPOTIFY_CLIENT_ID must be set (env or .env).") from error
