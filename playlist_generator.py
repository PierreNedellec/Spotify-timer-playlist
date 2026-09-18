import pandas as pd

df = pd.read_csv("spotify-tracks.csv")

target_min = int(input("How long should the playlist be in minutes? "))
target_ms = target_min*60*1000
min_ms = 90 * 1000  
max_ms = 7 * 60 * 1000 
resulting_df = df[(df["duration_ms"] >= min_ms) & (df["duration_ms"] <= max_ms) & (df["popularity"] > 80)]
sample = resulting_df.sample(target_min*5)

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

difference = time(playlist) - target_ms
while abs(difference) > 1000: # Acceptable margin of error in ms
    next_track_length = tracks[0][1]
    tracks.append(playlist.pop(playlist.index(shouldBeSwapped(playlist,next_track_length + difference))))
    playlist.append(tracks.pop(0))
    difference = time(playlist) - target_ms
    print(time(playlist)/60000)

lookup = df.set_index("track_id")

for item in playlist:
    row = lookup.loc[item[0]]
    print(f"{row['track_name']}, {row['artists']}")