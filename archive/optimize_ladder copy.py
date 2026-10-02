import pandas as pd
import numpy as np

campaigns = pd.read_csv("data/campaigns.csv")
posts = pd.read_csv("data/posts.csv")
ladders = pd.read_csv("data/historical_ladders.csv")

print("DATA LOADED SUCCESSFULLY")

print("Campaigns:", len(campaigns))
print("Posts:", len(posts))
print("Historical Milestones:", len(ladders))

print("\nCAMPAIGN COLUMNS:")
print(campaigns.columns.tolist())

print("\nLADDER COLUMNS:")
print(ladders.columns.tolist())
def inspect_campaign(campaign_id):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ]

    if campaign.empty:
        print("Campaign not found")
        return

    campaign = campaign.iloc[0]

    print("\nCAMPAIGN DETAILS")
    print("Campaign ID:", campaign_id)
    print("Brand:", campaign["brand"])
    print("Budget:", campaign["total_budget"])
    print("Target Creator Tier:", campaign["target_creator_tier"])

    ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].sort_values("view_threshold")

    print("\nEXISTING MILESTONE LADDER")
    print(ladder.to_string(index=False))

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ]

    print("\nHISTORICAL PERFORMANCE")
    print("Total Posts:", len(campaign_posts))

    if not campaign_posts.empty:

        print(
            "Average Views:",
            int(campaign_posts["views_final"].mean())
        )

        print(
            "Median Views:",
            int(campaign_posts["views_final"].median())
        )


inspect_campaign("C001")
def evaluate_current_ladder(campaign_id):

    ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].sort_values("view_threshold")

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ].copy()

    def get_payout(views):

        achieved = ladder[
            ladder["view_threshold"] <= views
        ]

        if achieved.empty:
            return 0

        return achieved.iloc[-1]["payout_amount"]

    campaign_posts["baseline_payout"] = (
        campaign_posts["views_final"].apply(get_payout)
    )

    print("\nBASELINE PAYOUT ANALYSIS")

    print("Campaign:", campaign_id)

    print(
        "Total Historical Payout:",
        campaign_posts["total_payout_earned"].sum()
    )

    print(
        "Calculated Ladder Payout:",
        campaign_posts["baseline_payout"].sum()
    )

    print(
        "Average Payout Per Post:",
        round(campaign_posts["baseline_payout"].mean(), 2)
    )

    print(
        "Posts Receiving Payout:",
        (campaign_posts["baseline_payout"] > 0).sum()
    )


evaluate_current_ladder("C001")
def analyze_budget(campaign_id):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ].iloc[0]

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ]

    budget = campaign["total_budget"]

    total_payout = campaign_posts[
        "total_payout_earned"
    ].sum()

    utilization = (total_payout / budget) * 100

    print("\nBUDGET ANALYSIS")

    print("Campaign:", campaign_id)
    print("Allocated Budget:", budget)
    print("Total Payout:", total_payout)

    print("Budget Utilization:", round(utilization, 2), "%")

    print(
        "Remaining Budget:",
        budget - total_payout
    )


analyze_budget("C001")


def calculate_ladder_payout(views, ladder):

    achieved = ladder[
        ladder["view_threshold"] <= views
    ]

    if achieved.empty:
        return 0

    return achieved.iloc[-1]["payout_amount"]


test_ladder = ladders[
    ladders["campaign_id"] == "C001"
].sort_values("view_threshold")

print("\nPAYOUT FUNCTION TEST")

print(
    "Payout for 12000 views:",
    calculate_ladder_payout(12000, test_ladder)
)

print(
    "Payout for 60000 views:",
    calculate_ladder_payout(60000, test_ladder)
)

def evaluate_proposed_ladder(campaign_id, proposed_ladder):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ].iloc[0]

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ].copy()

    budget = campaign["total_budget"]

    campaign_posts["proposed_payout"] = (
        campaign_posts["views_final"].apply(
            lambda views: calculate_ladder_payout(
                views, proposed_ladder
            )
        )
    )

    total_payout = campaign_posts["proposed_payout"].sum()

    utilization = (total_payout / budget) * 100

    print("\nPROPOSED LADDER EVALUATION")

    print("Campaign:", campaign_id)
    print("Expected Payout:", total_payout)
    print("Campaign Budget:", budget)
    print("Budget Utilization:", round(utilization, 2), "%")
    print("Remaining Budget:", budget - total_payout)

    print(
        "Posts Receiving Payout:",
        (campaign_posts["proposed_payout"] > 0).sum()
    )

    return campaign_posts
test_ladder = ladders[
    ladders["campaign_id"] == "C001"
].sort_values("view_threshold")

evaluate_proposed_ladder("C001", test_ladder)
