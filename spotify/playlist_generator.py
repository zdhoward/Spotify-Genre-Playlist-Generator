from credentials import SPOTIFY_API_ID, SPOTIFY_API_SECRET

import spotipy
import spotipy.util as util

import os
import json
from json.decoder import JSONDecodeError
from time import sleep

os.environ["SPOTIPY_CLIENT_ID"] = SPOTIFY_API_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIFY_API_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = "http://www.google.com/"

username = "zdhoward"
scope = "user-library-read"

speed = 50

sp = None


def main():
    global sp
    sp = connect_to_spotify()
    print("Hello, World!")

    force_data = True

    tracks = load_track_list()
    if tracks == False:
        force_data = True
        tracks = build_track_list()

    data = analyze_track_list(tracks[:20])

    for item in data:
        print(item)


def connect_to_spotify():
    log("Connecting to Spotify")
    # erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        if os.path.exists(f".cache-{username}"):
            os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    spotifyObject = spotipy.Spotify(auth=token)

    return spotifyObject


def load_track_list():
    log("Loading Track List")
    try:
        with open("tracks.json", "r") as file:
            data = json.load(file)
        return data
    except:
        log("ERROR - Failed to Load")
        return False


def save_track_list(_results):
    log("Saving Track List")
    try:
        with open("tracks.json", "w") as file:
            file.write(json.dumps(_results))
    except:
        log("ERROR - Failed To Save")
        return False


def display_track_list(_results):
    log("Displaying Track List")
    for item in _results:
        track = item["track"]
        print("%32.32s %s" % (track["artists"][0]["name"], track["name"]))


def load_track_data():
    log("Loading Track Data")
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
        return data
    except:
        log("ERROR - No Save File Found")
        return False


def save_track_data(_data):
    log("Saving Track Data")
    try:
        with open("data.json", "w") as file:
            file.write(json.dumps(_data))
    except:
        log("ERROR - Failed To Save")
        return False


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
        sleep(speed / 1000)
    print(offset + leftovers, "/", total)
    save_track_list(tracks)
    return tracks


def analyze_track_list(_tracks):
    global sp
    tracks = []
    for track in _tracks:
        # print("Artist: ", track["track"]["artists"][0]["name"])
        tracks.append(
            {
                "artist": track["track"]["artists"][0]["name"],
                "song": track["track"]["name"],
                "id": track["track"]["id"],
                "genre": sp.album(track["track"]["album"]["id"])["genres"],
            }
        )
    return tracks


def log(_msg):
    print(_msg)


if __name__ == "__main__":
    main()
