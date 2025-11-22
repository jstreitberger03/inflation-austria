"""Forecasting utilities for inflation data."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .config import ReportConfig, ensure_config
from .constants import COUNTRY_NAMES


def forecast_inflation(
    df: pd.DataFrame,
    config: ReportConfig | dict,
    method: Literal["holt_winters", "linear"] = "holt_winters",
) -> pd.DataFrame:
    """
    Forecast inflation using time series models with confidence intervals.

    Primary method: Holt-Winters Exponential Smoothing (trend, damped).
    Fallback: Linear regression on the most recent 12 months.
    """
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    config = ensure_config(config)
    forecasts: list[dict[str, object]] = []
    months_ahead = config.forecast_months

    for geo in df["geo"].unique():
        region_data = df[(df["geo"] == geo) & (df["coicop"] == "CP00")].sort_values("date").copy()
        if region_data.empty:
            continue

        country_name = region_data["country"].iloc[0] or COUNTRY_NAMES.get(geo, geo)
        training_window = min(config.forecast_training_window, len(region_data))
        training_data = region_data.tail(training_window).copy()

        try:
            if method == "holt_winters" and training_window >= 12:
                model = ExponentialSmoothing(
                    training_data["inflation_rate"].values,
                    trend="add",
                    seasonal=None,
                    damped_trend=True,
                )
                fitted_model = model.fit(optimized=True, use_brute=False)
                forecast_values = fitted_model.forecast(steps=months_ahead)
                fitted_values = fitted_model.fittedvalues
                residuals = training_data["inflation_rate"].values - fitted_values
                std_error = np.std(residuals)
                method_used = "Holt-Winters (Exponential Smoothing mit Trend)"
            else:
                raise ValueError("Using linear regression fallback")
        except Exception:
            recent_data = region_data.tail(12).copy()
            min_date = recent_data["date"].min()
            recent_data["months"] = (
                (recent_data["date"].dt.year - min_date.year) * 12
                + (recent_data["date"].dt.month - min_date.month)
            )

            model = LinearRegression()
            model.fit(recent_data["months"].values.reshape(-1, 1), recent_data["inflation_rate"].values)
            forecast_values = model.predict(np.arange(12, 12 + months_ahead).reshape(-1, 1))
            predictions = model.predict(recent_data["months"].values.reshape(-1, 1))
            residuals = recent_data["inflation_rate"].values - predictions
            std_error = np.std(residuals)
            method_used = "Lineare Regression (12-Monats-Trend)"

        last_date = region_data["date"].max()
        next_month = (
            pd.Timestamp(year=last_date.year + 1, month=1, day=1)
            if last_date.month == 12
            else pd.Timestamp(year=last_date.year, month=last_date.month + 1, day=1)
        )
        future_dates = pd.date_range(start=next_month, periods=months_ahead, freq="MS").tolist()

        for idx, (date, value) in enumerate(zip(future_dates, forecast_values)):
            horizon_factor = np.sqrt(1 + idx / 6)
            uncertainty = std_error * 1.96 * horizon_factor
            forecasts.append(
                {
                    "date": date,
                    "geo": geo,
                    "country": country_name,
                    "inflation_rate": float(value),
                    "lower_bound": max(0, float(value - uncertainty)),
                    "upper_bound": float(value + uncertainty),
                    "is_forecast": True,
                    "method": method_used,
                    "std_error": float(std_error),
                    "training_months": training_window,
                }
            )

    return pd.DataFrame(forecasts)
