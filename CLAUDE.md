# spotify-cli

## Repository

Interactive CLI that exports a public Spotify playlist's tracks as CSV or JSON, using the Client Credentials flow (app-only auth, no user login).

Read `README.md` before making changes — it documents the project pitch and features. Read `docs/architecture.md` for the domain model and export flow. Significant, hard-to-reverse decisions are recorded in `docs/adr/` — check it before revisiting one, and add an entry when making a new one.

## General Rules

- Keep changes scoped to the requested change.
- Prefer existing patterns over introducing new abstractions.
- Do not add dependencies unless they are necessary.
- Do not fill gaps with assumptions when the user hasn't given the information — ask, or mark it as pending.
- Do not claim a validation command passed unless it was actually run.
- Code, comments, commit messages, and documentation are always written in English.

## Git

- Do not create or switch branches unless explicitly requested.
- Do not create commits unless explicitly requested.
- Do not push unless explicitly requested.
- Keep commits focused on the requested change.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`type: summary`).

## Documentation

### Audience

Future-you revisiting this months later, or someone browsing the portfolio to see how it works. Not onboarding material — keep it concise and skimmable.

### Content Rules

- State facts concisely. Avoid unnecessary explanations or trailing rationale.
- Do not document information that is already obvious from the repository structure or configuration.
- Do not invent features, API shapes, or future direction — mark undecided things as TODO.
- Document a capability only after it is implemented and verified.
- Use proper Markdown headings (`##`, `###`), not bold text as headings.

---

## Project-Specific Guidelines

### Source

`src/spotify_cli/` (src-layout, hatchling build backend, `py.typed` marker). `cli.py` defines the Typer `app`, installed as the `spotify-cli` entry point. CLI logic (playlist parsing, auth, fetch, export) is not implemented yet — `main()` raises `NotImplementedError`.

### Validation

Run `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy .`, and `uv run pytest` before considering a change done — CI (`.github/workflows/ci.yml`) runs the same on push/PR to `main`. `mypy` runs in strict mode (`tool.mypy` in `pyproject.toml`).
