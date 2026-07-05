"""This module tests the music detail functionality and the spotify api.

test_spotify_token(client): test the generating of a Spotify Auth token.
test_acousticbrainz_data(client): test if AcousticBrainz successfully gets requested.
test_background(client): test if a background is successfully generated.
test_collage(): test if the collage method works properly.
test_unique_album_background(client): test if a background is successfully generated.
test_spotify_data(): test if Spotify track data gets successfully requested.

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)
"""

import numpy as np
from sewar.full_ref import uqi
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image

from project.blueprints.music_detail_bp import collage, get_acousticbrainz_data
from project.blueprints.music_detail_bp import request_spotify_data


URL_PREFIX = '/api/music'


def make_fake_image_bytes(size=(10, 10), color=(255, 0, 0)):
    """Build real, openable PNG bytes so Image.open() doesn't choke."""
    img = Image.new('RGB', size, color)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


FAKE_PLAYLIST_RESPONSE = {
    "items": [
        {"track": {"album": {"images": [
            {"url": "http://fake/img1_large.jpg"},
            {"url": "http://fake/img1_small.jpg"},
        ]}}},
        {"track": {"album": {"images": [
            {"url": "http://fake/img2_large.jpg"},
            {"url": "http://fake/img2_small.jpg"},
        ]}}},
    ],
    "total": 2,
}

FAKE_ALBUM_SEARCH_RESPONSE = {
    "albums": {
        "items": [
            {"images": [{"url": "http://fake/a1_large.jpg"}, {"url": "http://fake/a1_small.jpg"}]},
            {"images": [{"url": "http://fake/a2_large.jpg"}, {"url": "http://fake/a2_small.jpg"}]},
        ],
        "next": None,
    }
}

FAKE_SEARCH_RESPONSE = {
    "tracks": {
        "items": [
            {"id": "fake_id", "album": {"name": "Scatman (ski-ba-bop-ba-dop-bop)"}}
        ]
    }
}


def test_acousticbrainz_data():
    """Test if AcousticBrainz successfully gets requested."""
    ab_data = get_acousticbrainz_data('bab7f3de-56e3-42fd-be0d-f122960e6a13')
    assert ab_data


@patch('project.blueprints.music_detail_bp.requests.get')
@patch('project.blueprints.music_detail_bp.request_spotify_data')
def test_background(mock_spotify_data, mock_requests_get, client):
    """Test if a background is successfully generated.

    Args:
        client: The client component used to send requests to the server
    """
    mock_spotify_data.return_value = FAKE_PLAYLIST_RESPONSE

    fake_image_response = MagicMock()
    fake_image_response.content = make_fake_image_bytes()
    mock_requests_get.return_value = fake_image_response

    with patch('project.blueprints.music_detail_bp.collage') as mock_collage:
        response = client.get(URL_PREFIX + '/background')
        assert response.status_code == 200
        assert response.data == b'Background saved'
        mock_collage.assert_called_once()


def test_collage():
    """Test if the collage method works properly."""
    input_img = "tests/thisisbingus.jpg"
    output_img = "tests/4bingus.jpg"

    test_input = Image.open(input_img)
    test_output = Image.open(output_img)

    result = collage([test_input, test_input, test_input, test_input], 2)
    assert uqi(np.asanyarray(test_output), np.asanyarray(result)) > 0.8


@patch('project.blueprints.music_detail_bp.requests.get')
@patch('project.blueprints.music_detail_bp.request_spotify_data')
def test_unique_album_background(mock_spotify_data, mock_requests_get, client):
    """Test if a background is successfully generated.

    Args:
        client: The client component used to send requests to the server
    """
    mock_spotify_data.return_value = FAKE_ALBUM_SEARCH_RESPONSE

    fake_image_response = MagicMock()
    fake_image_response.content = make_fake_image_bytes()
    mock_requests_get.return_value = fake_image_response

    with patch('project.blueprints.music_detail_bp.collage') as mock_collage:
        response = client.get(URL_PREFIX + '/unique-album-background')
        assert response.status_code == 200
        assert response.data == b'Background saved'
        mock_collage.assert_called_once()


@patch('project.blueprints.music_detail_bp.get_spotify_token')
@patch('project.blueprints.music_detail_bp.requests.get')
def test_spotify_data(mock_requests_get, mock_get_token):  # pylint: disable=unused-argument
    """Test if Spotify track data gets successfully requested."""
    from project.models import token as tok
    tok.access_token = 'fake_token'
    tok.token_type = 'Bearer'

    fake_response = MagicMock()
    fake_response.ok = True
    fake_response.json.return_value = FAKE_SEARCH_RESPONSE
    mock_requests_get.return_value = fake_response

    url = 'search?q=scatman%20john&type=track'
    result = request_spotify_data(url)
    assert "Scatman" in result['tracks']['items'][0]['album']['name']
