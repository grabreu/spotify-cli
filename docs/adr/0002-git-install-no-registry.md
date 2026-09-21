# Not published to PyPI — installed straight from GitHub

Unlike Ramus, Aduana, and Desfecho, this CLI isn't registered as a publishable package with its own release-please/registry pipeline. It installs with `pip install git+https://github.com/grabreu/spotify-cli` instead — no PyPI account, no CD workflow, no version tagging to maintain for a tool this size.

**Consequences**: no semver or changelog trail; installing pulls from `main` directly rather than a stable released version (a specific commit can be pinned manually if needed). Fine for a single-user tool — would need real versioning if it ever gained other consumers depending on a stable version.
