
import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function money(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function percentage(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function App() {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedId, setSelectedId] = useState("C001");
  const [result, setResult] = useState(null);

  const [activePage, setActivePage] = useState("overview");

  const [backtest, setBacktest] = useState(null);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [backtestError, setBacktestError] = useState("");
  const [backtestStarted, setBacktestStarted] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/campaigns`)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load campaigns");
        return response.json();
      })
      .then((data) => {
        setCampaigns(data);
        if (data.length > 0) {
          setSelectedId(data[0].campaign_id);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  async function runOptimization() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API}/api/campaigns/${selectedId}/optimize`,
        { method: "POST" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Optimization failed");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadBacktest() {
    setBacktestStarted(true);
    setActivePage("backtest");
    setBacktestLoading(true);
    setBacktestError("");

    try {
      const response = await fetch(`${API}/api/backtest`);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not load backtesting results");
      }

      setBacktest(data);
    } catch (err) {
      setBacktestError(err.message);
    } finally {
      setBacktestLoading(false);
    }
  }

  const selectedCampaign = campaigns.find(
    (campaign) => campaign.campaign_id === selectedId
  );

  const totalPosts = backtest?.results?.reduce(
    (total, item) => total + item.posts_evaluated,
    0
  ) || 0;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">M</div>
          <div>
            <h2>
              Milestone<span>OS</span>
            </h2>
            <p>OPTIMIZATION ENGINE</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <button
          className={`nav-item ${activePage === "overview" ? "active" : ""}`}
          onClick={() => setActivePage("overview")}
          style={{
            width: "100%",
            textAlign: "left",
            border: "none",
            cursor: "pointer",
            font: "inherit",
          }}
        >
          ▦ &nbsp; Overview
        </button>

        <div className="nav-item">◈ &nbsp; Campaigns</div>
        <div className="nav-item">⌁ &nbsp; Optimization</div>

        <button
          className={`nav-item ${activePage === "backtest" ? "active" : ""}`}
          onClick={() => {
  setActivePage("backtest");
  setBacktestStarted(false);
  setBacktest(null);
  setBacktestError("");
}}
          style={{
            width: "100%",
            textAlign: "left",
            border: "none",
            cursor: "pointer",
            font: "inherit",
          }}
        >
          ▤ &nbsp; Backtesting
        </button>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          Python Engine Connected
          <p>Version 1.0.0</p>
        </div>
      </aside>

      <main className="main-content">

        {activePage === "overview" && (
          <>
            <header className="topbar">
              <div>
                <p className="eyebrow">ANALYTICS / OVERVIEW</p>
                <h1>Campaign Overview</h1>
                <p className="subtitle">
                  Optimize creator milestones with data-driven decisions.
                </p>
              </div>

              <div className="live-badge">
                <span /> ENGINE LIVE
              </div>
            </header>

            <section className="stats-grid">
              <div className="stat-card">
                <p>Total Campaigns</p>
                <h2>{campaigns.length || "—"}</h2>
                <span>Available in dataset</span>
              </div>

              <div className="stat-card">
                <p>Selected Campaign</p>
                <h2>{selectedId}</h2>
                <span>{selectedCampaign?.brand || "Loading..."}</span>
              </div>

              <div className="stat-card">
                <p>Campaign Budget</p>
                <h2>{money(selectedCampaign?.budget)}</h2>
                <span>Allocated budget</span>
              </div>

              <div className="stat-card">
                <p>Optimization Status</p>
                <h2 className="green-text">
                  {result ? "Complete" : "Ready"}
                </h2>
                <span>Python optimization engine</span>
              </div>
            </section>

            <section className="panel campaign-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">CONFIGURATION</p>
                  <h2>Optimize Campaign</h2>
                  <p className="subtitle">
                    Select a campaign and generate a candidate milestone ladder.
                  </p>
                </div>

                <span className="tag">LIVE DATA</span>
              </div>

              <div className="controls">
                <div className="select-wrap">
                  <label htmlFor="campaign">Select Campaign</label>

                  <select
                    id="campaign"
                    value={selectedId}
                    onChange={(e) => {
                      setSelectedId(e.target.value);
                      setResult(null);
                      setError("");
                    }}
                  >
                    {campaigns.map((campaign) => (
                      <option
                        key={campaign.campaign_id}
                        value={campaign.campaign_id}
                      >
                        {campaign.campaign_id} — {campaign.brand}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  className="optimize-button"
                  onClick={runOptimization}
                  disabled={loading || !selectedId}
                >
                  {loading ? "Optimizing..." : "✦ Run Optimization"}
                </button>
              </div>

              {error && <div className="error-box">{error}</div>}
            </section>

            {result && (
              <>
                <section className="stats-grid result-stats">
                  <div className="stat-card">
                    <p>Existing Payout Cost</p>
                    <h2>{money(result.existing_cost)}</h2>
                  </div>

                  <div className="stat-card">
                    <p>Optimized Payout Cost</p>
                    <h2 className="green-text">
                      {money(result.candidate_cost)}
                    </h2>
                  </div>

                  <div className="stat-card">
                    <p>Budget Remaining</p>
                    <h2>{money(result.budget_remaining)}</h2>
                  </div>

                  <div className="stat-card">
                    <p>Budget Feasibility</p>
                    <h2 className="green-text">
                      {result.candidate_within_budget
                        ? "Within Budget"
                        : "Over Budget"}
                    </h2>
                  </div>
                </section>

                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">STRUCTURE COMPARISON</p>
                      <h2>Milestone Ladder</h2>
                    </div>

                    <span className="tag success-tag">OPTIMIZED</span>
                  </div>

                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Milestone</th>
                          <th>Existing Views</th>
                          <th>Existing Payout</th>
                          <th>Candidate Views</th>
                          <th>Candidate Payout</th>
                        </tr>
                      </thead>

                      <tbody>
                        {result.candidate_ladder.map((item, index) => (
                          <tr key={index}>
                            <td>
                              <span className="milestone-number">
                                {index + 1}
                              </span>
                            </td>

                            <td>
                              {Number(
                                result.existing_ladder[index]?.view_threshold || 0
                              ).toLocaleString("en-IN")}
                            </td>

                            <td>
                              {money(
                                result.existing_ladder[index]?.payout_amount
                              )}
                            </td>

                            <td className="green-text">
                              {Number(item.view_threshold).toLocaleString("en-IN")}
                            </td>

                            <td className="green-text">
                              {money(item.payout_amount)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="budget-section">
                    <div className="budget-heading">
                      <span>Candidate Budget Utilization</span>
                      <strong>
                        {(
                          (result.candidate_cost / result.budget) * 100
                        ).toFixed(2)}%
                      </strong>
                    </div>

                    <div className="progress-track">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${Math.min(
                            100,
                            (result.candidate_cost / result.budget) * 100
                          )}%`,
                        }}
                      />
                    </div>

                    <p>
                      {money(result.candidate_cost)} spent out of{" "}
                      {money(result.budget)}
                    </p>
                  </div>
                </section>
              </>
            )}
          </>
        )}

        {activePage === "backtest" && (
          <>
            <header className="topbar">
              <div>
                <p className="eyebrow">MODEL VALIDATION / BACKTESTING</p>
                <h1>Backtesting Results</h1>
                <p className="subtitle">
                  Compare existing and candidate milestone structures across campaigns.
                </p>
              </div>

              <button
                className="optimize-button"
                onClick={loadBacktest}
                disabled={backtestLoading}
              >
                {backtestLoading ? "Running..." : "↻ Refresh Results"}
              </button>
            </header>

            {backtestLoading && (
              <section className="panel">
                <p>Running backtest across campaigns...</p>
              </section>
            )}

            {backtestError && (
              <section className="panel">
                <div className="error-box">{backtestError}</div>
              </section>
            )}

            {backtest && !backtestLoading && (
              <>
                <section className="stats-grid">
                  <div className="stat-card">
                    <p>Campaigns Evaluated</p>
                    <h2>{backtest.campaigns_evaluated}</h2>
                    <span>Historical campaigns</span>
                  </div>

                  <div className="stat-card">
                    <p>Within Budget</p>
                    <h2 className="green-text">
                      {backtest.within_budget_count} / {backtest.campaigns_evaluated}
                    </h2>
                    <span>Candidate budget feasibility</span>
                  </div>

                  <div className="stat-card">
                    <p>Total Posts Evaluated</p>
                    <h2>{totalPosts}</h2>
                    <span>Across evaluated campaigns</span>
                  </div>

                  <div className="stat-card">
                    <p>Evaluation Status</p>
                    <h2 className="green-text">Complete</h2>
                    <span>Backtest response received</span>
                  </div>
                </section>

                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">HISTORICAL VALIDATION</p>
                      <h2>Campaign Comparison</h2>
                      <p className="subtitle">
                        Existing vs candidate payout and milestone reach.
                      </p>
                    </div>

                    <span className="tag success-tag">BACKTEST COMPLETE</span>
                  </div>

                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Campaign</th>
                          <th>Posts</th>
                          <th>Budget</th>
                          <th>Existing Cost</th>
                          <th>Candidate Cost</th>
                          <th>Existing Budget Used</th>
                          <th>Candidate Budget Used</th>
                          <th>Existing Top Reach</th>
<th>Candidate Top Reach</th>
<th>Reach Change (pp)</th>
<th>Existing Views / ₹1000</th>
<th>Candidate Views / ₹1000</th>
<th>Efficiency Change</th>
<th>Budget Status</th>
                        </tr>
                      </thead>

                      <tbody>
                        {backtest.results.map((item) => (
                          <tr key={item.campaign_id}>
                            <td>{item.campaign_id}</td>
                            <td>{item.posts_evaluated}</td>
                            <td>{money(item.budget)}</td>
                            <td>{money(item.existing_cost)}</td>
                            <td className="green-text">
                              {money(item.candidate_cost)}
                            </td>
                            <td>{percentage(item.existing_budget_used_pct)}</td>
                            <td>{percentage(item.candidate_budget_used_pct)}</td>
                            <td>{percentage(item.existing_top_milestone_reach_pct)}</td>
                            <td className="green-text">
                              {percentage(item.candidate_top_milestone_reach_pct)}
                            </td>
                            <td>
  {item.top_milestone_reach_change_pp === null ||
  item.top_milestone_reach_change_pp === undefined
    ? "N/A"
    : `${item.top_milestone_reach_change_pp > 0 ? "+" : ""}${Number(item.top_milestone_reach_change_pp).toFixed(2)} pp`}
</td>

<td>
  {item.existing_views_per_1000 == null
    ? "N/A"
    : Number(item.existing_views_per_1000).toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}
</td>

<td>
  {item.candidate_views_per_1000 == null
    ? "N/A"
    : Number(item.candidate_views_per_1000).toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}
</td>

<td>
  {item.reach_efficiency_change_pct == null
    ? "N/A"
    : percentage(item.reach_efficiency_change_pct)}
</td>
                            <td>
                              <span
                                className={`tag ${
                                  item.candidate_within_budget
                                    ? "success-tag"
                                    : ""
                                }`}
                              >
                                {item.candidate_within_budget
                                  ? "Within Budget"
                                  : "Over Budget"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                 <div className="budget-section">
  <p className="subtitle">
    Each campaign is evaluated against its historical posts.
    The candidate ladder is generated using training data that
    excludes that target campaign.
  </p>

  <p className="subtitle">
    Views per ₹1,000 measures historical view efficiency relative
    to payout cost. Reach change is measured in percentage points.
    These are historical comparisons, not proof of causal
    performance improvement or actual sales ROI.
  </p>
</div>
                </section>

                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">CREATOR EQUITY / FAIRNESS</p>
                      <h2>Creator Tier Fairness</h2>
                      <p className="subtitle">
                        Compare average payouts and top-milestone reach by creator tier.
                        Small tier samples should be interpreted cautiously.
                      </p>
                    </div>
                    <span className="tag success-tag">FAIRNESS ANALYSIS</span>
                  </div>

                  {backtest.results.some(
                    (item) => Array.isArray(item.creator_fairness) && item.creator_fairness.length > 0
                  ) ? (
                    backtest.results.map((item) => (
                      <div className="budget-section" key={`${item.campaign_id}-fairness`}>
                        <div className="panel-heading">
                          <div>
                            <p className="eyebrow">CAMPAIGN {item.campaign_id}</p>
                            <h2>{item.campaign_id} — Tier Comparison</h2>
                          </div>
                          <span className="tag">{item.creator_fairness?.length || 0} tiers</span>
                        </div>

                        {Array.isArray(item.creator_fairness) && item.creator_fairness.length > 0 ? (
                          <div className="table-scroll">
                            <table>
                              <thead>
                                <tr>
                                  <th>Creator Tier</th>
                                  <th>Posts</th>
                                  <th>Existing Avg. Payout</th>
                                  <th>Candidate Avg. Payout</th>
                                  <th>Payout Change</th>
                                  <th>Existing Top Reach</th>
                                  <th>Candidate Top Reach</th>
                                </tr>
                              </thead>
                              <tbody>
                                {item.creator_fairness.map((tier, index) => (
                                  <tr key={`${item.campaign_id}-${tier.creator_tier || index}`}>
                                    <td>{tier.creator_tier || "Unknown"}</td>
                                    <td>{tier.posts_evaluated ?? "—"}</td>
                                    <td>{money(tier.existing_avg_payout)}</td>
                                    <td className="green-text">{money(tier.candidate_avg_payout)}</td>
                                    <td>
                                      {tier.payout_change_pct === null ||
                                      tier.payout_change_pct === undefined
                                        ? "N/A"
                                        : percentage(tier.payout_change_pct)}
                                    </td>
                                    <td>{percentage(tier.existing_top_milestone_reach_pct)}</td>
                                    <td className="green-text">
                                      {percentage(tier.candidate_top_milestone_reach_pct)}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <p className="subtitle">No creator-tier fairness data returned for this campaign.</p>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="subtitle">
                      The API response does not contain creator_fairness data yet.
                      Confirm the backend response at /api/backtest.
                    </p>
                  )}

                  <p className="subtitle">
                    Fairness metrics are calculated from the evaluated historical posts.
                    A tier with very few posts may not represent typical creator outcomes.
                  </p>
                </section>
              </>
            )}
          </>
        )}

        <footer>
          MilestoneOS · Powered by Python, FastAPI & React
        </footer>
      </main>
    </div>
  );
}

export default App;