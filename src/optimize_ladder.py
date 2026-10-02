import pandas as pd

campaigns = pd.read_csv("data/campaigns.csv")
posts = pd.read_csv("data/posts.csv")
ladders = pd.read_csv("data/historical_ladders.csv")


def inspect_campaign(campaign_id):

    campaign_data = campaigns[
        campaigns["campaign_id"] == campaign_id
    ]

    if campaign_data.empty:
        print("Campaign not found")
        return

    campaign = campaign_data.iloc[0]

    print("\n===== CAMPAIGN DETAILS =====")

    print("Campaign ID:", campaign_id)
    print("Brand:", campaign["brand"])
    print("Budget:", campaign["total_budget"])
    print("Target Tier:", campaign["target_creator_tier"])

    ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].sort_values("view_threshold")

    print("\n===== EXISTING MILESTONE LADDER =====")

    print(
        ladder[
            ["milestone_rank", "view_threshold", "payout_amount"]
        ].to_string(index=False)
    )

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ]

    print("\n===== HISTORICAL PERFORMANCE =====")

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


if __name__ == "__main__":
    inspect_campaign("C001")