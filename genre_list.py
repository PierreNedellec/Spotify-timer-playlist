import pandas as pd

df = pd.read_csv("data/spotify-tracks.csv")

genres = sorted(df["track_genre"].unique())
print(len(genres))
print(genres)