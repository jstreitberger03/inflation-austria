"""Analysis routines for inflation data."""

from __future__ import annotations

import pandas as pd

from .config import ensure_config


def calculate_statistics(df: pd.DataFrame, config) -> dict:
    """Calculate statistical measures for inflation data."""
    config = ensure_config(config)
    df_filtered = df[df["date"] >= config.analysis_start_date].copy()
    stats: dict[str, dict[str, float]] = {}

    for geo in df_filtered["geo"].unique():
        region_data = df_filtered[df_filtered["geo"] == geo]
        if region_data.empty:
            continue
        country_name = region_data["country"].iloc[0]

        stats[country_name] = {
            "mean": region_data["inflation_rate"].mean(),
            "median": region_data["inflation_rate"].median(),
            "min": region_data["inflation_rate"].min(),
            "max": region_data["inflation_rate"].max(),
            "std": region_data["inflation_rate"].std(),
            "latest": region_data.sort_values("date", ascending=False)["inflation_rate"].iloc[0],
            "latest_date": region_data.sort_values("date", ascending=False)["date"].iloc[0],
        }

    return stats


def compare_regions(df: pd.DataFrame) -> pd.DataFrame:
    """Compare inflation between Austria and Euro zone."""
    df_overall = df[df["coicop"] == "CP00"].copy()
    comparison = df_overall.pivot(index="date", columns="country", values="inflation_rate")

    if "Österreich" in comparison.columns and "Eurozone" in comparison.columns:
        comparison["Difference (AT - EA)"] = comparison["Österreich"] - comparison["Eurozone"]
        comparison["Higher in Austria"] = comparison["Difference (AT - EA)"] > 0

    return comparison


def identify_trends(df: pd.DataFrame) -> dict:
    """Identify trends and periods of high/low inflation."""
    trends: dict[str, dict] = {}

    for geo in df["geo"].unique():
        region_data = df[df["geo"] == geo].sort_values("date")
        if region_data.empty:
            continue

        country_name = region_data["country"].iloc[0]
        max_idx = region_data["inflation_rate"].idxmax()
        min_idx = region_data["inflation_rate"].idxmin()

        trends[country_name] = {
            "highest_date": region_data.loc[max_idx, "date"],
            "highest_rate": region_data.loc[max_idx, "inflation_rate"],
            "lowest_date": region_data.loc[min_idx, "date"],
            "lowest_rate": region_data.loc[min_idx, "inflation_rate"],
        }

    return trends
