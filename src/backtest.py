import pandas as pd

from optimizer import (
    posts,
    campaigns,
    ladders,
    calculate_payout,
    generate_candidate_ladder,
    optimize_payouts,
)


def evaluate_campaign(campaign_id):

    campaign_row = campaigns[
        campaigns["campaign_id"] == campaign_id
    ]

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ].copy()

    existing_ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].copy()

    if campaign_row.empty or campaign_posts.empty or existing_ladder.empty:
        print(f"Skipping {campaign_id}: missing data.")
        return None

    budget = float(campaign_row.iloc[0]["total_budget"])

    # Generate candidate ladder without using target campaign outcomes
    candidate_ladder = generate_candidate_ladder(campaign_id)

    if candidate_ladder is None or candidate_ladder.empty:
        print(f"Skipping {campaign_id}: candidate ladder unavailable.")
        return None

    # Optimize payout structure
    candidate_ladder = optimize_payouts(
        campaign_id,
        candidate_ladder
    )

    if candidate_ladder is None or candidate_ladder.empty:
        print(f"Skipping {campaign_id}: optimization failed.")
        return None

    existing_ladder = existing_ladder.sort_values("view_threshold")
    candidate_ladder = candidate_ladder.sort_values("view_threshold")

    # Evaluate existing payout
    campaign_posts["existing_payout"] = campaign_posts[
        "views_final"
    ].apply(
        lambda views: calculate_payout(
            views,
            existing_ladder
        )
    )

    # Evaluate candidate payout
    campaign_posts["candidate_payout"] = campaign_posts[
        "views_final"
    ].apply(
        lambda views: calculate_payout(
            views,
            candidate_ladder
        )
    )

    # Calculate total costs
    existing_cost = float(
        campaign_posts["existing_payout"].sum()
    )

    candidate_cost = float(
        campaign_posts["candidate_payout"].sum()
    )

    # Calculate highest milestone reachability
    existing_top_threshold = existing_ladder[
        "view_threshold"
    ].max()

    candidate_top_threshold = candidate_ladder[
        "view_threshold"
    ].max()

    existing_top_reach = (
        campaign_posts["views_final"] >= existing_top_threshold
    ).mean() * 100

    candidate_top_reach = (
        campaign_posts["views_final"] >= candidate_top_threshold
    ).mean() * 100

    # Marginal Brand ROI analysis
    total_views = float(
        campaign_posts["views_final"].fillna(0).sum()
    )

    incremental_payout = candidate_cost - existing_cost

    existing_views_per_1000 = (
        total_views / existing_cost * 1000
        if existing_cost > 0
        else None
    )

    candidate_views_per_1000 = (
        total_views / candidate_cost * 1000
        if candidate_cost > 0
        else None
    )

    reach_efficiency_change_pct = (
        (candidate_views_per_1000 - existing_views_per_1000)
        / existing_views_per_1000 * 100
        if existing_views_per_1000 is not None
        and candidate_views_per_1000 is not None
        and existing_views_per_1000 > 0
        else None
    )

    top_milestone_reach_change_pp = (
        candidate_top_reach - existing_top_reach
    )

    return {
        "campaign_id": campaign_id,
        "posts_evaluated": len(campaign_posts),
        "budget": budget,
        "existing_cost": existing_cost,
        "candidate_cost": candidate_cost,

        "existing_budget_used_pct": (
            existing_cost / budget * 100 if budget else 0
        ),
        "candidate_budget_used_pct": (
            candidate_cost / budget * 100 if budget else 0
        ),

        "existing_top_milestone_reach_pct": existing_top_reach,
        "candidate_top_milestone_reach_pct": candidate_top_reach,
        "candidate_within_budget": candidate_cost <= budget,

        # Marginal Brand ROI metrics
        "total_observed_views": total_views,
        "incremental_payout": incremental_payout,
        "existing_views_per_1000": existing_views_per_1000,
        "candidate_views_per_1000": candidate_views_per_1000,
        "reach_efficiency_change_pct": reach_efficiency_change_pct,
        "top_milestone_reach_change_pp": top_milestone_reach_change_pp,
    }


def main():

    # Select up to five campaigns with posts and milestone data
    available_ids = []

    for campaign_id in campaigns["campaign_id"].dropna().astype(str):

        has_posts = (
            posts["campaign_id"].astype(str) == campaign_id
        ).any()

        has_ladder = (
            ladders["campaign_id"].astype(str) == campaign_id
        ).any()

        if has_posts and has_ladder:
            available_ids.append(campaign_id)

        if len(available_ids) == 5:
            break

    print("\n===== BACKTEST: UP TO FIVE CAMPAIGNS =====")
    print("Each target campaign is excluded from its own training data.")

    results = []

    for campaign_id in available_ids:

        print(f"\n--- Evaluating {campaign_id} ---")

        result = evaluate_campaign(campaign_id)

        if result is not None:
            results.append(result)

    if not results:
        print("No campaigns could be evaluated.")
        return

    results_df = pd.DataFrame(results)

    display_columns = [
        "campaign_id",
        "posts_evaluated",
        "budget",
        "existing_cost",
        "candidate_cost",
        "incremental_payout",
        "existing_budget_used_pct",
        "candidate_budget_used_pct",
        "existing_top_milestone_reach_pct",
        "candidate_top_milestone_reach_pct",
        "top_milestone_reach_change_pp",
        "existing_views_per_1000",
        "candidate_views_per_1000",
        "reach_efficiency_change_pct",
        "candidate_within_budget",
    ]

    print("\n===== BACKTEST SUMMARY =====")

    print(
        results_df[display_columns].round(2).to_string(index=False)
    )

    print("\nCampaigns evaluated:", len(results_df))

    print(
        "Candidate ladders within budget:",
        int(results_df["candidate_within_budget"].sum()),
        "of",
        len(results_df),
    )


if __name__ == "__main__":
    main()

    
