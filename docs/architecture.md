# Architecture

## Domain Model

`Track` isn't persisted — it exists only for the duration of one export, built from Spotify's playlist-items response, or from the Liked Songs (saved tracks) response when `--liked` is used — the two have different raw shapes (`item` vs. `track`) but are normalized to the same shape before reaching `Track`. `artist` is the one field with a shape that differs by target: a real list on the `Track` object (kept as an array in JSON), joined into a comma-separated string wherever a flat format is needed (CSV, the interactive column picker's display). Items Spotify reports as local files, podcast episodes, or unavailable/removed never become a `Track` — they're filtered out before this point, not represented with null fields. Liked Songs export uses the fixed `playlist_id`/`playlist_name` pair `"liked_songs"`/`"Liked Songs"`, since Spotify has no real playlist for it.

```mermaid
classDiagram
    class Track {
        +string title
        +List~string~ artist
        +string album
        +string duration
        +string isrc
        +int track_number
        +datetime added_at
        +string spotify_url
    }
    class Export {
        +string playlist_id
        +string playlist_name
        +datetime exported_at
        +List~Track~ tracks
    }
    Export "1" --> "*" Track
```

## Export Flow

The one flow the CLI has, whether triggered interactively or by flags, and whether the source is a playlist or (`--liked`) Liked Songs — those two only differ in which Spotify endpoint is paginated. Representative because it carries the two non-obvious rules: the 429 retry, and the silent-filter-with-summary for non-track items.

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Spotify as Spotify API

    User->>CLI: spotify-cli [flags]
    CLI->>CLI: prompt for any input missing from flags
    alt no cached token, or cached token expired/revoked
        CLI->>User: open browser to log in (Authorization Code + PKCE)
        User->>Spotify: authorize
        Spotify-->>CLI: access_token + refresh_token (cached to disk)
    end
    CLI->>Spotify: GET playlist items, or Liked Songs, paginated
    alt 429 rate limited
        Spotify-->>CLI: 429 + Retry-After
        CLI->>CLI: wait, retry
    end
    Spotify-->>CLI: playlist item pages
    CLI->>CLI: drop local/episode/unavailable items, summarize count to stderr
    CLI->>CLI: map remaining items to Track, apply selected columns
    alt --output given (or wizard says "save")
        CLI-->>User: write CSV/JSON to file
    else
        CLI-->>User: print CSV/JSON to stdout
    end
```

A 404 (playlist doesn't exist), 401 (bad/expired token), or 403 (playlist exists but isn't owned by, or shared with, the logged-in user — Spotify's API withholds track data from everyone else, regardless of the playlist's public/private visibility) never retries — the CLI fails fast with a clear message and exit code 1, unlike the 429 case above. The 429 retry (handled by `spotipy`) gives up after 5 attempts, to avoid hanging indefinitely on a persistent rate limit.
