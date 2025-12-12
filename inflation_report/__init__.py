"""Inflation report package providing data, analysis, and configuration utilities."""

from .config import ReportConfig, load_config
from .data import fetch_interest_rates, fetch_inflation_data, process_inflation_data
from .analysis import compare_regions
from .constants import COUNTRY_NAMES

__all__ = [
    "ReportConfig",
    "load_config",
    "fetch_inflation_data",
    "process_inflation_data",
    "fetch_interest_rates",
    "compare_regions",
    "COUNTRY_NAMES",
]
