import pandas as pd

df = pd.read_csv("spotify-tracks.csv")

df = df.drop_duplicates(subset="track_id")
df.to_csv("spotify-tracks.csv", index=False)

mask = (
    
)