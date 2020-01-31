import json
from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util

import os
from os.path import exists
from time import sleep

from credentials import USERNAME, SPOTIFY_API_ID, SPOTIFY_API_SECRET

speed = 50
tracks_file = "tracks.json"
analysis_file = "analysis.json"


def main():
    sp = connect_to_spotify()

    if exists(tracks_file):  ## this is for debug only
        tracks = load_json(tracks_file)
    else:
        tracks = build_track_list(sp)

    ## update analyzed data to categorize song into all applicable playlists

    ## report any issues

    ## generate playlists


def analyze_track_list():
    return False


def update_analysis():
    return False


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


def build_track_list(sp):
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
        sleep(speed / 1000)
    print(offset + leftovers, "/", total)
    save_json(tracks_file, tracks)
    return tracks


def log(_msg):
    print(_msg)


if __name__ == "__main__":
    main()
