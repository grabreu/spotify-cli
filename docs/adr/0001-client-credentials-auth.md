# Spotify auth uses Client Credentials, not user login

Client Credentials (app-only auth, just a Client ID/Secret) was chosen over the Authorization Code flow, which would require the user to log into their own Spotify account and grant OAuth scopes before every run.

**Consequences**: only public playlists are reachable — a private or collaborative playlist the user owns but hasn't made public can't be exported. Switching to Authorization Code later would add a login step and token refresh handling; revisit only if per-user data (saved tracks, private playlists) becomes an actual need.
