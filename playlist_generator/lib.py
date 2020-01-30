def analyze_track_list():
    pass


def update_analyzation():
    pass


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
