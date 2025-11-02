#!/usr/bin/env python3
"""
Main script for generating the Austria Inflation Report.

This script fetches inflation data from Eurostat, analyzes it,
and generates comprehensive reports comparing Austria with the Euro zone.
"""
import sys
from data_fetcher import fetch_inflation_data, process_inflation_data
from analysis import (
    calculate_statistics, 
    compare_regions, 
    identify_trends
)
from visualization import (
    create_output_directory,
    plot_inflation_comparison,
    plot_difference,
    plot_statistics_comparison
)
from report_generator import generate_text_report, print_summary


def main():
    """Main function to run the inflation report generation."""
    print("=" * 80)
    print("AUSTRIA INFLATION REPORT GENERATOR")
    print("=" * 80)
    print()
    
    # Step 1: Fetch data
    print("[1/6] Fetching inflation data...")
    raw_data = fetch_inflation_data()
    
    # Step 2: Process data
    print("[2/6] Processing data...")
    df = process_inflation_data(raw_data)
    
    # Filter out any rows with missing dates
    df = df.dropna(subset=['date'])
    
    print(f"      Processed {len(df)} monthly data points from {df['date'].min():%B %Y} to {df['date'].max():%B %Y}")
    print()
    
    # Step 3: Analyze data
    print("[3/6] Analyzing data...")
    stats = calculate_statistics(df)
    comparison = compare_regions(df)
    trends = identify_trends(df)
    print("      Analysis complete")
    print()
    
    # Step 4: Create visualizations
    print("[4/6] Creating visualizations...")
    output_dir = create_output_directory()
    
    plot_inflation_comparison(df, output_dir)
    plot_difference(comparison, output_dir)
    plot_statistics_comparison(stats, output_dir)
    print()
    
    # Step 5: Generate text report
    print("[5/6] Generating text report...")
    generate_text_report(df, stats, comparison, trends, output_dir)
    print()
    
    # Step 6: Print summary
    print("[6/6] Summary:")
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
