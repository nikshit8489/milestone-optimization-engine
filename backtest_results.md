# Backtesting Results

## Milestone Optimization Engine

**Document Type:** Performance Evaluation Report
---

## 1. Executive Summary

The backtesting process evaluates the proposed milestone payout optimization approach against existing payout structures across five campaigns.

The evaluation focuses on budget utilization, payout expenditure, milestone attainment, and historical views-per-payout efficiency.

The results demonstrate that the candidate payout structures remained within their respective campaign budgets, while reach and payout efficiency varied across campaigns.

## 2. Evaluation Methodology

The engine evaluates five campaigns (C001–C005) using their historical post-performance data.

The following metrics are compared:

* Existing and candidate payout expenditure.
* Campaign budget utilization.
* Incremental payout.
* Existing and candidate top milestone reach.
* Views generated per ₹1,000 payout.
* Change in reach efficiency.

The candidate payout structure is generated using the budget-constrained optimization approach, with a 95th-percentile simulated payout-cost constraint.

## 3. Backtesting Results

| Campaign | Existing Cost | Candidate Cost |    Budget | Reach Change (pp) |
| -------- | ------------: | -------------: | --------: | ----------------: |
| C001     |       ₹70,000 |      ₹1,16,250 | ₹2,00,000 |              0.00 |
| C002     |       ₹48,000 |      ₹1,16,000 | ₹2,00,000 |             +6.67 |
| C003     |       ₹18,000 |        ₹26,722 |   ₹75,000 |              0.00 |
| C004     |     ₹1,15,000 |      ₹1,20,000 | ₹2,00,000 |             -6.67 |
| C005     |       ₹57,000 |      ₹1,31,250 | ₹2,00,000 |             +6.67 |

All five candidate payout costs remained within their respective campaign budgets.

## 4. Payout Efficiency Analysis

| Campaign | Existing Views / ₹1,000 | Candidate Views / ₹1,000 | Efficiency Change |
| -------- | ----------------------: | -----------------------: | ----------------: |
| C001     |               17,617.67 |                10,608.49 |           -39.78% |
| C002     |               31,495.35 |                13,032.56 |           -58.62% |
| C003     |               64,514.28 |                43,456.96 |           -32.64% |
| C004     |               89,384.14 |                85,659.80 |            -4.17% |
| C005     |               57,609.05 |                25,018.79 |           -56.57% |

The efficiency metric represents historical views per ₹1,000 of payout expenditure.

## 5. Key Observations

1. **Budget Feasibility:** All five evaluated candidate payout structures remained within the available campaign budgets.

2. **Milestone Attainment:** C002 and C005 recorded a 6.67 percentage-point increase in top milestone reach.

3. **Stable Reach:** C001 and C003 showed no change in top milestone reach.

4. **Reach Variation:** C004 recorded a 6.67 percentage-point decrease in top milestone reach.

5. **Payout Efficiency:** Candidate structures showed lower historical views per ₹1,000 payout across all five evaluated campaigns.

These results highlight the tradeoff between increasing performance-based compensation and maintaining payout efficiency.

## 6. Limitations

* Evaluation is based on synthetic historical data.
* The same observed views are used to compare existing and candidate payout costs.
* Results do not establish causal improvements in creator performance.
* Sales, conversions, and revenue data are unavailable; therefore, actual business ROI cannot be calculated.
* The evaluation covers five campaigns rather than the complete dataset of 30 campaigns.

## 7. Conclusion

The backtesting results demonstrate that the Milestone Optimization Engine can generate candidate payout structures that satisfy campaign budget constraints under the evaluated scenarios.

The comparison also reveals variation in milestone attainment and historical payout efficiency, providing stakeholders with measurable information for payout planning.

Further validation using real campaign outcomes, conversion data, and a larger evaluation sample would be required before making production-level performance claims.
