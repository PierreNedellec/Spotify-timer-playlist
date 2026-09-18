import pandas as pd

df = pd.read_csv("spotify-tracks.csv")

sample = df.sample(n=100, random_state=42)

print(df.head())
print(df.shape)
print(df.dtypes)