import os
import sys
import json
import webbrowser

from time import sleep

import spotipy
import spotipy.util as util

from json.decoder import JSONDecodeError

from credentials import ID, SECRET


def main():
    # get username from terminal
    # https://open.spotify.com/user/zdhoward?si=AxiGiLcaShCG1lJjhTb8bA
    username = "zdhoward?si=AxiGiLcaShCG1lJjhTb8bA"
    username = "zdhoward"

    os.environ["SPOTIPY_CLIENT_ID"] = ID
    os.environ["SPOTIPY_CLIENT_SECRET"] = SECRET
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://www.google.com/"

    scope = "user-library-read"

    # erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    # create spotify object
    spotifyObject = spotipy.Spotify(auth=token)

    ## app logic
    user = spotifyObject.current_user()

    display_name = user["display_name"]

    print(display_name)

    results = load_results()
    if results == False:
        results = get_all_saved_tracks(spotifyObject)
    if results:
        show_tracks(results)
        # print (len(results))
        # print (results[180]['track']['artists'][0]['name'])

    # print (results[0])


def show_tracks(_results):
    for item in _results:
        track = item["track"]
        print("%32.32s %s" % (track["artists"][0]["name"], track["name"]))


def get_all_saved_tracks(_sp):
    print("Retreiving all tracks")
    done = False
    offset = 0
    results = []
    total = 0
    while done == False:
        result = _sp.current_user_saved_tracks(limit=50, offset=offset)
        if total == 0:
            total = result["total"]
        for item in result["items"]:
            track = item["track"]
            # print (track['name'].ljust(30), "by", track['artists'][0]['name'])
        results += result["items"]
        offset += 50
        if offset >= total:
            done = True
            offset -= 50
            leftovers = total - offset
            if leftovers > 0:
                results += _sp.current_user_saved_tracks(
                    limit=leftovers, offset=offset
                )["items"]
            break
        print(offset, "/", total, end="\r")
        sleep(50 / 1000)
    print(offset + leftovers, "/", total)

    save_results(results)
    # show_tracks(results)

    return results


def save_results(_results):
    with open("results.json", "w") as file:
        file.write(json.dumps(_results))


def load_results():
    try:
        with open("results.json", "r") as file:
            data = json.load(file)
        return data
    except:
        return False


if __name__ == "__main__":
    main()
