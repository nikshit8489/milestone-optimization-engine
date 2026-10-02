# Synthetic Data Generation & Assumptions

## Milestone Optimization Engine

### 1. Overview

The Milestone Optimization Engine uses synthetic data to simulate a creator marketing ecosystem involving campaigns, creators, content performance, and milestone-based payouts.

Since real marketplace data was unavailable, datasets were generated using Python, Pandas, and NumPy. The data provides a reproducible environment for evaluating budget feasibility, payout efficiency, and creator fairness.

### 2. Dataset Summary

| Dataset                      | Records |
| ---------------------------- | ------: |
| Campaigns                    |      30 |
| Creators                     |     300 |
| Posts                        |     450 |
| Historical Milestone Records |     120 |

Each campaign contains 15 posts and four historical milestone records.

### 3. Data Generation Methodology

**Reproducibility:** NumPy random seed 42 is used to ensure repeatable data generation.

**Creator Distribution:**

| Tier  | Creators | Follower Range |
| ----- | -------: | -------------- |
| Nano  |      120 | 1K–9,999       |
| Micro |      105 | 10K–99,999     |
| Mid   |       60 | 100K–999,999   |
| Macro |       15 | 1M–3M          |

Historical average views are generated as 5%–80% of follower count. Account age ranges from 6–119 months, while completion rates range from 10%–90%.

Creators are randomly assigned to Instagram or YouTube.

### 4. Campaign Assumptions

The generator supports five categories: Gaming, FMCG, Finance, D2C, and Entertainment.

Campaign budgets are selected from ₹50,000, ₹75,000, ₹1,00,000, ₹1,50,000, and ₹2,00,000.

Campaign start dates begin on 1 January 2026, advancing by seven days per campaign. Each campaign has a seven-day duration.

A target creator tier is stored as campaign metadata. However, the current generator selects eligible creators based on platform rather than enforcing the target tier.

### 5. Performance and Payout Modeling

Final views are generated using a lognormal distribution with sigma = 0.8 and predefined category multipliers.

| Category      | Multiplier |
| ------------- | ---------: |
| Gaming        |        1.2 |
| FMCG          |        1.0 |
| Finance       |        0.7 |
| D2C           |        0.9 |
| Entertainment |        1.3 |

The historical payout ladder uses four thresholds:

| Views   |         Payout |
| ------- | -------------: |
| 10,000  | 0.5% of budget |
| 50,000  |   2% of budget |
| 100,000 |   5% of budget |
| 500,000 |  15% of budget |

Payout is determined by the highest milestone achieved, rather than the cumulative sum of lower milestone rewards.

### 6. Time-Based Performance

The dataset records views at three observation points:

* **24 hours:** 15%–35% of final views.
* **7 days:** 55%–80% of final views.
* **30 days:** Equal to final views.

The fractions are independently generated. The uploaded dataset was validated to satisfy the expected chronological view ordering.

### 7. Suspicious Engagement Simulation

A 5% probability is used to introduce suspicious activity. Flagged posts receive an artificial final-view multiplier between 3 and 7.

The uploaded dataset contains 20 flagged posts out of 450, representing approximately 4.44%.

This mechanism is intended to test the optimizer's handling of abnormal engagement and is not a production fraud-detection model.

### 8. Data Quality Validation

The validation process checks:

* Missing values and duplicate records.
* Negative final view counts.
* Suspicious post counts.
* Missing and invalid creator tier values.
* Creator tier distribution.

The uploaded CSV datasets contain no missing values or duplicate rows, and all observed final view counts are non-negative.

### 9. Assumptions and Limitations

The synthetic data is based on predefined distributions rather than calibrated real-world marketplace observations.

Key limitations include:

* Follower count is an approximate indicator of potential reach.
* Category multipliers are assumed rather than empirically learned.
* Suspicious engagement is randomly simulated.
* Completion rates are generated independently of actual posting histories.
* Target creator tier does not restrict creator selection in the current generator.
* Sales, conversions, revenue, and brand-lift data are not included.

Consequently, the results demonstrate system behavior under controlled assumptions and should not be interpreted as guaranteed real-world campaign outcomes.

### 10. Conclusion

The synthetic dataset provides a reproducible foundation for evaluating milestone payout optimization, budget constraints, and creator-tier fairness.

Its controlled variation in creator profiles, campaign categories, content performance, and suspicious engagement enables systematic testing while clearly separating simulated outcomes from real marketplace performance.
