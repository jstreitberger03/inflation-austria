"""Forecasting helpers for inflation rates."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .config import ReportConfig, ensure_config
from .constants import COUNTRY_NAMES


def _forecast_holt_winters(series: pd.Series, periods: int) -> tuple[np.ndarray, float]:
    """Forecast with damped Holt-Winters; returns forecast and residual std."""
    # Require at least two seasonal cycles to stabilize.
    if len(series) < 24:
        raise ValueError("Not enough data for Holt-Winters")

    model = ExponentialSmoothing(
        series,
        trend="add",
        damped_trend=True,
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )
    fitted = model.fit(optimized=True, use_brute=True)
    forecast = fitted.forecast(periods)
    resid_std = float(np.std(fitted.resid, ddof=1)) if hasattr(fitted, "resid") else float(np.std(series.diff().dropna(), ddof=1))
    return forecast, resid_std


def _forecast_linear_regression(series: pd.Series, periods: int) -> tuple[np.ndarray, float]:
    """Simple linear regression fallback forecast."""
    x = np.arange(len(series)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, series.values)

    future_x = np.arange(len(series), len(series) + periods).reshape(-1, 1)
    forecast = model.predict(future_x)

    resid_std = float(np.std(series.values - model.predict(x), ddof=1))
    return forecast, resid_std


def _prediction_interval(values: np.ndarray, resid_std: float, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    """Return lower/upper prediction bounds using a normal approximation."""
    delta = z * resid_std
    lower = values - delta
    upper = values + delta
    return lower, upper


def forecast_inflation(df: pd.DataFrame, config: ReportConfig | dict) -> pd.DataFrame:
    """
    Forecast inflation for each configured country using Holt-Winters with a linear fallback.

    Returns a tidy DataFrame with columns: date, geo, country, inflation_rate, lower_bound, upper_bound.
    """
    config = ensure_config(config)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["coicop"] == "CP00"]
    if df.empty:
        return pd.DataFrame(columns=["date", "geo", "country", "inflation_rate", "lower_bound", "upper_bound"])

    forecast_horizon = int(config.forecast_months)
    results: list[dict] = []

    for geo in df["geo"].unique():
        hist = df[df["geo"] == geo].sort_values("date")
        if hist.empty:
            continue

        series = hist.set_index("date")["inflation_rate"].asfreq("MS")
        # Drop leading NaNs that may arise from asfreq alignment
        series = series.dropna()
        if series.empty:
            continue

        try:
            forecast_values, resid_std = _forecast_holt_winters(series, forecast_horizon)
        except Exception:
            forecast_values, resid_std = _forecast_linear_regression(series, forecast_horizon)

        last_date: datetime = series.index.max().to_pydatetime()
        future_dates = [pd.Timestamp(last_date) + pd.DateOffset(months=i) for i in range(1, forecast_horizon + 1)]
        lower, upper = _prediction_interval(forecast_values, resid_std)

        for date, value, lo, hi in zip(future_dates, forecast_values, lower, upper, strict=True):
            results.append(
                {
                    "date": pd.to_datetime(date),
                    "geo": geo,
                    "country": COUNTRY_NAMES.get(geo, geo),
                    "inflation_rate": float(value),
                    "lower_bound": float(lo),
                    "upper_bound": float(hi),
                }
            )

    forecast_df = pd.DataFrame(results)
    if hasattr(config, "forecast_display_limit"):
        forecast_df = forecast_df[forecast_df["date"] <= pd.to_datetime(config.forecast_display_limit)]
    return forecast_df.sort_values("date")
