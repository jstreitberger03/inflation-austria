#!/usr/bin/env python3
"""
Main script for generating the Austria Inflation Report.

This script fetches inflation data from Eurostat, analyzes it,
and generates comprehensive reports comparing Austria with the Euro zone.
"""
import yaml
import sys
from data_fetcher import (
    fetch_inflation_data, 
    process_inflation_data,
    fetch_ecb_interest_rates,
    forecast_inflation
)
from analysis import (
    calculate_statistics, 
    compare_regions, 
    identify_trends
)
from visualization import (
    create_output_directory,
    plot_inflation_comparison,
    plot_difference,
    plot_statistics_comparison,
    plot_historical_comparison,
    plot_eu_heatmap,
    plot_inflation_components,
    plot_ecb_interest_rates
)
from report_generator import generate_text_report, print_summary
from html_report_generator import generate_html_report


def load_config(path='config.yaml'):
    """Lädt die Konfigurationsdatei."""
    print(f"      Lade Konfiguration von '{path}'...")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """Main function to run the inflation report generation."""
    print("=" * 80)
    print("AUSTRIA INFLATION REPORT GENERATOR")
    print("=" * 80)
    print()

    # Step 1: Konfiguration laden
    print("[1/9] Lade Konfiguration...")
    config = load_config()
    print()

    # Step 2: Fetch data
    print("[2/9] Fetching inflation data...")
    raw_data = fetch_inflation_data(config)

    # Step 3: Process data
    print("[3/9] Processing data...")
    df = process_inflation_data(raw_data, config)
    
    # Filter out any rows with missing dates
    df = df.dropna(subset=['date'])
    
    print(f"      Processed {len(df)} monthly data points from {df['date'].min():%B %Y} to {df['date'].max():%B %Y}")
    print()

    # Step 4: Fetch ECB interest rates
    print("[4/9] Fetching ECB interest rates...")
    interest_df = fetch_ecb_interest_rates()
    print(f"      Fetched {len(interest_df)} interest rate data points")
    print()

    # Step 5: Generate forecast
    print(f"[5/9] Generating {config['forecast_months']}-month inflation forecast...")
    forecast_df = forecast_inflation(df, config)
    print(f"      Generated forecasts for {len(forecast_df) // len(config['countries'])} months")
    print()

    # Step 6: Analyze data
    print("[6/9] Analyzing data...")
    stats = calculate_statistics(df, config)
    comparison = compare_regions(df)
    trends = identify_trends(df)
    print("      Analysis complete")
    print()

    # Step 7: Create visualizations
    print("[7/9] Creating visualizations...")
    output_dir = create_output_directory()
    
    plot_inflation_comparison(df, config, output_dir)
    plot_ecb_interest_rates(interest_df, output_dir)
    plot_difference(comparison, config, output_dir)
    plot_statistics_comparison(stats, config, output_dir)
    plot_historical_comparison(config, output_dir)  # Historical plot since Euro introduction
    plot_inflation_components(df, output_dir)  # Inflation components for Austria
    plot_eu_heatmap(output_dir)  # EU-wide heatmap
    print()
    
    # Step 8: Generate reports
    print("[8/9] Generating reports...")
    generate_text_report(df, stats, comparison, trends, output_dir)
    generate_html_report(df, stats, comparison, trends, forecast_df, output_dir)
    print()
    
    # Step 9: Print summary
    print("[9/9] Summary:")
    print_summary(stats, trends)
    print()
    
    print("=" * 80)
    print(f"REPORT GENERATION COMPLETE!")
    print(f"All outputs saved to '{output_dir}/' directory")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
