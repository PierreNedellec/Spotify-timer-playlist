import pandas as pd
import requests
import base64

# MAKING THE PLAYLIST
df = pd.read_csv("spotify-tracks.csv")

target_min = int(input("How long should the playlist be in minutes? "))
target_ms = target_min*60*1000
min_ms = 90 * 1000  
max_ms = 7 * 60 * 1000 
filtered_df = df[(df["duration_ms"] >= min_ms) & (df["duration_ms"] <= max_ms) & (df["popularity"] > 80) & (df["track_genre"] == "pop")]

tracks = list(zip(filtered_df["track_id"], filtered_df["duration_ms"]))
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
while abs(difference) > 100: # Acceptable margin of error in ms
    next_track_length = tracks[0][1]
    tracks.append(playlist.pop(playlist.index(shouldBeSwapped(playlist,next_track_length + difference))))
    playlist.append(tracks.pop(0))
    difference = time(playlist) - target_ms
    print(time(playlist)/60000)

lookup = df.set_index("track_id")

for item in playlist:
    row = lookup.loc[item[0]]
    print(f"{row['track_name']}, {row['artists']}")


# WRITING THE PLAYLIST OT SPOTIFY

CLIENT_ID = "41769ddb18cc4fe8828383daa95eedfc"
CLIENT_SECRET = "6068e30d28214a72bc6efcc2c1e83e36"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

def get_access_token(code):
    auth_b64 = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )  
    print(response.text)  
    response.raise_for_status()
    return response.json()["access_token"]

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
code = "AQDPlx02MRYeqfpbCEaMUc8DKq7nrZmRXKwMMf4EwBKc1Ir7f7z_O9IqaiBRGvLfkSbTa7dlt8x8UaR2uJHgWDCRFbgtzyh9FFawDYGubDpaBB6ITzmsdYqVgFlupE_ZoingR0o77o2gQRYNOAFa7fFtfUb4N076U2Bne7THDF4hbrYcnwdZ5BXaBYX-6AVKb_sqiDhEdQ4XjIrXefpNWav8cIUppzpwETZ4NiIW-I6qCTqYE3PNo9sesbYgVElQ-uclpC47hGH4tdTzIO2BXjgzYxzYAnX9QEc"
access_token = get_access_token(code)
user_id = get_user_id(access_token)
spotifyPlaylist = create_playlist(access_token, target_min)

print(spotifyPlaylist["external_urls"]["spotify"])

uris = [f"spotify:track:{track_id}" for track_id, duration in playlist]
add_tracks(access_token, spotifyPlaylist["id"], uris)