import pandas as pd
import requests
import base64
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()
import os


# MAKING THE PLAYLIST
df = pd.read_csv("spotify-tracks.csv")

target_min = int(input("How long should the playlist be in minutes? "))
target_ms = target_min*60*1000
min_ms = 90 * 1000  
max_ms = 7 * 60 * 1000 
filtered_df = df[(df["duration_ms"] >= min_ms) & (df["duration_ms"] <= max_ms) & (df["popularity"] > 10) & (df["track_genre"] == "hardcore")]

tracks = list(zip(filtered_df["track_id"], filtered_df["duration_ms"], filtered_df["energy"]))
playlist = []

def time(pl):
    playlist_time = 0
    for item in pl:
        playlist_time += item[1]
    return playlist_time

def shouldBeSwapped(pl,duration_target): # Swaps the element in the playlist that minimises the difference with the target duration.
    best = ['',-999999]
    for item in pl:
        if abs(item[1]-duration_target) < abs(best[1]-duration_target):
            best = item
    return best

while time(playlist) < target_ms:
    playlist.append(tracks.pop(0))

difference = time(playlist) - target_ms
while abs(difference) > 2000: # Acceptable margin of error in ms
    next_track_length = tracks[0][1]
    tracks.append(playlist.pop(playlist.index(shouldBeSwapped(playlist,next_track_length + difference))))
    playlist.append(tracks.pop(0))
    difference = time(playlist) - target_ms
    print(time(playlist)/60000)

playlist = sorted(playlist, key=lambda x: x[-1], reverse=True)

lookup = df.set_index("track_id")

for item in playlist:
    row = lookup.loc[item[0]]
    print(f"{row['track_name']}, {row['artists']}")


# WRITING THE PLAYLIST OT SPOTIFY
SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

def get_access_token():
    auth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="playlist-modify-private",
    )
    return auth.get_access_token(as_dict=False)

def get_user_id(access_token):
    response = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response.raise_for_status()
    return response.json()["id"]

def create_playlist(access_token, duration):
    response = requests.post(
        "https://api.spotify.com/v1/me/playlists",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"name": f"Playlist {duration}min", "public": False}
    )
    response.raise_for_status()
    return response.json()

def add_tracks(access_token, playlist_id, uris):
    response = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"uris": uris}
    )
    response.raise_for_status()
    return response.json()


# ---- run it ----
code = "AQALHwdL-ZERgFbc5aZDiQ5IPtwuy-KVLq7wAJfrIdSr8CjYBxEn4Iwf-74Krdf-e9ZnLDaSaL1_PFviED9BsNis9GSqjncSUuYVQDM2Yur6CGZ3foP7LLE0bCvM1w77fdMGtwp9GzNw44oe-SXItNJ9tVVs8pqQ_uYvojRBrdZCDyBWZf_3_6kekY6LCxOeHK2JjSi2KGovOdFrm0cEzlvMg6-CkEv66zqWb11ktblNEeZj0WRbWCVHlzj08iiUk_XGg9bx-NfP2t7hL3AtWOQcgKZ4j_-L4y8"
access_token = get_access_token()
user_id = get_user_id(access_token)
spotifyPlaylist = create_playlist(access_token, target_min)

print(spotifyPlaylist["external_urls"]["spotify"])

uris = [f"spotify:track:{item[0]}" for item in playlist]
add_tracks(access_token, spotifyPlaylist["id"], uris)