#!/usr/bin/env python3
from main import (
    tracks_file,
    analysis_file,
    load_json,
    save_json,
    analyze_track_list,
    run,
)
from definitions import ARTIST_CATEGORIES


def main():
    manage()


def manage():
    artists = get_all_uncategorized_artists()
    categories = ARTIST_CATEGORIES.keys()

    count = 0
    interface = "--------------------\n"
    interface += "[00]: SKIP\n"
    opts = ["SKIP"]
    for category in categories:
        if category != "IGNORE":
            count += 1
            opts.append(category)
            # interface += f"[~~]: {category}"
            # else:
            interface += f"[{str(count).zfill(2)}]: {category}\n"

    for category in categories:
        if category == "IGNORE":
            interface += f"[~~]: {category}"
            opts.append(category)

    print(interface)

    answers = {}
    for artist in artists:
        opt = input(f"\rArtist => {artist}: ")
        if "~" in str(opt):
            opt = len(opts) - 1
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
        artist = track["artists"][0]["name"]
        if artist not in all_artists:
            all_artists.append(artist)

    categorized_artists = []
    for category in all_categorized.keys():
        for track in all_categorized[category]:
            artist = track["artists"][0]["name"]
            if artist not in categorized_artists:
                categorized_artists.append(artist)

    uncategorized_artists = []
    for artist in all_artists:
        if artist not in categorized_artists:
            uncategorized_artists.append(artist)

    return sorted(uncategorized_artists)


def add_new_categorized_artists(_answers):
    categories = {}
    for answer in _answers.keys():
        category = _answers[answer]
        artist = answer

        if category not in categories.keys():
            categories[category] = []
        categories[category].append(artist)
    add_definitions(categories)


def add_definitions(_definitions):
    data = ARTIST_CATEGORIES
    print("Adding:")
    print(_definitions)
    ans = input("Would you like to continue to add these? (y/n): ")
    if ans != "":
        if ans.strip()[0].lower() == "y":
            ## add whatever to the definitions here

            merged = {}
            for key in ARTIST_CATEGORIES.keys():
                if key in _definitions.keys():
                    ARTIST_CATEGORIES[key] += _definitions[key]

            # print("Merged:")
            # print(ARTIST_CATEGORIES)

            # format file contents
            contents = ["ARTIST_CATEGORIES = {"]
            for category in ARTIST_CATEGORIES.keys():
                contents.append(f'\t"{category}": [')
                artists_per_category = []
                for item in ARTIST_CATEGORIES[category]:
                    if item not in artists_per_category:
                        artists_per_category.append(item)
                        contents.append(f'\t\t"{item}",')
                contents.append("\t],")
            contents.append("}")
            # print(contents)

            # write file
            file = open("definitions.py", "w")
            # file.writelines(contents)
            for line in contents:
                file.write(line + "\n")
            file.close()

            # run()
            track_list = load_json(tracks_file)
            analyze_track_list(track_list)


if __name__ == "__main__":
    main()
    # load_definitions()
    # from test_definitions import ARTIST_CATEGORIES as AC
