
import pandas as pd

# Load datasets
campaigns = pd.read_csv("data/campaigns.csv")
creators = pd.read_csv("data/creators.csv")
posts = pd.read_csv("data/posts.csv")
ladders = pd.read_csv("data/historical_ladders.csv")

CAMPAIGN_ID = "C001"
MIN_SAMPLES = 10

campaign = campaigns[
    campaigns["campaign_id"] == CAMPAIGN_ID
].iloc[0]

# Historical ladder provides payout amounts and milestone count
historical_ladder = ladders[
    ladders["campaign_id"] == CAMPAIGN_ID
].sort_values("milestone_rank")

payouts = historical_ladder["payout_amount"].tolist()
milestone_count = len(payouts)

percentiles = (
    [0.25 + i * (0.65 / (milestone_count - 1))
     for i in range(milestone_count)]
    if milestone_count > 1 else [0.50]
)

# Training data excludes the evaluation campaign
training = posts[
    posts["campaign_id"] != CAMPAIGN_ID
].merge(
    campaigns[["campaign_id", "category", "platform"]],
    on="campaign_id",
    suffixes=("", "_campaign")
)

training = training[
    (training["category"] == campaign["category"]) &
    (training["platform_campaign"] == campaign["platform"])
].copy()

training = training.merge(
    creators[["creator_id", "tier"]],
    on="creator_id",
    how="left"
)

training = training[
    ~training["flagged_suspicious"].astype(bool)
]

if training.empty:
    raise ValueError("No comparable training data found.")


def make_ladder(view_data, tier):

    thresholds = (
        view_data.quantile(percentiles)
        .round()
        .astype(int)
        .tolist()
    )

    for i in range(1, len(thresholds)):
        thresholds[i] = max(
            thresholds[i],
            thresholds[i - 1] + 1
        )

    return pd.DataFrame({
        "milestone_rank": range(1, milestone_count + 1),
        "view_threshold": thresholds,
        "payout_amount": payouts
    })


# Uniform ladder
uniform_ladder = make_ladder(
    training["views_final"].dropna(),
    "uniform"
)

# Tier-specific ladders
tier_ladders = {}

for tier in ["nano", "micro", "mid", "macro"]:

    tier_data = training[
        training["tier"] == tier
    ]["views_final"].dropna()

    if len(tier_data) < MIN_SAMPLES:
        tier_data = training["views_final"].dropna()

    tier_ladders[tier] = make_ladder(
        tier_data,
        tier
    )


# Evaluation on C001 only
evaluation = posts[
    posts["campaign_id"] == CAMPAIGN_ID
].merge(
    creators[["creator_id", "tier"]],
    on="creator_id",
    how="left"
)

evaluation = evaluation[
    ~evaluation["flagged_suspicious"].astype(bool)
]


def evaluate_ladder(data, ladder):

    total_payout = 0
    reach_rates = []

    for _, post in data.iterrows():

        views = post["views_final"]

        achieved = ladder[
            ladder["view_threshold"] <= views
        ]

        if achieved.empty:
            total_payout += 0
        else:
            total_payout += achieved.iloc[-1]["payout_amount"]

    for _, milestone in ladder.iterrows():

        reached = (
            data["views_final"] >= milestone["view_threshold"]
        ).sum()

        rate = (
            reached / len(data) * 100
            if len(data) else 0
        )

        reach_rates.append(round(rate, 2))

    return total_payout, reach_rates


results = []

for tier in ["nano", "micro", "mid", "macro"]:

    tier_posts = evaluation[
        evaluation["tier"] == tier
    ]

    if tier_posts.empty:
        continue

    for method, ladder in [
        ("Uniform", uniform_ladder),
        ("Tier-specific", tier_ladders[tier])
    ]:

        total, rates = evaluate_ladder(
            tier_posts,
            ladder
        )

        results.append({
            "tier": tier,
            "method": method,
            "posts": len(tier_posts),
            "total_payout": total,
            "avg_payout": round(total / len(tier_posts), 2),
            "milestone_reachability": rates
        })


comparison = pd.DataFrame(results)

print("\n===== UNIFORM LADDER =====")
print(uniform_ladder.to_string(index=False))

print("\n===== TIER-SPECIFIC LADDERS =====")

for tier, ladder in tier_ladders.items():
    print(f"\n{tier.upper()}")
    print(ladder.to_string(index=False))

print("\n===== FAIRNESS COMPARISON =====")
print(comparison.to_string(index=False))

print("\n===== TOTAL PAYOUT BY METHOD =====")

print(
    comparison.groupby("method")["total_payout"].sum()
)


def analyze_ladder_quality(ladder, tier):

    ladder = ladder.sort_values("milestone_rank").copy()

    ladder["view_gap"] = (
        ladder["view_threshold"].diff()
    )

    ladder["incremental_payout"] = (
        ladder["payout_amount"].diff()
    )

    # First milestone starts from zero views and zero payout
    ladder.loc[ladder.index[0], "view_gap"] = (
        ladder.iloc[0]["view_threshold"]
    )

    ladder.loc[ladder.index[0], "incremental_payout"] = (
        ladder.iloc[0]["payout_amount"]
    )

    ladder["payout_per_1000_incremental_views"] = (
        ladder["incremental_payout"]
        / ladder["view_gap"]
        * 1000
    )

    print(f"\n===== {tier.upper()} LADDER QUALITY =====")

    print(
        ladder[
            [
                "milestone_rank",
                "view_threshold",
                "payout_amount",
                "view_gap",
                "incremental_payout",
                "payout_per_1000_incremental_views"
            ]
        ].round(2).to_string(index=False)
    )

    if (
        (ladder["view_gap"] <= 0).any()
        or (ladder["incremental_payout"] < 0).any()
    ):
        print("WARNING: Invalid threshold or payout progression.")

    else:
        print("Threshold and payout progression is valid.")


print("\n===== MILESTONE GAP ANALYSIS =====")

analyze_ladder_quality(uniform_ladder, "uniform")

for tier, ladder in tier_ladders.items():
    analyze_ladder_quality(ladder, tier)