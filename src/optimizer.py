import pandas as pd
import numpy as np

posts = pd.read_csv("data/posts.csv")
campaigns = pd.read_csv("data/campaigns.csv")
ladders = pd.read_csv("data/historical_ladders.csv")
creators = pd.read_csv("data/creators.csv")
print("CREATOR COLUMNS:", creators.columns.tolist())
print(creators.head())

if __name__ == "__main__":
    print("DATA LOADED SUCCESSFULLY")
    print("Posts:", len(posts))
    print("Campaigns:", len(campaigns))
    print("Milestones:", len(ladders))

def calculate_payout(views, ladder):

    achieved = ladder[ladder["view_threshold"] <= views]

    if achieved.empty:
        return 0

    return achieved.iloc[-1]["payout_amount"]


if __name__ == "__main__":
    test_ladder = ladders[ladders["campaign_id"] == "C001"]

    print("Payout for 12000 views:",
          calculate_payout(12000, test_ladder))
    posts["calculated_payout"] = 0

    for campaign_id in campaigns["campaign_id"]:

        ladder = ladders[ladders["campaign_id"] == campaign_id]
        ladder = ladder.sort_values("view_threshold")

        mask = posts["campaign_id"] == campaign_id

        posts.loc[mask, "calculated_payout"] = posts.loc[mask, "views_final"].apply(
            lambda views: calculate_payout(views, ladder)
        )

    print("\nCALCULATED PAYOUTS")
    print(posts[["post_id", "views_final", "calculated_payout"]].head(10))

def generate_candidate_ladder(campaign_id):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ]

    if campaign.empty:
        print("Campaign not found")
        return pd.DataFrame()

    campaign = campaign.iloc[0]

    # Existing ladder is used for comparison
    existing_ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].sort_values("milestone_rank").copy()

    if existing_ladder.empty:
        print("No milestone structure found")
        return pd.DataFrame()

    # Exclude the campaign being evaluated
    training_posts = posts[
        posts["campaign_id"] != campaign_id
    ].copy()

    # Attach campaign category to historical posts
    training_posts = training_posts.merge(
        campaigns[["campaign_id", "category", "platform"]],
        on="campaign_id",
        suffixes=("", "_campaign")
    )

    # Select comparable campaigns
    comparable = training_posts[
        (training_posts["category"] == campaign["category"]) &
        (training_posts["platform"] == campaign["platform"])
    ]

    # Exclude suspicious posts when the flag is available
    if "flagged_suspicious" in comparable.columns:
        comparable = comparable[
            ~comparable["flagged_suspicious"].astype(bool)
        ]

    # Fallback if the comparable group is too small
    if len(comparable) < 10:

        comparable = training_posts[
            training_posts["platform"] == campaign["platform"]
        ]

        if "flagged_suspicious" in comparable.columns:
            comparable = comparable[
                ~comparable["flagged_suspicious"].astype(bool)
            ]

    if comparable.empty:
        print("Insufficient training data")
        return pd.DataFrame()

    historical_views = comparable["views_final"].dropna()

    milestone_count = len(existing_ladder)

    percentiles = np.linspace(
        0.25, 0.90, milestone_count
    )

    thresholds = np.quantile(
        historical_views,
        percentiles
    ).round().astype(int)

    # Ensure thresholds are strictly increasing
    for i in range(1, len(thresholds)):
        thresholds[i] = max(
            thresholds[i],
            thresholds[i - 1] + 1
        )

    candidate_ladder = existing_ladder.copy()

    candidate_ladder["view_threshold"] = thresholds

    candidate_ladder = candidate_ladder.sort_values(
        "view_threshold"
    ).reset_index(drop=True)

    print("\nIMPROVED CANDIDATE LADDER")
    print("Campaign:", campaign_id)
    print("Training posts:", len(comparable))
    print("Target campaign excluded from training: Yes")

    print(
        candidate_ladder[
            ["campaign_id", "view_threshold", "payout_amount"]
        ].to_string(index=False)
    )

    return candidate_ladder
