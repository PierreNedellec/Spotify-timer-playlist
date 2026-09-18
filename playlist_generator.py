import pandas as pd

df = pd.read_csv("spotify-tracks.csv")

target_min = int(input("How long should the playlist be in minutes? "))
target_ms = target_min*60*1000
#First version: random sample --> then selected to fill a determined time
sample = df.sample(target_min*5)

tracks = list(zip(sample["track_id"], sample["duration_ms"]))
playlist = []

def time(pl):
    playlist_time = 0
    for item in pl:
        playlist_time += item[1]
    return playlist_time

while time(playlist) < target_ms:
    playlist.append(tracks.pop(0))

def shouldBeSwapped(pl,duration_target):
    best = ['',-999999]
    for item in pl:
        if abs(item[1]-duration_target) < abs(best[1]-duration_target):
            best = item
    return best

while time(playlist) != target_ms:
    difference = time(playlist) - target_ms
    next_track_length = tracks[0][1]
    tracks.append(playlist.pop(playlist.index(shouldBeSwapped(playlist,next_track_length + difference))))
    playlist.append(tracks.pop(0))
    print(time(playlist)/60000)


print(playlist)
print(time(playlist)/60000)