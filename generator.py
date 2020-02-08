#!/usr/bin/env python3
import json
from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util
from spotipy import oauth2

import os
from os.path import exists
from time import sleep
from random import shuffle
from datetime import datetime

from credentials import USERNAME, SPOTIFY_API_ID, SPOTIFY_API_SECRET
from definitions import ARTIST_CATEGORIES

from callbacks import wait_for_http_callback, visit_url

speed = 50
tracks_file = "tracks.json"
analysis_file = "analysis.json"

playlist_prefix = "GEN-"
date_postfix = "-" + datetime.today().strftime("%Y-%m-%d")

sp = None

uncategorized_artists = []

show_uncategorized_artists = False
force_rebuild = True
include_date_in_name = False

include_liked_tracks = True
include_liked_albums = True
include_followed_artists = True


def main():
    run()


def run():
    global sp, uncategorized_artists
    sp = connect_to_spotify()

    if exists(tracks_file) and not force_rebuild:
        tracks = load_json(tracks_file)
    else:
        tracks = build_track_list()

    analysis = analyze_track_list(tracks)

    ## generate playlists
    for playlist in sorted(analysis.keys()):
        if playlist != "IGNORE":
            generate_playlist(analysis[playlist], playlist)

    ### debug
    if show_uncategorized_artists:
        print("Uncategorized Artists")
        for artist in sorted(uncategorized_artists):
            print(f'"{artist}",')


def generate_playlist(_track_list, _name, _track_length=0):
    global sp

    # maximum add 100 tracks at a time
    if _track_length == 0 or _track_length > 100:
        _track_length = 100

    playlist_name = (
        f"{playlist_prefix}{_name}{date_postfix if include_date_in_name else ''}"
    )
    log(f"Generating Playlist: {playlist_name}")
    tracks = _track_list
    shuffle(tracks)

    playlist = []
    for track in tracks:
        id, artist, song = get_data_from_track_list_item(track)
        if len(playlist) < _track_length or _track_length == 0:
            playlist.append(id)

    # get a list of current playlists and delete any named like this
    playlists = sp.current_user_playlists()["items"]
    replaced = False

    for each_playlist in playlists:
        if playlist_name == each_playlist["name"]:
            id = each_playlist["id"]
            replaced = True
            # edit playlist
            sp.user_playlist_replace_tracks(USERNAME, id, playlist)

    if not replaced:
        # create a new playlist with playlist
        id = sp.user_playlist_create(
            USERNAME, playlist_name, public=False, description="Generated in Python"
        )["id"]
        sp.user_playlist_add_tracks(USERNAME, id, playlist)


def analyze_track_list(_track_list):
    global uncategorized_artists
    log("Analyzing Track List")
    analysis = {}
    for track in _track_list:
        playlists = categorize_track(track)
        if len(playlists) > 0:
            for playlist in playlists:
                if playlist not in analysis.keys():
                    analysis[playlist] = []
                analysis[playlist].append(track)
        else:
            id, artist, song = get_data_from_track_list_item(track)
            if artist not in uncategorized_artists:
                uncategorized_artists.append(artist)
    save_json(analysis_file, analysis)
    return analysis


def categorize_track(_track):
    global uncategorized_artists
    categories = []
    id, artist, song = get_data_from_track_list_item(_track)
    for category in ARTIST_CATEGORIES.keys():
        if artist in ARTIST_CATEGORIES[category]:
            categories.append(category)
    return categories


def update_analysis(_saved_analysis, _track_list):
    log("Updating Analysis")
    ids = []
    for category in _saved_analysis.keys():
        for item in _saved_analysis[category]:
            id, artist, song = get_data_from_track_list_item(item)
            ids.append(id)

    to_analyze = []
    for track in _track_list:
        id, artist, song = get_data_from_track_list_item(track)
        if id not in ids:
            to_analyze.append(track)

    new_data = {}
    new_analysis = {}
    if len(to_analyze) > 0:
        new_analysis = analyze_track_list(to_analyze)
        for category in ARTIST_CATEGORIES.keys():
            new_data[category] = []
            tracks = []
            if category in _saved_analysis.keys():
                tracks += _saved_analysis[category]
            if category in new_analysis.keys():
                tracks += new_analysis[category]
            new_data[category] = tracks
    return new_data


def get_data_from_track_list_item(_track):
    artist = _track["artists"][0]["name"]
    song = _track["name"]
    id = _track["id"]
    return id, artist, song


