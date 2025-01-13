"""This module handles the retrieval of the music details that are displayed in the result tables.

methods:
    token_to_dict
    collage
    get_unique_n
    request_spotify_data

blueprint routes:
    get_spotify_token
    get_acousticbrainz_data
    get_background
    first_100_album_collage

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)
"""
import base64
import json
import os
import time
from io import BytesIO
import requests
import numpy as np
from PIL import Image
from dotenv import load_dotenv

from flask import Blueprint, request

from project.blueprints.constants import BAD_REQUEST_RESPONSE
from project.models import token as tok

blueprint = Blueprint('music', __name__, url_prefix='/api/music')

SPOTIFY_API = 'https://api.spotify.com/v1/'
AB_API = 'https://acousticbrainz.org/api/v1/'
LFM_API = 'http://ws.audioscrobbler.com/2.0/'
LFM_KEY = '5ffe852eb4ffb7e7d5d53e71981cad7f'
MAX_TRACK_LIMIT = 50


@blueprint.route('/song-info', methods=['POST'])
def song_info():
    """Get the LastFM and AcousticBrainz data from a song using their APIs.

    Returns:
         Object with AcousticBrainz and LastFM data
    """
    json_data = request.json
    try:
        track = json_data['track']
        artist = json_data['artist']
    except KeyError:
        return BAD_REQUEST_RESPONSE
    mbid = json_data.get('mbid')
    lastfm_data = last_fm_info(artist, track, mbid)
    if 'track' in lastfm_data:
        lastfm_track = lastfm_data['track']
        if not mbid and lastfm_track and 'mbid' in lastfm_track:
            mbid = lastfm_track['mbid']
    return {'AcousticBrainz':get_acousticbrainz_data(mbid) if mbid else None,
            'LastFM':lastfm_data}


@blueprint.route('/spotify-info', methods=['POST'])
def spotify_info():
    """Request Spotify data by making a query with artist and track name.

    Returns:
        Spotify tracks found by query, each track containing data
    """
    json_data = request.json
    try:
        track = json_data['track']
        artist = json_data['artist']
    except KeyError:
        return BAD_REQUEST_RESPONSE
    artist_query = 'artist:' + artist if artist else ''
    track_query = '+track:' + track if track else ''
    url = 'search?q=' + artist_query + track_query + '&type=track'
    data = request_spotify_data(url)
    return data['tracks']


@blueprint.route('/spotify-track', methods=['POST'])
def spotify_track():
    """Request Spotify track from its ID.

    Returns:
        the Spotify track
    """
    json_data = request.json
    try:
        track_id = json_data['id']
    except KeyError:
        return BAD_REQUEST_RESPONSE
    url = 'tracks/' + track_id
    data = request_spotify_data(url)
    return data


def last_fm_info(artist, track, mbid):
    """Request song-data from LastFM.

    Args:
        artist: the artist name
        track: the track name
        mbid: MBID unique hash-token

    Returns:
        Object containing all LastFM data about a track
    """
    # Use MBID instead of artist and track name
    if mbid:
        url = LFM_API + '?method=track.getInfo&api_key=' + LFM_KEY + \
              '&mbid=' + mbid + '&autocorrect=1&format=json'
    else:
        url = LFM_API + '?method=track.getInfo&api_key=' + LFM_KEY + \
              '&artist=' + artist + \
              '&track=' + track + '&autocorrect=1&format=json'
    res = requests.get(url, timeout=10)
    return json.loads(res.text)


def get_acousticbrainz_data(mbid):
    """Request High-Level audio features from the AcousticBrainz API using a MusicBrainzID.

    Args:
        mbid: Unique MusicBrainz identifier, which can be retrieved from LastFM

    Returns:
        Dict: Dictionary with all High-Level audiofeatures
    """
    url = AB_API + 'high-level' + '?recording_ids=' + mbid
    res = requests.get(url, timeout=10)
    return json.loads(res.text)


@blueprint.route('/background', methods=['GET'])
def get_background():
    """Generate a background from the album covers of a Spotify Playlist.

    Returns:
        Image: Background-image
    """
    playlist1 = '6KnSfElksjrqygPIc4TDmf'  # Playlist with nice album art

    playlist_id = playlist1

    items = []
    # Keep querying until we have all playlist items.
    offset = 0
    playlist_length = 0
    while offset < playlist_length or offset == 0:
        url = 'playlists/' \
              + playlist_id + '/tracks?limit=' \
              + str(MAX_TRACK_LIMIT) + '&offset=' \
              + str(offset)
        playlist = request_spotify_data(url)

        items += playlist['items']
        if offset == 0:
            playlist_length = playlist['total']
        offset += MAX_TRACK_LIMIT
    urls = [item['track']['album']['images'][1]['url'] for item in items]
    images = [Image.open(BytesIO(requests.get(url, timeout=10).content)) for url in urls]
    collage(images)
    return 'Background saved'


