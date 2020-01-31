from main import tracks_file, analysis_file, load_json, save_json
from definitions import ARTIST_CATEGORIES


def main():
    artists = get_all_uncategorized_artists()
    categories = ARTIST_CATEGORIES.keys()

    count = 0
    interface = "--------------------\n"
    interface += "[00]: SKIP\n"
    opts = []
    for category in categories:
        count += 1
        opts.append(category)
        interface += f"[{str(count).zfill(2)}]: {category}\n"

    print(interface)

    answers = {}
    for artist in artists:
        opt = input(f"\rArtist => {artist}: ")
        if opt != "0" and opt != "q" and opt != "":
            answers[artist] = opts[int(opt)]
        elif opt == "q":
            break

    add_new_categorized_artists(answers)


def get_all_uncategorized_artists():
    all_tracks = load_json(tracks_file)
    all_categorized = load_json(analysis_file)

    all_artists = []
    for track in all_tracks:
        artist = track["track"]["artists"][0]["name"]
        if artist not in all_artists:
            all_artists.append(artist)

    categorized_artists = []
    for category in all_categorized.keys():
        for track in all_categorized[category]:
            artist = track["track"]["artists"][0]["name"]
            if artist not in categorized_artists:
                categorized_artists.append(artist)

    uncategorized_artists = []
    for artist in all_artists:
        if artist not in categorized_artists:
            uncategorized_artists.append(artist)

    return uncategorized_artists


def add_new_categorized_artists(_answers):
    for answer in _answers.keys():
        category = _answers[answer]
        artist = answer


if __name__ == "__main__":
    main()