def save_json(_json_file, _json):
    log(f"Saving {_json_file}")
    try:
        with open(_json_file, "w") as file:
            file.write(json.dumps(_json))
    except:
        log(f"ERROR - Failed To Save {_json_file}")
        return False


def load_json(_json_file):
    log(f"Loading {_json_file}")
    try:
        with open(_json_file, "r") as file:
            data = json.load(file)
        return data
    except:
        log(f"ERROR - {_json_file} Not File Found")
        return False


def connect_to_spotify():
    log("Connecting to Spotify")
    scope = "user-library-read playlist-modify-private playlist-read-private user-follow-read"
    os.environ["SPOTIPY_CLIENT_ID"] = SPOTIFY_API_ID
    os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIFY_API_SECRET
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:5000/callback"
    # erase cache and prompt for user permission
    try:
        token = get_user_token(USERNAME, scope)
    except:
        os.remove(f".cache-{USERNAME}")
        token = get_user_token(USERNAME, scope)

    return spotipy.Spotify(auth=token)


def build_track_list():
    log("Building New Track List")
    to_merge = []
    if include_liked_tracks:
        to_merge.append(get_saved_tracks())
    if include_liked_albums:
        to_merge.append(get_saved_albums())
    if include_followed_artists:
        to_merge.append(get_followed_artists())

    all_tracks = merge_track_lists(to_merge)

    save_json(tracks_file, all_tracks)
    return all_tracks


def get_saved_albums():
    global sp

    offset = 0
    limit = 50
    total = 0

    saved_tracks = []
    while True:
        page = sp.current_user_saved_albums(limit=50, offset=0)
        if total == 0:
            total = page["total"]

        for album in page["items"]:
            for track in album["album"]["tracks"]["items"]:
                saved_tracks.append(track)

        offset += limit
        if offset >= total:
            break
        if offset + limit > total:
            limit = total - offset
        print(f"Liked Albums: {offset} / {total}", end="\r")
    print(f"Liked Albums: {offset} / {total}")
    return saved_tracks


def get_saved_tracks():
    global sp

    offset = 0
    limit = 50
    total = 0

    saved_tracks = []

    while True:
        page = sp.current_user_saved_tracks(limit=limit, offset=offset)
        for item in page["items"]:
            saved_tracks.append(item["track"])

        if total == 0:
            total = page["total"]

        offset += limit
        if offset >= total:
            break
        if offset + limit > total:
            limit = total - offset
        print(f"Liked Tracks: {offset} / {total}", end="\r")
    print(f"Liked Tracks: {offset} / {total}")
    return saved_tracks


def get_followed_artists():
    global sp
    last = None
    total = 0
    current = 0
    limit = 50

    all_artists = []
    while True:
        followed = sp.current_user_followed_artists(limit=limit, after=last)["artists"]
        artists = followed["items"]
        for artist in artists:
            all_artists.append(artist)
            last = artist["id"]

        if total == 0:
            total = followed["total"]

        current += limit
        if current >= total:
            break
        if current + limit > total:
            limit = total - current

        print(f"Followed Artists: {current} / {total}", end="\r")
    print(f"Followed Artists: {current} / {total}")

    saved_tracks = []
    for artist in all_artists[:1]:
        albums = sp.artist_albums(artist["id"], limit=50)["items"]
        for album in albums:
            tracks = sp.album_tracks(album["id"])
            for track in tracks["items"]:
                saved_tracks.append(track)
    print(f"Followed Artist Tracks: {len(saved_tracks)} / {len(saved_tracks)}")
    return saved_tracks


def merge_two_track_lists(_left, _right):
    all_tracks = _left
    for item in _right:
        if item not in all_tracks:
            all_tracks.append(item)
    return all_tracks


def merge_track_lists(_lists):
    all_tracks = []
    for list in _lists:
        all_tracks = merge_two_track_lists(all_tracks, list)
    return all_tracks


def get_user_token(
    username,
    scope=None,
    client_id=None,
    client_secret=None,
    redirect_uri=None,
    cache_path=None,
):
    """ prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor
        Parameters:
         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens
    """

    if not client_id:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")

    if not client_secret:
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not redirect_uri:
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not client_id:
        raise spotipy.SpotifyException(550, -1, "no credentials set")

    cache_path = cache_path or ".cache-" + username
    sp_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path
    )

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        try:
            visit_url(auth_url)
        except BaseException:
            print("Please navigate here: %s" % auth_url)

        response = wait_for_http_callback(5000)

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        return token_info["access_token"]
    else:
        return None


def log(_msg, end=None):
    print(_msg, end=end)


if __name__ == "__main__":
    main()
