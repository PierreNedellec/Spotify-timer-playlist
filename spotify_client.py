import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "playlist-modify-private"
REDIRECT_URI = "http://127.0.0.1:8888/callback"


def get_client():
    load_dotenv()
    auth = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth)


def create_timed_playlist(sp, track_ids, minutes, genre):
    playlist = sp.current_user_playlist_create(
        name=f"{genre.title()} - {minutes}min",
        public=False,
        description=f"Timer playlist: {minutes} minutes of {genre}.",
    )
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist["id"], track_ids[i:i + 100])
    return playlist["external_urls"]["spotify"]