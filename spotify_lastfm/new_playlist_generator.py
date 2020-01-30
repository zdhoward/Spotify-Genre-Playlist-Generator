import os

import pylast
import spotipy
import spotipy.util as util

import json
from json.decoder import JSONDecodeError

from credentials import (
    SPOTIFY_API_ID,
    SPOTIFY_API_SECRET,
    LAST_FM_API_ID,
    LAST_FM_API_SECRET,
    LAST_FM_USERNAME,
    LAST_FM_HASHED_PASS,
)

from definitions import genres, genre_blacklist, artist_category

## file config
tracks_file = "tracks.json"
data_file = "data.json"

# spotify config
username = "zdhoward"
scope = "user-library-read"
os.environ["SPOTIPY_CLIENT_ID"] = SPOTIFY_API_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIFY_API_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = "http://www.google.com/"

# speed of requests
speed = 50

unused_genres = []
artists_to_categorize = []

# init connection objects
fm = None
sp = None


def main():
    global fm, sp, unused_genres, artists_to_categorize
    fm = connect_to_last_fm()
    sp = connect_to_spotify()

    # load track list if available # for debugging only
    track_list = load_json(tracks_file)
    # load data list if available
    saved_data_list = load_json(data_file)

    # get current track list
    if track_list == False:
        track_list = build_track_list()

    # update data list if track isn't already saved
    data_list = update_data(saved_data_list, track_list[2000:3000])

    save_json(data_file, data_list)

    print("\n\nUnused Genres:")
    for genre in sorted(unused_genres):
        print(f'"{genre}",')

    print("\n\nArtists To Categorize:")
    for artist in sorted(artists_to_categorize):
        print(f'"{artist}",')


def update_data(_saved, _tracks):
    log("Updating Data List")
    # get ids in saved
    ids = []
    for genre in _saved.keys():
        for item in _saved[genre]:
            ids.append(item["id"])

    # look through all tracks and analyze the missing entries
    to_analyze = []
    for track in _tracks:
        if track["track"]["id"] not in ids:
            to_analyze.append(
                {
                    "artist": track["track"]["artists"][0]["name"],
                    "song": track["track"]["name"],
                    "id": track["track"]["id"],
                }
            )

    new_data = {}

    if len(to_analyze) > 0:
        analyzed = analyze_track_list(to_analyze)
        for genre in genres:
            genre_tracks = []
            if genre in _saved.keys():
                genre_tracks += _saved[genre]
            if genre in analyzed.keys():
                genre_tracks += analyzed[genre]
            new_data[genre] = genre_tracks

    return new_data


def analyze_track_list(_tracks):
    global fm
    log("Analyzing Track List")
    data = {}
    count = 0
    for track in _tracks:
        # artist = track["track"]["artists"][0]["name"]
        # song = track["track"]["name"]
        # id = track["track"]["id"]
        print(f"{count}/{len(_tracks)}", end="\r")
        count += 1

        artist = track["artist"]
        song = track["song"]
        id = track["id"]

        genre = categorize_track(artist, song)
        if genre != False:
            if genre not in data.keys():
                data[genre] = []
            data[genre].append({"artist": artist, "song": song, "id": id})
        # analyze track and get genre
        # add track to the genre list
    return data


def categorize_track(_artist, _song):
    global unused_genres, artists_to_categorize
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
        if _artist.lower() == "doobmin":
            return "Hip-Hop"

    ## attempt to classify by artist
    for genre in artist_category.keys():
        if _artist in artist_category[genre]:
            return genre
    if _artist not in artists_to_categorize:
        artists_to_categorize.append(_artist)
    log(f"Failed to categorize: {_song} - {_artist} ")
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
    save_json(tracks_file, tracks)
    return tracks


def log(_msg):
    print(_msg)


if __name__ == "__main__":
    main()
