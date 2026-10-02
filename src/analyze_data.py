
import pandas as pd

posts = pd.read_csv("data/posts.csv")

posts["growth_24h_7d"] = (
    posts["views_at_7d"] / posts["views_at_24h"]
)

posts["growth_7d_30d"] = (
    posts["views_at_30d"] / posts["views_at_7d"]
)

print("\nVIEW GROWTH COMPARISON")

print(posts.groupby("flagged_suspicious")[
    ["growth_24h_7d", "growth_7d_30d"]
].mean().round(2))

print("\nPOST COUNTS")
print(posts["flagged_suspicious"].value_counts())