# CLI defaults to an interactive wizard, not flags-only

`questionary` drives a Vite-style wizard — prompting for playlist, format, columns, and output — instead of the more common flags-only CLI pattern (plain Typer/argparse, no prompts). Any flag supplied skips its matching prompt, so the same command still runs with zero prompts once every value is passed; the wizard is a convenience layer over the flags, not a separate mode.

**Consequences**: adds a dependency (`questionary`) beyond the CLI framework itself. Non-interactive environments (CI, piped stdin) must pass every flag explicitly, or the run blocks waiting on a prompt that can never be answered.
