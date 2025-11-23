"""Pipeline orchestration for generating inflation figures."""

from __future__ import annotations

from pathlib import Path

from .analysis import calculate_statistics, compare_regions, identify_trends
from .config import ReportConfig, load_config
from .data import fetch_ecb_interest_rates, fetch_inflation_data, process_inflation_data
from .forecasting import forecast_inflation
from .reporting.text import print_summary
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


def run_report(config_path: str | Path | None = None) -> int:
    """Run the full pipeline and return an exit code."""
    print("=" * 80)
    print("AUSTRIA INFLATION FIGURE GENERATOR")
    print("=" * 80)
    print()

    print("[1/8] Lade Konfiguration...")
    config = load_config(config_path)
    print()

    print("[2/8] Fetching inflation data...")
    raw_data = fetch_inflation_data(config)

    print("[3/8] Processing data...")
    df = process_inflation_data(raw_data, config)
    df = df.dropna(subset=["date"])
    print(f"      Processed {len(df)} monthly data points from {df['date'].min():%B %Y} to {df['date'].max():%B %Y}")
    print()

    print("[4/8] Fetching ECB interest rates...")
    interest_df = fetch_ecb_interest_rates()
    print(f"      Fetched {len(interest_df)} interest rate data points")
    print()

    print(f"[5/8] Generating {config.forecast_months}-month inflation forecast...")
    forecast_df = forecast_inflation(df, config)
    months_generated = len(forecast_df) // len(config.countries) if not forecast_df.empty else 0
    print(f"      Generated forecasts for {months_generated} months")
    print()

    print("[6/8] Analyzing data...")
    stats = calculate_statistics(df, config)
    comparison = compare_regions(df)
    trends = identify_trends(df)
    print("      Analysis complete")
    print()

    print("[7/8] Creating visualizations...")
    output_dir = create_output_directory()
    plot_inflation_comparison(df, config, forecast_df=forecast_df, output_dir=output_dir)
    plot_ecb_interest_rates(interest_df, output_dir=output_dir)
    plot_difference(comparison, config, output_dir=output_dir)
    plot_statistics_comparison(stats, config, output_dir=output_dir)
    plot_historical_comparison(config, output_dir=output_dir)
    plot_inflation_components(df, output_dir=output_dir)
    plot_eu_heatmap(output_dir=output_dir)
    print()

    print("[8/8] Summary:")
    print_summary(stats, trends)
    print()

    print("=" * 80)
    print("FIGURE GENERATION COMPLETE!")
    print(f"All figures saved to '{output_dir}/' directory")
    print("=" * 80)

    return 0
