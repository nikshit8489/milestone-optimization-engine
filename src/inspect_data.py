import pandas as pd

files = ["campaigns", "creators", "posts", "historical_ladders"]

for file in files:
    df = pd.read_csv(f"data/{file}.csv")

    print(f"\n--- {file.upper()} ---")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print(df.head(2).to_string(index=False))