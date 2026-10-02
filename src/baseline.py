import pandas as pd

campaigns = pd.read_csv("data/campaigns.csv")
posts = pd.read_csv("data/posts.csv")

baseline = posts.groupby("campaign_id")["total_payout_earned"].sum()

campaigns["actual_payout"] = campaigns["campaign_id"].map(baseline)

campaigns["budget_used_pct"] = (
    campaigns["actual_payout"] / campaigns["total_budget"] * 100
)

print(campaigns[[
    "campaign_id",
    "total_budget",
    "actual_payout",
    "budget_used_pct"
]].head(10))
print("\nOVERALL BASELINE")
print("Total Budget:", campaigns["total_budget"].sum())
print("Total Payout:", campaigns["actual_payout"].sum())
print("Average Budget Used:", round(campaigns["budget_used_pct"].mean(), 2), "%")