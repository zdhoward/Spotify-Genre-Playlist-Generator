import json
from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util

import os
from os.path import exists
from time import sleep
from random import shuffle
from datetime import datetime

from credentials import USERNAME, SPOTIFY_API_ID, SPOTIFY_API_SECRET
from definitions import ARTIST_CATEGORIES

speed = 50
tracks_file = "tracks.json"
analysis_file = "analysis.json"

playlist_prefix = "GEN-"
date_postfix = "-" + datetime.today().strftime("%Y-%m-%d")

sp = None

uncategorized_artists = []

show_uncategorized_artists = True
force_rebuild = True
include_date_in_name = False


def main():
    global sp, uncategorized_artists
    sp = connect_to_spotify()

    if exists(tracks_file) and not force_rebuild:
        tracks = load_json(tracks_file)
    else:
        tracks = build_track_list()

    analysis = analyze_track_list(tracks)

    ## report any issues

    ## generate playlists
    for playlist in analysis.keys():
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
            # log("Replacing current playlist")
            sp.user_playlist_replace_tracks(USERNAME, id, playlist)

    if not replaced:
        # create a new playlist with playlist
        # log("Creating a new playlist")
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
    # log("Categorizing Track")
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


def get_data_from_track_list_item(_item):
    track = _item["track"]
    artist = track["artists"][0]["name"]
    song = track["name"]
    id = track["id"]
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
    scope = "user-library-read playlist-modify-private playlist-read-private"
    os.environ["SPOTIPY_CLIENT_ID"] = SPOTIFY_API_ID
    os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIFY_API_SECRET
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://www.google.com/"
    # erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(USERNAME, scope)
    except:
        os.remove(f".cache-{USERNAME}")
        token = util.prompt_for_user_token(USERNAME, scope)

    return spotipy.Spotify(auth=token)


def build_track_list():
    global sp
    log("Building Track List")
    total = 0
    offset = 0
    page_limit = 50
    tracks = []
    while True:
        page = sp.current_user_saved_tracks(limit=page_limit, offset=offset)
        if total == 0:
            total = page["total"]
        tracks += page["items"]
        if offset + page_limit >= total:
            leftovers = total - offset
            tracks += sp.current_user_saved_tracks(limit=leftovers, offset=offset)[
                "items"
            ]
            break
        offset += page_limit
        print(offset, "/", total, end="\r")
        if speed > 0:
            sleep(speed / 1000)
    print(offset + leftovers, "/", total)
    save_json(tracks_file, tracks)
    return tracks


def log(_msg):
    print(_msg)


if __name__ == "__main__":
    main()
