from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .optimizer import (
    posts,
    campaigns,
    ladders,
    creators,
    calculate_payout,
    generate_candidate_ladder,
    optimize_payouts,
)

app = FastAPI(
    title="Milestone Optimization Engine",
    description="API for campaign milestone optimization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Milestone Optimization Engine API is running",
        "status": "success"
    }


@app.get("/api/campaigns")
def get_campaigns():
    result = []

    for _, campaign in campaigns.iterrows():
        result.append({
            "campaign_id": str(campaign["campaign_id"]),
            "brand": str(campaign["brand"]),
            "platform": str(campaign["platform"]),
            "category": str(campaign["category"]),
            "budget": float(campaign["total_budget"]),
            "target_creator_tier": str(
                campaign["target_creator_tier"]
            )
        })

    return result


@app.post("/api/campaigns/{campaign_id}/optimize")
def optimize_campaign(campaign_id: str):

    campaign = campaigns[
        campaigns["campaign_id"] == campaign_id
    ]

    if campaign.empty:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    campaign_posts = posts[
        posts["campaign_id"] == campaign_id
    ].copy()

    existing_ladder = ladders[
        ladders["campaign_id"] == campaign_id
    ].copy()

    if campaign_posts.empty or existing_ladder.empty:
        raise HTTPException(
            status_code=400,
            detail="Campaign data or milestone ladder unavailable"
        )

    budget = float(campaign.iloc[0]["total_budget"])

    candidate_ladder = generate_candidate_ladder(campaign_id)

    if candidate_ladder.empty:
        raise HTTPException(
            status_code=400,
            detail="Could not generate candidate ladder"
        )

    candidate_ladder = optimize_payouts(
        campaign_id,
        candidate_ladder
    )

    existing_ladder = existing_ladder.sort_values("view_threshold")
    candidate_ladder = candidate_ladder.sort_values("view_threshold")

    campaign_posts["existing_payout"] = campaign_posts[
        "views_final"
    ].apply(
        lambda views: calculate_payout(views, existing_ladder)
    )

    campaign_posts["candidate_payout"] = campaign_posts[
        "views_final"
    ].apply(
        lambda views: calculate_payout(views, candidate_ladder)
    )

    existing_cost = float(campaign_posts["existing_payout"].sum())
    candidate_cost = float(campaign_posts["candidate_payout"].sum())

    return {
        "campaign_id": campaign_id,
        "budget": budget,
        "existing_cost": existing_cost,
        "candidate_cost": candidate_cost,
        "budget_remaining": budget - candidate_cost,
        "candidate_within_budget": candidate_cost <= budget,
        "existing_ladder": existing_ladder[
            ["view_threshold", "payout_amount"]
        ].to_dict(orient="records"),
        "candidate_ladder": candidate_ladder[
            ["view_threshold", "payout_amount"]
        ].to_dict(orient="records")
    }


