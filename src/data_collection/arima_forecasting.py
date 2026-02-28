"""
ARIMA Skill Demand Forecasting
MSc Thesis: Job Market Skill Demand Forecasting
Author: Amil Thomas

Reads data/processed/skill_by_month.csv and applies ARIMA to forecast
skill demand for the next 2 months. Classifies skills as:
  - Emerging  : positive trend + forecast growth
  - Stable    : flat trend
  - Declining : negative trend + forecast decline

Output:
  data/processed/arima_forecasts.csv
  data/processed/skill_trends.csv
"""

import csv
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

INPUT_FILE      = "data/processed/skill_by_month.csv"
OUTPUT_FORECAST = "data/processed/arima_forecasts.csv"
OUTPUT_TRENDS   = "data/processed/skill_trends.csv"

os.makedirs("data/processed", exist_ok=True)

MIN_OBSERVATIONS = 3   # skip skills with fewer than this many non-zero months
FORECAST_STEPS   = 2   # forecast 2 months ahead


def load_data():
    rows = list(csv.DictReader(open(INPUT_FILE, encoding="utf-8")))
    months = [r["month"] for r in rows]
    skills = [k for k in rows[0].keys() if k != "month"]
    data = {skill: [int(r[skill]) for r in rows] for skill in skills}
    return months, skills, data


def is_stationary(series):
    try:
        result = adfuller(series, autolag="AIC")
        return result[1] < 0.05
    except Exception:
        return False


def fit_arima(series):
    """Try ARIMA with different orders, return best fit."""
    best_model = None
    best_aic   = float("inf")

    orders = [(1,0,0),(0,1,0),(1,1,0),(0,1,1),(1,1,1),(0,0,1),(2,0,0)]

    for order in orders:
        try:
            model = ARIMA(series, order=order)
            result = model.fit()
            if result.aic < best_aic:
                best_aic   = result.aic
                best_model = result
        except Exception:
            continue

    return best_model


def classify_trend(series, forecast_values):
    """Classify skill as Emerging, Stable, or Declining."""
    if len(series) < 2:
        return "Stable"

    # Linear trend slope
    x = np.arange(len(series))
    slope = np.polyfit(x, series, 1)[0]

    # Forecast direction
    last_actual  = series[-1]
    forecast_avg = np.mean(forecast_values) if forecast_values else last_actual
    forecast_change = forecast_avg - last_actual

    if slope > 0.5 or forecast_change > 0.5:
        return "Emerging"
    elif slope < -0.5 or forecast_change < -0.5:
        return "Declining"
    else:
        return "Stable"


def run():
    print("=" * 65)
    print("ARIMA SKILL DEMAND FORECASTING")
    print("=" * 65)

    # Check statsmodels is available
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError:
        print("\nERROR: statsmodels not installed.")
        print("Run: pip install statsmodels")
        return

    months, skills, data = load_data()
    print(f"Loaded {len(months)} months x {len(skills)} skills")
    print(f"Months: {months}")
    print(f"Forecasting {FORECAST_STEPS} months ahead\n")

    # Generate next month labels
    last_month = months[-1]
    year, month = int(last_month[:4]), int(last_month[5:7])
    forecast_months = []
    for _ in range(FORECAST_STEPS):
        month += 1
        if month > 12:
            month = 1
            year += 1
        forecast_months.append(f"{year}-{month:02d}")

    forecast_rows = []
    trend_rows    = []

    for skill in skills:
        series = data[skill]
        total  = sum(series)
        nonzero = sum(1 for v in series if v > 0)

        # Skip skills with too little data
        if nonzero < MIN_OBSERVATIONS or total < 5:
            continue

        series_arr = np.array(series, dtype=float)

        # Fit ARIMA
        model_result = fit_arima(series_arr)

        if model_result is None:
            forecast_values = [series[-1]] * FORECAST_STEPS
        else:
            try:
                forecast = model_result.forecast(steps=FORECAST_STEPS)
                forecast_values = [max(0, round(float(v), 1)) for v in forecast]
            except Exception:
                forecast_values = [series[-1]] * FORECAST_STEPS

        trend = classify_trend(series, forecast_values)

        # Growth rate (last month vs first month)
        first_nonzero = next((v for v in series if v > 0), 1)
        last_val      = series[-1]
        growth_rate   = round((last_val - first_nonzero) / max(first_nonzero, 1) * 100, 1)

        # Save forecast row
        row = {
            "skill":       skill,
            "trend":       trend,
            "total_count": total,
            "growth_rate": growth_rate,
        }
        for i, fm in enumerate(forecast_months):
            row[f"forecast_{fm}"] = forecast_values[i] if i < len(forecast_values) else 0

        # Add historical months
        for i, m in enumerate(months):
            row[m] = series[i]

        forecast_rows.append(row)

        trend_rows.append({
            "skill":       skill,
            "trend":       trend,
            "total_count": total,
            "growth_rate": growth_rate,
            "avg_monthly": round(total / len(months), 1),
        })

        print(f"  {skill:<30} {trend:<12} total={total:>4}  growth={growth_rate:>+6.1f}%  forecast={forecast_values}")

    # Sort by total count
    forecast_rows.sort(key=lambda x: x["total_count"], reverse=True)
    trend_rows.sort(key=lambda x: x["total_count"], reverse=True)

    # Save forecasts
    if forecast_rows:
        fieldnames = list(forecast_rows[0].keys())
        with open(OUTPUT_FORECAST, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(forecast_rows)

    # Save trends
    if trend_rows:
        with open(OUTPUT_TRENDS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["skill","trend","total_count","growth_rate","avg_monthly"])
            w.writeheader()
            w.writerows(trend_rows)

    # Summary
    from collections import Counter
    trend_counts = Counter(r["trend"] for r in trend_rows)

    print(f"\n{'=' * 65}")
    print(f"FORECASTING COMPLETE")
    print(f"{'=' * 65}")
    print(f"  Skills analysed : {len(trend_rows)}")
    print(f"  Emerging        : {trend_counts.get('Emerging', 0)}")
    print(f"  Stable          : {trend_counts.get('Stable', 0)}")
    print(f"  Declining       : {trend_counts.get('Declining', 0)}")
    print(f"\n  Output: {OUTPUT_FORECAST}")
    print(f"  Output: {OUTPUT_TRENDS}")

    print(f"\n{'EMERGING SKILLS':}")
    print(f"  {'Skill':<30} {'Total':>6}  {'Growth':>8}")
    print(f"  {'-'*48}")
    for r in [x for x in trend_rows if x['trend']=='Emerging']:
        print(f"  {r['skill']:<30} {r['total_count']:>6}  {r['growth_rate']:>+7.1f}%")

    print(f"\n{'DECLINING SKILLS':}")
    print(f"  {'Skill':<30} {'Total':>6}  {'Growth':>8}")
    print(f"  {'-'*48}")
    for r in [x for x in trend_rows if x['trend']=='Declining']:
        print(f"  {r['skill']:<30} {r['total_count']:>6}  {r['growth_rate']:>+7.1f}%")


if __name__ == "__main__":
    run()