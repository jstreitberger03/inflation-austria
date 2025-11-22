"""Compatibility wrappers for the refactored visualization module."""

from inflation_report.visualization import (
    create_output_directory,
    plot_difference,
    plot_ecb_interest_rates,
    plot_eu_heatmap,
    plot_historical_comparison,
    plot_inflation_comparison,
    plot_inflation_components,
    plot_statistics_comparison,
)

__all__ = [
    "create_output_directory",
    "plot_inflation_comparison",
    "plot_difference",
    "plot_statistics_comparison",
    "plot_historical_comparison",
    "plot_inflation_components",
    "plot_eu_heatmap",
    "plot_ecb_interest_rates",
]
