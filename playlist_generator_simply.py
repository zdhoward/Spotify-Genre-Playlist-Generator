from credentials import SPOTIFY_API_ID, SPOTIFY_API_SECRET

import spotipy
import spotipy.util as util

import os

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

    tracks = load_track_list()

    print(tracks)


def connect_to_spotify():
    log("Connecting to Spotify")
    # erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
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
        log("ERROR - No Save File Found")
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


def log(_msg):
    print(_msg)


if __name__ == "__main__":
    main()
