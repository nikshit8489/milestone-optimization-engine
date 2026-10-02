import pandas as pd

posts = pd.read_csv("data/posts.csv")
creators = pd.read_csv("data/creators.csv")

data = posts.merge(creators, on="creator_id")

print("VIEW DISTRIBUTION BY CREATOR TIER")

result = data.groupby("tier")["views_final"].agg(
    ["count", "median", "mean"]
)

print(result.round(0))

print("\nVIEW PERCENTILES")

print(data.groupby("tier")["views_final"].quantile(
    [0.50, 0.75, 0.90]
).unstack().round(0))