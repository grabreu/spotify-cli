import pytest

from spotify_cli.playlist import InvalidPlaylistReferenceError, parse_playlist_id


@pytest.mark.parametrize(
    "reference",
    [
        "37i9dQZF1DXcBWIGoYBM5M",
        "  37i9dQZF1DXcBWIGoYBM5M  ",
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc123",
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M/",
        "https://open.spotify.com/intl-pt/playlist/37i9dQZF1DXcBWIGoYBM5M",
        "http://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
        "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
    ],
)
def test_parse_playlist_id_accepts_known_shapes(reference: str) -> None:
    assert parse_playlist_id(reference) == "37i9dQZF1DXcBWIGoYBM5M"


@pytest.mark.parametrize(
    "reference",
    [
        "",
        "   ",
        "not a playlist reference",
        "https://example.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
        "https://open.spotify.com/album/37i9dQZF1DXcBWIGoYBM5M",
        "https://open.spotify.com/playlist/",
        "spotify:track:37i9dQZF1DXcBWIGoYBM5M",
        "37i9dQZF1DXcBWIGoYBM5M!",
    ],
)
def test_parse_playlist_id_rejects_unrecognized_input(reference: str) -> None:
    with pytest.raises(InvalidPlaylistReferenceError):
        parse_playlist_id(reference)
