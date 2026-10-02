# Milestone Optimization Engine

A data-driven creator payout optimization system that recommends milestone-based reward structures using historical performance data, simulations, and campaign budget constraints.

## Features

* Synthetic campaign and creator data generation
* Performance-based milestone payout optimization
* 1,000 payout simulations
* 95th-percentile budget feasibility analysis
* Campaign backtesting and payout efficiency comparison
* Creator tier fairness analysis
* FastAPI backend and React dashboard

## Tech Stack

**Backend:** Python, FastAPI, Pandas, NumPy
**Frontend:** React, Vite
**API Documentation:** Swagger UI

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nikshit8489/milestone-optimization-engine.git
cd milestone-optimization-engine
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Synthetic Data

```bash
python src/generate_data.py
```

### 4. Validate Dataset

```bash
python src/check_data.py
```

### 5. Run Backtesting

From the project root directory, execute:

```powershell
$env:PYTHONPATH="src"
python -m backtest
```

This evaluates existing and optimized payout structures and reports:

* Payout expenditure
* Budget utilization
* Milestone reach
* Incremental payout
* Views per ₹1,000 payout
* Reach efficiency change

### 6. Start the Backend

```bash
python -m uvicorn src.api:app --reload
```

Backend: http://127.0.0.1:8000

API Documentation: http://127.0.0.1:8000/docs

### 7. Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Documentation

* `methodology.md` — Optimization methodology and approach.
* `synthetic_data_generation.md` — Dataset generation assumptions and limitations.

