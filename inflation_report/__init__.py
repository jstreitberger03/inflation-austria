"""Inflation report package providing data, analysis, visualization, and summary utilities."""

from .config import ReportConfig, load_config
from .data import fetch_ecb_interest_rates, fetch_inflation_data, process_inflation_data
from .forecasting import forecast_inflation
from .analysis import calculate_statistics, compare_regions, identify_trends
from .visualization import (
    create_output_directory,
    plot_difference,
    plot_ecb_interest_rates,
    plot_eu_heatmap,
    plot_historical_comparison,
    plot_inflation_comparison,
    plot_inflation_components,
    plot_statistics_comparison,
)
from .reporting.text import generate_text_report, print_summary

__all__ = [
    "ReportConfig",
    "load_config",
    "fetch_inflation_data",
    "process_inflation_data",
    "fetch_ecb_interest_rates",
    "forecast_inflation",
    "calculate_statistics",
    "compare_regions",
    "identify_trends",
    "create_output_directory",
    "plot_difference",
    "plot_ecb_interest_rates",
    "plot_eu_heatmap",
    "plot_historical_comparison",
    "plot_inflation_comparison",
    "plot_inflation_components",
    "plot_statistics_comparison",
    "generate_text_report",
    "print_summary",
]