def optimize_payouts(campaign_id, candidate_ladder):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ].iloc[0]

    budget = campaign["total_budget"]

    training_posts = posts[
        posts["campaign_id"] != campaign_id
    ].copy()

    training_posts = training_posts.merge(
        campaigns[["campaign_id", "category", "platform"]],
        on="campaign_id",
        suffixes=("", "_campaign")
    )

    training_posts = training_posts[
        (training_posts["category"] == campaign["category"]) &
        (training_posts["platform"] == campaign["platform"])
    ]

    if "flagged_suspicious" in training_posts.columns:
        training_posts = training_posts[
            ~training_posts["flagged_suspicious"].astype(bool)
        ]

    if training_posts.empty:
        print("No suitable training data")
        return candidate_ladder

    rng = np.random.default_rng(42)

    campaign_size = 15
    simulations = 1000

    best_ladder = None
    best_scale = 0

    for scale in [0.25, 0.50, 0.75, 1.00, 1.25, 1.50]:

        test_ladder = candidate_ladder.copy()

        test_ladder["payout_amount"] = (
            test_ladder["payout_amount"] * scale
        ).round().astype(int)

        simulated_costs = []

        for _ in range(simulations):

            sample = training_posts["views_final"].sample(
                n=campaign_size,
                replace=True,
                random_state=int(rng.integers(0, 1000000))
            )

            total_cost = sum(
                calculate_payout(views, test_ladder)
                for views in sample
            )

            simulated_costs.append(total_cost)

        p95_cost = np.percentile(simulated_costs, 95)

        print(
            f"Scale: {scale:.2f} | "
            f"95th percentile cost: {p95_cost:.0f}"
        )

        if p95_cost <= budget and scale > best_scale:

            best_scale = scale
            best_ladder = test_ladder.copy()

    if best_ladder is None:
        print("No feasible payout structure found")
        return candidate_ladder

    print("\nOPTIMIZED PAYOUT LADDER")
    print("Selected payout scale:", best_scale)

    print(
        best_ladder[
            ["campaign_id", "view_threshold", "payout_amount"]
        ].to_string(index=False)
    )

    return best_ladder
def analyze_tier_reachability(campaign_id, candidate_ladder):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ].iloc[0]

    training_posts = posts[
        posts["campaign_id"] != campaign_id
    ].copy()

    training_posts = training_posts.merge(
        campaigns[["campaign_id", "category", "platform"]],
        on="campaign_id",
        suffixes=("", "_campaign")
    )

    training_posts = training_posts[
        (training_posts["category"] == campaign["category"]) &
        (training_posts["platform_campaign"] == campaign["platform"])
    ]

    training_posts = training_posts.merge(
        creators[["creator_id", "tier"]],
        on="creator_id",
        how="left"
    )

    training_posts = training_posts[
        ~training_posts["flagged_suspicious"].astype(bool)
    ]

    print("\n===== CREATOR TIER REACHABILITY =====")

    print("Campaign:", campaign_id)
    print("Target Tier:", campaign["target_creator_tier"])
    print("Training Posts:", len(training_posts))

    results = []

    for tier, group in training_posts.groupby("tier"):

        row = {
    "tier": tier,
    "sample_posts": len(group)
}

        for rank, threshold in enumerate(
            candidate_ladder["view_threshold"],
            start=1
        ):

            reachability = (
                group["views_final"] >= threshold
            ).mean() * 100

            row[f"milestone_{rank}_reach_pct"] = round(
                reachability, 2
            )

        results.append(row)

    reachability_df = pd.DataFrame(results)

    print("\nREACHABILITY BY CREATOR TIER")

    print(reachability_df.to_string(index=False))

    return reachability_df

if __name__ == "__main__":
    candidate_ladder = generate_candidate_ladder("C001")
    candidate_ladder = optimize_payouts(
        "C001",
        candidate_ladder
    )
    reachability = analyze_tier_reachability(
        "C001",
        candidate_ladder
    )
    print("\nCAMPAIGN C001 DETAILS")

    campaign_details = campaigns[
        campaigns["campaign_id"] == "C001"
    ]

    print(campaign_details.to_string(index=False))

    print("\nTOTAL POSTS FOR C001:")

    print(
        len(posts[posts["campaign_id"] == "C001"])
    )
    # BUDGET EVALUATION

    campaign_id = "C001"

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ].copy()

    existing_ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].sort_values("view_threshold")

    candidate_ladder = candidate_ladder.sort_values(
        "view_threshold"
    )

    # Calculate payout using existing ladder

    campaign_posts["existing_payout"] = campaign_posts[
        "views_final"
    ].apply(
        lambda views: calculate_payout(views, existing_ladder)
    )

    # Calculate payout using candidate ladder

    campaign_posts["candidate_payout"] = campaign_posts[
        "views_final"
    ].apply(
        lambda views: calculate_payout(views, candidate_ladder)
    )

    # Calculate total costs

    existing_cost = campaign_posts["existing_payout"].sum()

    candidate_cost = campaign_posts["candidate_payout"].sum()

    budget = campaigns.loc[
        campaigns["campaign_id"] == campaign_id,
        "total_budget"
    ].iloc[0]

    print("\n===== BUDGET EVALUATION =====")

    print("Campaign Budget:", budget)

    print("Existing Ladder Cost:", existing_cost)

    print("Candidate Ladder Cost:", candidate_cost)

    print("Existing Budget Remaining:", budget - existing_cost)

    print("Candidate Budget Remaining:", budget - candidate_cost)

    print("\n===== COMPARISON =====")

    print("Cost Difference:", candidate_cost - existing_cost)

    print("Candidate Within Budget:", candidate_cost <= budget)
