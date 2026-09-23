# Spotify auth uses Authorization Code with PKCE, not Client Credentials

Authorization Code with PKCE (browser login, no client secret) was chosen over Client Credentials (app-only auth): Spotify's playlist items endpoint requires a real, logged-in user and only serves playlists that user owns or collaborates on. Client Credentials has no user context at all, so it can only reach playlist metadata, never the tracks, for any playlist. PKCE was chosen over the classic Authorization Code flow because it needs no client secret, which fits a distributed CLI with nowhere secure to store one. `spotipy` handles the flow (PKCE, browser login, local callback capture, token refresh) rather than a hand-rolled implementation.

The access/refresh token pair is cached to `~/.cache/spotify-cli/token.json` and refreshed automatically, so login only happens once.

**Consequences**: the first run (or an expired/revoked cache) requires a browser and a signed-in Spotify account. The CLI is not usable in a fully headless/CI context without a pre-seeded cache file. The cached token file is a credential and must be kept out of version control. Logging in does not unlock arbitrary public playlists: Spotify still only returns track data for playlists the logged-in user owns or collaborates on, so the CLI's scope is "your own (or collaborative) playlists," not "any public playlist."
