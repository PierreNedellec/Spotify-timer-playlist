import pandas as pd
import spotify_client
import solver


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

def format_duration(total_seconds):
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}" 

def main():
    df = pd.read_csv("data/spotify-tracks.csv")

    target_min = ask_minutes()
    target_s = target_min*60
    genre = ask_genre(sorted(df["track_genre"].unique()))
    min_ms = 90 * 1000  
    max_ms = 10 * 60 * 1000 
    filtered_df = df[(df["duration_ms"] >= min_ms) & (df["duration_ms"] <= max_ms) & (df["popularity"] > 40) & (df["track_genre"] == genre)]

    tracks = [(track_id, round(d / 1000)) for track_id, d in zip(filtered_df["track_id"], filtered_df["duration_ms"])]

    print(f"Number of tracks selected: {len(tracks)}")
    playlist_ids, playlist_time = solver.design_playlist(tracks, target_s)

    if not playlist_ids:
        print("No combination of songs fits. Try a longer time or another genre.")
        return

    print(f"Created a playlist of time {format_duration(playlist_time)}")
    gap = abs(playlist_time - target_s)
    if gap > 30:
        print(f"Warning: that's {format_duration(gap)} off your target. "
            "This genre may not have enough songs.")

    sp = spotify_client.get_client()
    url = spotify_client.create_timed_playlist(sp, playlist_ids, target_min, genre)
    print(f"Your playlist: {url}")


if __name__ == "__main__":
    main()