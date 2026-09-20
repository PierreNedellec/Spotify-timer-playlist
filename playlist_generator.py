import pandas as pd
import requests
import base64
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()
import os


# MAKING THE PLAYLIST
df = pd.read_csv("data/spotify-tracks.csv")

target_min = int(input("How long should the playlist be in minutes? "))
target_ms = target_min*60*1000
min_ms = 90 * 1000  
max_ms = 7 * 60 * 1000 
filtered_df = df[(df["duration_ms"] >= min_ms) & (df["duration_ms"] <= max_ms) & (df["popularity"] > 80) & (df["track_genre"] == "house")]

tracks_duration_ms = list(zip(filtered_df["track_id"], filtered_df["duration_ms"], filtered_df["energy"]))
tracks = []
for id,duration,energy in tracks_duration_ms:
    tracks.append((id,round(duration/1000),energy)) 

print(tracks)

playlist = []

possible_times = {0:[]}
for track in tracks:
    print(f"Operating on track {tracks.index(track)+1}/{len(tracks)}.")
    for time in possible_times.copy().keys():
        if time > target_min*60*1.1:
            continue
        new_time = time + track[1]
        if track[0] in possible_times[time]:
            continue
        new_track_path = possible_times[time]+[track[0]]
        possible_times.update({new_time:new_track_path})

best_time = min(possible_times.keys(), key= lambda x: abs(x-target_min*60))
print(f"Playlist time: {best_time}")
playlist = possible_times[best_time]


lookup = filtered_df.set_index("track_id")

for track_id in playlist:
    row = lookup.loc[track_id]
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


access_token = get_access_token()
user_id = get_user_id(access_token)
spotifyPlaylist = create_playlist(access_token, target_min)

print(spotifyPlaylist["external_urls"]["spotify"])

uris = [f"spotify:track:{track_id}" for track_id in playlist]
add_tracks(access_token, spotifyPlaylist["id"], uris)