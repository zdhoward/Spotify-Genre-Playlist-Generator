one = {"Hip-Hop": [{"artist": "artist1", "song": "song1", "id": "id1"}]}
two = {
    "Hip-Hop": [{"artist": "artist2", "song": "song2", "id": "id2"}],
    "Rock": [{"artist": "artist22", "song": "song22", "id": "id22"}],
}

three = {**one, **two}

for genre in one.keys():
    if genre not in three.keys():
        three[genre] = []

    three[genre] = one[genre] + two[genre]

print("One:", one)
print("Two:", two)
print("Three:", three)
