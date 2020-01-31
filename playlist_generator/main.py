import json
from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util

import os
from os.path import exists
from time import sleep

from credentials import USERNAME, SPOTIFY_API_ID, SPOTIFY_API_SECRET
from definitions import ARTIST_CATEGORIES

speed = 50
tracks_file = "tracks.json"
analysis_file = "analysis.json"

sp = None

uncategorized_artists = []


def main():
    global sp
    sp = connect_to_spotify()

    if exists(tracks_file):  ## this is for debug only
        tracks = load_json(tracks_file)
    else:
        tracks = build_track_list()[:100]

    ## update analyzed data to categorize song into all applicable playlists
    if exists(analysis_file):
        saved_analysis = load_json(analysis)
        analysis = update_analysis(saved_analysis, tracks)
    else:
        analysis = analyze_track_list(tracks)

    ## report any issues

    ## generate playlists

    for item in analysis["Hip Hop"]:
        id, artist, song = get_data_from_track_list_item(item)
        print(id, artist, song)
    # print(uncategorized_artists)


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
    return analysis


def categorize_track(_track):
    global uncategorized_artists
    # log("Categorizing Track")
    categories = []
    id, artist, song = get_data_from_track_list_item(_track)
    for category in ARTIST_CATEGORIES.keys():
        if artist in ARTIST_CATEGORIES[category]:
            categories.append(category)
        if len(categories) < 1:
            if artist not in uncategorized_artists:
                uncategorized_artists.append(artist)
    return categories


def update_analysis(_saved_analysis, _track_list):
    log("Updating Analysis")
    saved_analysis = load_json(analysis_file)

    ids = []
    for category in _saved_analysis.keys():
        for item in _saved_analysis[category]:
            ids.append(item["id"])

    print(ids)

    new_analysis = analyze_track_list(_track_list)
    return False


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
    scope = "user-library-read"
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
