import sys
import lastFM
import spotifyAPI
import json
from database import *

print("***** SPECTRUM CRAWLER *****")
print("")

if (len(sys.argv) < 3):
    sys.exit("Missing parameters")
elif (not sys.argv[1].isdigit() or not sys.argv[2].isdigit()):
    sys.exit("Bad parameter type")
else:
    print("Step 1 --- lastFM extraction")

    lastFM_songs = []
    songs = []
    max_genres = int(sys.argv[1])
    songs_per_genre = int(sys.argv[2])

    # get genres
    genres = lastFM.get_genres(max_genres)

    print(str(len(genres)) + " genres retrieved")

    # get songs
    for genre in genres:
        extraction = lastFM.get_songs_per_genre(genre, [], 1, songs_per_genre)
        lastFM_songs = lastFM_songs + extraction

    print(str(len(lastFM_songs)) + " songs retrieved")

    print("")
    print("Step 2 --- Spotify extraction")
    for song in lastFM_songs:
        s = spotifyAPI.search_song(song['title'], song['artist'])
        if (s is not False):
            s['genre'] = song['genre']
            songs.append(s)

    print(str(len(songs)) + " songs retrieved")
    if (len(songs) < len(lastFM_songs)):
        print(str(len(lastFM_songs) - len(songs)) + " songs lost in conversion")

    with open('songs.json', 'w') as outfile:
        json.dump(songs, outfile)


print("")
print("Step 3 --- Database insertion")
with open('songs.json') as json_file:
    jsonObject = json.load(json_file)
connect()

# print the keys and values
for song in jsonObject:
    id_song = insert_song(song['title'], song['artist'], song['genre'])
    for primitive, value in song['primitives'].items():
        insert_song_primitive(id_song, primitive, value)

disconnect()
print("")
print("DONE !")
print("")
