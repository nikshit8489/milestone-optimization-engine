
import pandas as pd

creators = pd.read_csv("data/creators.csv")
posts = pd.read_csv("data/posts.csv")

data = posts.merge(
    creators[
        [
            "creator_id",
            "tier",
            "historical_completion_rate"
        ]
    ],
    on="creator_id",
    how="left"
)

# Exclude suspicious posts from fairness analysis
if "flagged_suspicious" in data.columns:
    data = data[
        ~data["flagged_suspicious"].astype(bool)
    ]

performance = data.groupby("tier").agg(
    creators=("creator_id", "nunique"),
    sample_posts=("post_id", "count"),
    avg_views=("views_final", "mean"),
    median_views=("views_final", "median"),
    avg_completion=(
        "historical_completion_rate",
        "mean"
    )
)

print("\n===== CREATOR FAIRNESS ANALYSIS =====")

print(performance.round(2))

print("\n===== SAMPLE SIZE WARNING =====")

print(
    "Small tier samples should be interpreted cautiously."
)

def generate_tier_ladders(campaign_id, min_samples=10):

    campaigns = pd.read_csv("data/campaigns.csv")
    ladders = pd.read_csv("data/historical_ladders.csv")

    campaign_data = campaigns[
        campaigns["campaign_id"] == campaign_id
    ]

    if campaign_data.empty:
        print("Campaign not found")
        return {}

    campaign = campaign_data.iloc[0]

    existing_ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].sort_values("milestone_rank")

    if existing_ladder.empty:
        print("No existing milestone structure")
        return {}

    # Exclude target campaign to prevent data leakage
    training_posts = posts[
        posts["campaign_id"] != campaign_id
    ].copy()

    training_posts = training_posts.merge(
        campaigns[["campaign_id", "category", "platform"]],
        on="campaign_id",
        suffixes=("", "_campaign")
    )

    # Select comparable campaigns
    comparable = training_posts[
        (training_posts["category"] == campaign["category"]) &
        (training_posts["platform_campaign"] == campaign["platform"])
    ].copy()

    # Remove suspicious posts
    if "flagged_suspicious" in comparable.columns:
        comparable = comparable[
            ~comparable["flagged_suspicious"].astype(bool)
        ]

    # Attach creator tier
    comparable = comparable.merge(
        creators[["creator_id", "tier"]],
        on="creator_id",
        how="left"
    )

    if comparable.empty:
        print("No comparable training data")
        return {}

    milestone_count = len(existing_ladder)

    percentiles = [
        0.25 + i * (0.65 / (milestone_count - 1))
        for i in range(milestone_count)
    ] if milestone_count > 1 else [0.50]

    results = {}

    print("\n===== TIER-SPECIFIC MILESTONE LADDERS =====")
    print("Campaign:", campaign_id)

    for tier in ["nano", "micro", "mid", "macro"]:

        tier_posts = comparable[
            comparable["tier"] == tier
        ]

        # Use pooled data when tier sample is too small
        if len(tier_posts) < min_samples:
            print(
                f"\n{tier.upper()}: Insufficient tier data. "
                "Using pooled comparable data."
            )
            selected_posts = comparable
            fallback_used = True
        else:
            selected_posts = tier_posts
            fallback_used = False

        views = selected_posts["views_final"].dropna()

        if views.empty:
            print(f"{tier}: No usable view data")
            continue

        thresholds = (
            views.quantile(percentiles)
            .round()
            .astype(int)
            .tolist()
        )

        # Ensure strictly increasing thresholds
        for i in range(1, len(thresholds)):
            thresholds[i] = max(
                thresholds[i],
                thresholds[i - 1] + 1
            )

        tier_ladder = existing_ladder[
            ["milestone_rank", "payout_amount"]
        ].copy()

        tier_ladder["view_threshold"] = thresholds
        tier_ladder["tier"] = tier

        results[tier] = tier_ladder[
            ["tier", "milestone_rank", "view_threshold", "payout_amount"]
        ]

        print(f"\n--- {tier.upper()} ---")
        print("Training posts used:", len(selected_posts))
        print("Pooled fallback:", fallback_used)
        print(tier_ladder.to_string(index=False))

    return results


tier_ladders = generate_tier_ladders("C001")

def evaluate_tier_reachability(campaign_id, tier_ladders):

    evaluation_posts = posts[
        posts["campaign_id"] == campaign_id
    ].copy()

    evaluation_posts = evaluation_posts.merge(
        creators[["creator_id", "tier"]],
        on="creator_id",
        how="left"
    )

    # Exclude suspicious posts from evaluation
    if "flagged_suspicious" in evaluation_posts.columns:
        evaluation_posts = evaluation_posts[
            ~evaluation_posts["flagged_suspicious"].astype(bool)
        ]

    print("\n===== MILESTONE REACHABILITY =====")
    print("Evaluation Campaign:", campaign_id)

    for tier, ladder in tier_ladders.items():

        tier_data = evaluation_posts[
            evaluation_posts["tier"] == tier
        ]

        print(f"\n--- {tier.upper()} ---")

        print("Evaluation posts:", len(tier_data))

        if tier_data.empty:
            print("No evaluation posts available.")
            continue

        for _, milestone in ladder.iterrows():

            threshold = milestone["view_threshold"]

            reached = (
                tier_data["views_final"] >= threshold
            ).sum()

            reach_rate = (
                reached / len(tier_data)
            ) * 100

            print(
                f"Milestone {int(milestone['milestone_rank'])}: "
                f"{int(threshold):,} views | "
                f"Reached: {reached}/{len(tier_data)} | "
                f"Reach rate: {reach_rate:.2f}%"
            )


evaluate_tier_reachability("C001", tier_ladders)