def collage(images, size=10):
    """Create collage from images.

    Args:
        images: the image urls
        size: matrix size (size x size matrix of images)

    Returns:
        the collage in PNG format
    """
    image_width, image_height = images[0].size
    width = image_width * size
    height = image_width * size
    background = Image.new('RGB', (width, height))
    index = 0
    for i in range(0, width, image_width):
        for j in range(0, height, image_height):
            background.paste(images[index], (i, j))
            index += 1
            # Handle contents size smaller than image count (flip).
            if index == len(images) - 1:
                # Flip images using NumPy array
                images = [Image.fromarray(np.flip(img, axis=0)) for img in images]
                index = 0
    background.save('../client/public/background.png')
    return background


@blueprint.route('/unique-album-background', methods=['GET'])
def first_100_album_collage():
    """Route: Make a collage from the first 100 relevant albums from Spotify.

    Returns:
        an PNG image with the collage
    """
    # Get all items. "q=*" ensures that we search for all albums without any filter.
    albums = get_unique_n('q=*', 100, 'album', True)
    images = [Image.open(BytesIO(requests.get(url, timeout=10).content)) for url in albums]

    collage(images)
    return 'Background saved'


def get_unique_n(query, amount, category, image):
    """Route: Given a Spotify query, find the n most relevant (first) unique items.

    Args:
        query: the query to do in the Spotify search
        amount: the amount of unique items
        category: the query object category (tracks/albums/playlists/etc.)
        image(bool): whether image items should be retrieved

    Returns:
        the n unique items
    """
    # Amount of items returned are a multiple of 10.
    limit = 10
    url = SPOTIFY_API + 'search?' + query + '&type=' + category + '&limit=' + str(limit)

    items = set()  # Use a set to enforce uniqueness
    # Get next until we have n items.
    while len(items) < amount:
        query = request_spotify_data(url, full_url=True)

        # Validate the query response
        if not query or category + 's' not in query:
            print("Invalid response or missing category data.")
            break

        category_data = query[category + 's']
        if 'items' not in category_data or not category_data['items']:
            print("No items found in category data.")
            break

        # Add image URLs or IDs
        for item in category_data['items']:
            if image:
                try:
                    # Safely access the second image if it exists
                    if 'images' in item and len(item['images']) > 1:
                        items.add(item['images'][1]['url'])
                except Exception as e:
                    print(f"Error processing image data: {e}")

            else:
                try:
                    items.add(item['id'])
                except KeyError:
                    print(f"Error processing item ID for {item}.")

        # Break if no more pages are available
        if not category_data.get('next'):
            break

        url = category_data['next']

    # Return only the requested number of unique items
    return list(items)[:amount]


def request_spotify_data(url, full_url=False):
    """Make an authorised Spotify JSON request from the url.

    Args:
        url: the url at which to do the request
        full_url: whether the url contains the Spotify endpoint already

    Returns:
        the response text
    """
    full_url = url if full_url else SPOTIFY_API + url
    # print('spotify request url', full_url)
    get_spotify_token()
    headers = {'Authorization':tok.token_type + ' ' + tok.access_token,
               'Content-Type':'application/json'}
    res = requests.get(full_url, headers=headers,timeout=10)
    # print('spotify request data', json.loads(res.text))
    return json.loads(res.text)


def get_spotify_token():
    """Route: Get Spotify auth TOKEN using client credentials (id and secret).

    Returns:
        dict: A dictionary containing the access token and token type.
    """
    if (not tok.access_token) or tok.expiration_time - 100 > time.time():
        load_dotenv()  # Load variables from .env file
        spotify_id = os.getenv('SPOTIFY_CLIENT_ID')
        spotify_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        # Ensure credentials are provided
        if not spotify_id or not spotify_secret:
            raise ValueError("Spotify client ID and secret must be set.")

        # Encode credentials for Basic Auth
        message = f"{spotify_id}:{spotify_secret}".encode('utf-8')
        encoded = base64.b64encode(message).decode('utf-8')

        headers = {
            'Authorization':f'Basic {encoded}',
            'Content-Type':'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}

        try:
            res = requests.post(
              'https://accounts.spotify.com/api/token', data=data, headers=headers, timeout=10)
            res.raise_for_status()  # Raise an error for bad status codes
            token_data = res.json()

            tok.access_token = token_data['access_token']
            tok.token_type = token_data['token_type']
            tok.expiration_time = time.time() + token_data.get('expires_in', 3600)

        except requests.RequestException as e:
            raise RuntimeError(f'Failed to retrieve Spotify token: {e}') from e

    return {
        "access_token":tok.access_token,
        "token_type":tok.token_type,
        "expires_in":int(tok.expiration_time - time.time())
    }


def token_to_dict(token):
    """Convert a token to a dictionary format.

    Args:
        token: the token to convert

    Returns:
        the token in dictionary form
    """
    return {'access_token':token.access_token,
            'token_type':token.token_type,
            'expiration_time':token.expiration_time}
