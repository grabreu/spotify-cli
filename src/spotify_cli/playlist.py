from __future__ import annotations

import re
from urllib.parse import urlparse

_ID_PATTERN = re.compile(r"^[A-Za-z0-9]+$")
_URI_PATTERN = re.compile(r"^spotify:playlist:([A-Za-z0-9]+)$")


class InvalidPlaylistReferenceError(ValueError):
    pass


def parse_playlist_id(reference: str) -> str:
    reference = reference.strip()

    uri_match = _URI_PATTERN.match(reference)
    if uri_match:
        return uri_match.group(1)

    if reference.startswith(("http://", "https://")):
        return _parse_url(reference)

    if _ID_PATTERN.match(reference):
        return reference

    raise InvalidPlaylistReferenceError(
        f"Not a recognizable playlist ID, URL, or URI: {reference!r}"
    )


def _parse_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc != "open.spotify.com":
        raise InvalidPlaylistReferenceError(f"Not a recognizable playlist ID, URL, or URI: {url!r}")

    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) >= 2 and segments[-2] == "playlist" and _ID_PATTERN.match(segments[-1]):
        return segments[-1]

    raise InvalidPlaylistReferenceError(f"Not a recognizable playlist ID, URL, or URI: {url!r}")
