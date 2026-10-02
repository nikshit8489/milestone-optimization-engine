
import pandas as pd
import numpy as np
from datetime import date, timedelta


rng = np.random.default_rng(42)


NUM_CAMPAIGNS = 30
NUM_CREATORS = 300
POSTS_PER_CAMPAIGN = 15

categories = ["gaming", "FMCG", "finance", "D2C", "entertainment"]
platforms = ["instagram", "youtube"]
formats = ["reel", "short", "long_form", "carousel"]


def get_creator_tier(followers):
    if followers < 10000:
        return "nano"
    elif followers < 100000:
        return "micro"
    elif followers < 1000000:
        return "mid"
    else:
        return "macro"



# CREATOR GENERATION
creators = []

tier_distribution = {
    "nano": 120,
    "micro": 105,
    "mid": 60,
    "macro": 15
}

tier_ranges = {
    "nano": (1000, 9999),
    "micro": (10000, 99999),
    "mid": (100000, 999999),
    "macro": (1000000, 3000000)
}

creator_number = 1

for tier, count in tier_distribution.items():

    min_followers, max_followers = tier_ranges[tier]

    for _ in range(count):

        followers = int(
            rng.integers(min_followers, max_followers + 1)
        )

        avg_views = int(
            followers * rng.uniform(0.05, 0.8)
        )

        creators.append({
            "creator_id": f"CR{creator_number:04d}",
            "platform": rng.choice(platforms),
            "follower_count": followers,
            "tier": tier,
            "account_age_months": int(rng.integers(6, 120)),
            "historical_avg_views_per_post": avg_views,
            "historical_completion_rate": round(
                rng.uniform(0.1, 0.9), 2
            )
        })

        creator_number += 1

creators_df = pd.DataFrame(creators)


# CAMPAIGN GENERATION
campaigns = []
historical_ladders = []

for i in range(NUM_CAMPAIGNS):
    campaign_id = f"C{i+1:03d}"
    budget = int(rng.choice([50000, 75000, 100000, 150000, 200000]))

    campaigns.append({
        "campaign_id": campaign_id,
        "brand": f"Brand_{i+1}",
        "category": rng.choice(categories),
        "platform": rng.choice(platforms),
        "total_budget": budget,
        "start_date": date(2026, 1, 1) + timedelta(days=i * 7),
        "end_date": date(2026, 1, 8) + timedelta(days=i * 7),
        "target_creator_tier": rng.choice(
            ["nano", "micro", "mid", "macro"]
        )
    })

    thresholds = [10000, 50000, 100000, 500000]
    payouts = [
        int(budget * 0.005),
        int(budget * 0.02),
        int(budget * 0.05),
        int(budget * 0.15)
    ]

    for rank, (views, payout) in enumerate(
        zip(thresholds, payouts), start=1
    ):
        historical_ladders.append({
            "campaign_id": campaign_id,
            "milestone_rank": rank,
            "view_threshold": views,
            "payout_amount": payout
        })

campaigns_df = pd.DataFrame(campaigns)
ladders_df = pd.DataFrame(historical_ladders)


# Post generation based on campaign and creator data
posts = []

category_multiplier = {
    "gaming": 1.2,
    "FMCG": 1.0,
    "finance": 0.7,
    "D2C": 0.9,
    "entertainment": 1.3
}

for _, campaign in campaigns_df.iterrows():

    eligible_creators = creators_df[
        creators_df["platform"] == campaign["platform"]
    ]

    selected = eligible_creators.sample(
        n=min(POSTS_PER_CAMPAIGN, len(eligible_creators)),
        random_state=int(rng.integers(0, 100000))
    )

    for _, creator in selected.iterrows():

        base_views = creator["historical_avg_views_per_post"]

        multiplier = category_multiplier[campaign["category"]]

        final_views = int(
            rng.lognormal(
                mean=np.log(max(1, base_views * multiplier)),
                sigma=0.8
            )
        )

        suspicious = rng.random() < 0.05

        if suspicious:
            final_views *= int(rng.integers(3, 8))

        views_24h = int(final_views * rng.uniform(0.15, 0.35))
        views_7d = int(final_views * rng.uniform(0.55, 0.80))
        views_30d = final_views

        posts.append({
            "post_id": f"P{len(posts)+1:05d}",
            "campaign_id": campaign["campaign_id"],
            "creator_id": creator["creator_id"],
            "post_date": campaign["start_date"],
            "platform": campaign["platform"],
            "format": rng.choice(formats),
            "views_at_24h": views_24h,
            "views_at_7d": views_7d,
            "views_at_30d": views_30d,
            "views_final": final_views,
            "total_payout_earned": 0,
            "flagged_suspicious": suspicious
        })

posts_df = pd.DataFrame(posts)


# Calculation of historical payouts
for i, post in posts_df.iterrows():

    ladder = ladders_df[
        ladders_df["campaign_id"] == post["campaign_id"]
    ]

    achieved = ladder[
        ladder["view_threshold"] <= post["views_final"]
    ]

    if not achieved.empty:
        posts_df.at[i, "total_payout_earned"] = (
            achieved["payout_amount"].iloc[-1]
        )


# Save datasets
campaigns_df.to_csv("data/campaigns.csv", index=False)
creators_df.to_csv("data/creators.csv", index=False)
posts_df.to_csv("data/posts.csv", index=False)
ladders_df.to_csv("data/historical_ladders.csv", index=False)

print("Synthetic dataset generated successfully!")
print(f"Campaigns: {len(campaigns_df)}")
print(f"Creators: {len(creators_df)}")
print(f"Posts: {len(posts_df)}")
print(f"Historical milestone records: {len(ladders_df)}")