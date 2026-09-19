import pandas as pd

df = pd.read_csv("spotify-tracks.csv")

genres = sorted(df["track_genre"].unique())
print(len(genres))
print(genres)