@app.get("/api/backtest")
def get_backtest():

    results = []
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

    for campaign_id in available_ids:

        campaign_row = campaigns[
            campaigns["campaign_id"] == campaign_id
        ]

        campaign_posts = posts[
            posts["campaign_id"] == campaign_id
        ].copy()

        existing_ladder = ladders[
            ladders["campaign_id"] == campaign_id
        ].copy()

        budget = float(campaign_row.iloc[0]["total_budget"])

        candidate_ladder = generate_candidate_ladder(campaign_id)

        if candidate_ladder is None or candidate_ladder.empty:
            continue

        candidate_ladder = optimize_payouts(
            campaign_id,
            candidate_ladder
        )

        existing_ladder = existing_ladder.sort_values("view_threshold")
        candidate_ladder = candidate_ladder.sort_values("view_threshold")

        campaign_posts["existing_payout"] = campaign_posts[
            "views_final"
        ].apply(
            lambda views: calculate_payout(views, existing_ladder)
        )

        campaign_posts["candidate_payout"] = campaign_posts[
            "views_final"
        ].apply(
            lambda views: calculate_payout(views, candidate_ladder)
        )

        existing_cost = float(campaign_posts["existing_payout"].sum())
        candidate_cost = float(campaign_posts["candidate_payout"].sum())

        existing_top_threshold = existing_ladder["view_threshold"].max()
        candidate_top_threshold = candidate_ladder["view_threshold"].max()

        existing_top_reach = (
            campaign_posts["views_final"] >= existing_top_threshold
        ).mean() * 100

        candidate_top_reach = (
            campaign_posts["views_final"] >= candidate_top_threshold
        ).mean() * 100
                # Marginal Brand ROI metrics
        total_observed_views = float(
            campaign_posts["views_final"].fillna(0).sum()
        )

        incremental_payout = candidate_cost - existing_cost

        existing_views_per_1000 = (
            total_observed_views / existing_cost * 1000
            if existing_cost > 0
            else None
        )

        candidate_views_per_1000 = (
            total_observed_views / candidate_cost * 1000
            if candidate_cost > 0
            else None
        )

        reach_efficiency_change_pct = (
            (
                candidate_views_per_1000
                - existing_views_per_1000
            ) / existing_views_per_1000 * 100
            if existing_views_per_1000 is not None
            and candidate_views_per_1000 is not None
            and existing_views_per_1000 > 0
            else None
        )

        top_milestone_reach_change_pp = (
            candidate_top_reach - existing_top_reach
        )

        # Creator fairness calculation

        fairness_results = []

        creator_id_col = (
            "creator_id"
            if "creator_id" in campaign_posts.columns
            else None
        )

        creators_id_col = (
            "creator_id"
            if "creator_id" in creators.columns
            else None
        )

        tier_col = next(
            (
                col for col in ["creator_tier", "tier"]
                if col in creators.columns
            ),
            None
        )

        if creator_id_col and creators_id_col and tier_col:

            creator_tiers = creators[
                [creators_id_col, tier_col]
            ].drop_duplicates()

            fairness_posts = campaign_posts.merge(
                creator_tiers,
                left_on=creator_id_col,
                right_on=creators_id_col,
                how="left"
            )

            fairness_posts = fairness_posts.dropna(
                subset=[tier_col]
            )

            for tier, group in fairness_posts.groupby(tier_col):

                post_count = len(group)

                existing_avg = float(
                    group["existing_payout"].mean()
                )

                candidate_avg = float(
                    group["candidate_payout"].mean()
                )

                payout_change_pct = (
                    (candidate_avg - existing_avg)
                    / existing_avg * 100
                    if existing_avg != 0
                    else None 
                )

                existing_reach = (
                    group["views_final"] >= existing_top_threshold
                ).mean() * 100

                candidate_reach = (
                    group["views_final"] >= candidate_top_threshold
                ).mean() * 100

                fairness_results.append({
                    "creator_tier": str(tier),
                    "posts_evaluated": int(post_count),
                    "existing_avg_payout": existing_avg,
                    "candidate_avg_payout": candidate_avg,
                    "payout_change_pct": payout_change_pct,
                    "existing_top_milestone_reach_pct": existing_reach,
                    "candidate_top_milestone_reach_pct": candidate_reach
                })

        results.append({
            "campaign_id": campaign_id,
            "posts_evaluated": len(campaign_posts),
            "budget": budget,
            "existing_cost": existing_cost,
            "candidate_cost": candidate_cost,
                        # Marginal Brand ROI metrics
            "total_observed_views": total_observed_views,
            "incremental_payout": incremental_payout,
            "existing_views_per_1000": existing_views_per_1000,
            "candidate_views_per_1000": candidate_views_per_1000,
            "reach_efficiency_change_pct": reach_efficiency_change_pct,
            "top_milestone_reach_change_pp": top_milestone_reach_change_pp,
            "existing_budget_used_pct": (
                existing_cost / budget * 100 if budget else 0
            ),
            "candidate_budget_used_pct": (
                candidate_cost / budget * 100 if budget else 0
            ),
            "existing_top_milestone_reach_pct": existing_top_reach,
            "candidate_top_milestone_reach_pct": candidate_top_reach,
            "candidate_within_budget": candidate_cost <= budget,
            "creator_fairness": fairness_results
        })

    return {
        "campaigns_evaluated": len(results),
        "within_budget_count": sum(
            item["candidate_within_budget"] for item in results
        ),
        "results": results
    }