# Architecture

## Domain Model

`Track` isn't persisted — it exists only for the duration of one export, built from Spotify's playlist-items response. `artist` is the one field with a shape that differs by target: a real list on the `Track` object (kept as an array in JSON), joined into a comma-separated string wherever a flat format is needed (CSV, the interactive column picker's display). Items Spotify reports as local files, podcast episodes, or unavailable/removed never become a `Track` — they're filtered out before this point, not represented with null fields.

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

The one flow the CLI has, whether triggered interactively or by flags. Representative because it carries the two non-obvious rules: the 429 retry, and the silent-filter-with-summary for non-track items.

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Spotify as Spotify API

    User->>CLI: spotify-cli [flags]
    CLI->>CLI: prompt for any input missing from flags
    CLI->>Spotify: POST /api/token (Client Credentials)
    Spotify-->>CLI: access_token
    CLI->>Spotify: GET playlist items (paginated)
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

A 404 (playlist not found/private) or 401 (bad credentials) never retries — the CLI fails fast with a clear message and exit code 1, unlike the 429 case above. The 429 retry gives up after 5 attempts, to avoid hanging indefinitely on a persistent rate limit.
