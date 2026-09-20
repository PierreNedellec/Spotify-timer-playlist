import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import spotify_client
import solver


# MAKING THE PLAYLIST
def ask_minutes():
    while True:
        try:
            minutes = int(input("How long should the playlist be in minutes? "))
            if minutes > 0:
                return minutes
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a whole number.")

def ask_genre(available_genres):
    while True:
        genre = input("Genre (e.g. house, jazz): ").strip().lower()
        if genre in available_genres:
            return genre
        print(f"Unknown genre. Options: {', '.join(available_genres)}")    

def main():
    df = pd.read_csv("data/spotify-tracks.csv")

    target_min = ask_minutes()
    genre = ask_genre(sorted(df["track_genre"].unique()))
    min_ms = 90 * 1000  
    max_ms = 30 * 60 * 1000 
    filtered_df = df[(df["duration_ms"] >= min_ms) & (df["duration_ms"] <= max_ms) & (df["popularity"] > 40) & (df["track_genre"] == genre)]

    tracks_duration_ms = list(zip(filtered_df["track_id"], filtered_df["duration_ms"]))
    tracks = []
    for id,duration in tracks_duration_ms:
        tracks.append((id,round(duration/1000))) 

    print(f"Number of tracks selected: {len(tracks)}")
    playlist_ids, playlist_time = solver.design_playlist(tracks, target_min)
    print(f"Created a playlist of time {playlist_time//60}:{playlist_time%60:02d}")

    sp = spotify_client.get_client()
    url = spotify_client.create_timed_playlist(sp, playlist_ids, target_min, genre)
    print(f"Your playlist: {url}")


if __name__ == "__main__":
    main()