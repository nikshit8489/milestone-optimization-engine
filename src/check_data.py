import pandas as pd

campaigns = pd.read_csv("data/campaigns.csv")
creators = pd.read_csv("data/creators.csv")
posts = pd.read_csv("data/posts.csv")
ladders = pd.read_csv("data/historical_ladders.csv")

datasets = {
    "Campaigns": campaigns,
    "Creators": creators,
    "Posts": posts,
    "Historical Ladders": ladders
}

for name, df in datasets.items():
    print(f"\n{name}")
    print("Missing values:", df.isnull().sum().sum())
    print("Duplicate rows:", df.duplicated().sum())

print("\nPOST VALIDATION")
print("Negative views:", (posts["views_final"] < 0).sum())
print("Suspicious posts:", posts["flagged_suspicious"].sum())
print("\nCREATOR DATA QUALITY CHECK")

print("Missing Tier Values:")
print(creators["tier"].isna().sum())

print("\nUnique Creator Tiers:")
print(creators["tier"].unique())

print("\nMissing Values Per Column:")
print(creators.isnull().sum())
print("\nTIER VALUE INSPECTION")

print(
    creators["tier"].value_counts(dropna=False)
)

print("\nCHECK STRING NAN:")

print(
    (creators["tier"].astype(str).str.lower() == "nan").sum()
)