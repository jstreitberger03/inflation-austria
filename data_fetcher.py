"""Compatibility wrappers for the refactored package modules."""

from inflation_report.data import (
    fetch_ecb_interest_rates,
    fetch_inflation_data,
    process_inflation_data,
)
from inflation_report.forecasting import forecast_inflation

__all__ = [
    "fetch_inflation_data",
    "process_inflation_data",
    "fetch_ecb_interest_rates",
    "forecast_inflation",
]
