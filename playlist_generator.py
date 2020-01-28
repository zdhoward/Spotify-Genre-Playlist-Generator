import os
import sys
import json
from json.decoder import JSONDecodeError
import webbrowser
from time import sleep
import signal

import spotipy
import spotipy.util as util

import pylast

from credentials import (
    SPOTIFY_API_ID,
    SPOTIFY_API_SECRET,
    LAST_FM_API_ID,
    LAST_FM_API_SECRET,
    LAST_FM_USERNAME,
    LAST_FM_HASHED_PASS,
)

from definitions import genres, genre_blacklist

os.environ["SPOTIPY_CLIENT_ID"] = SPOTIFY_API_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIFY_API_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = "http://www.google.com/"

username = "zdhoward"
scope = "user-library-read"

speed = 50

unused_genres = []

sp = None
fm = None


def signal_handler(_sig, _frame):
    print("You pressed Ctrl+C!")
    sys.exit(0)


def main():
    global sp, fm, unused_genres

    signal.signal(signal.SIGINT, signal_handler)

    sp = connect_to_spotify()
    fm = connect_to_last_fm()
    display_name = sp.current_user()["display_name"]
    print(f"Hello, {display_name}!")
    # print("[b] Rebuild track database")
    # print("[a] Reanalyze track database")
    # print("[g] Generate Playlists")
    # operation = ""
    # while True:
    #    operation = input("What would you like to do?\n")
    #    if operation == "b" or operation == "a" or operation == "g":
    #        break
    #    print("Please select a valid option")
    # print(operation)
    # if operation == "d"
    ################################
    #   DEBUGGING
    force_data = True

    tracks = load_track_list()
    if tracks == False:
        force_data = True
        tracks = build_track_list(sp)

    data = load_track_data()
    if data == False or force_data:
        data = analyze_track_list(tracks[1000:1500])

    print("\n\nUsed Genres:")
    print(data.keys())

    print("\n\nUnused Genres:")
    # print("\n".join(unused_genres))
    for genre in unused_genres:
        print(f'"{genre}",')

    # track = fm.get_track("Aesop Rock", "Cat Food")
    # track = fm.get_track("Iron Maiden", "Fear of the Dark")


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


def connect_to_last_fm():
    log("Connecting to Last FM")
    lastfmObject = pylast.LastFMNetwork(
        api_key=LAST_FM_API_ID,
        api_secret=LAST_FM_API_SECRET,
        username=LAST_FM_USERNAME,
        password_hash=LAST_FM_HASHED_PASS,
    )
    return lastfmObject


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


def analyze_track_list(_tracks):
    global fm
    log("Analyzing Track List")
    data = {}
    for track in _tracks:
        artist = track["track"]["artists"][0]["name"]
        song = track["track"]["name"]
        genre = categorize_track(artist, song)
        if genre != False:
            if genre not in data.keys():
                data[genre] = []
            data[genre].append({"artist": artist, "song": song})
        # analyze track and get genre
        # add track to the genre list
    save_track_data(data)
    return data


def categorize_track(_artist, _song):
    global unused_genres
    try:
        track = fm.get_track(_artist, _song)
        tags = track.get_top_tags()

        for name, weight in tags:
            for genre in genres.keys():
                # print (f"Checking {genre}")
                if str(name).lower() in genres[genre]:
                    # log(
                    #    f"Categorizing as {str(name).lower()} => {genre}: {_song} - {_artist}"
                    # )
                    return genre
        # if none are matched then add all options to unused_genres
        for name, weight in tags:
            if (
                str(name).lower() not in unused_genres
                and str(name).lower() not in genre_blacklist
            ):
                print(
                    f"Adding {str(name).lower()} to unused_genres because of: {_song} - {_artist})"
                )
                unused_genres.append(str(name).lower())
    except:
        log(f"Failed to categorize: {_song} - {_artist} ")
    return False


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


def generate_playlists():
    log("Generating Playlists")


def generate_playlist():
    log("Generating Playlist")


def log(_msg):
    print(_msg)


if __name__ == "__main__":
    main()
