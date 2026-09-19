import pandas as pd

RAW_FILE = "spotify-tracks source data.csv"
CLEAN_FILE = "spotify-tracks.csv"

df = pd.read_csv(RAW_FILE)

df = df.drop(columns=["Unnamed: 0"], errors="ignore")

before = len(df)

df = df.drop_duplicates(subset=["track_id", "track_genre"])

df = df.drop_duplicates(subset=["track_name", "artists", "track_genre"])

df.to_csv(CLEAN_FILE, index=False)
print(f"Kept {len(df)} of {before} rows -> {CLEAN_FILE}")