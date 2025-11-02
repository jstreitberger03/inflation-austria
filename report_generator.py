"""
Module for generating text reports from inflation analysis.
"""
from datetime import datetime


def generate_text_report(df, stats, comparison, trends, output_dir='output'):
    """
    Generate a comprehensive text report of the inflation analysis.
    
    Args:
        df (pd.DataFrame): Processed inflation data
        stats (dict): Statistics dictionary
        comparison (pd.DataFrame): Month-by-month comparison
        trends (dict): Trends and extremes data
        output_dir (str): Directory to save the report
        
    Returns:
        str: Path to the saved report
    """
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("INFLATION REPORT: AUSTRIA VS EURO ZONE")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 80)
    
    # Get data range
    years = sorted(df['year'].unique())
    report_lines.append(f"Analysis Period: {years[0]} - {years[-1]}")
    report_lines.append("")
    
    # Latest inflation rates
    for country in stats.keys():
        latest_rate = stats[country]['latest']
        latest_date = stats[country]['latest_date']
        report_lines.append(f"{country} - Latest Inflation Rate ({latest_date:%B %Y}): {latest_rate:.2f}%")
    report_lines.append("")
    
    # Key Statistics
    report_lines.append("KEY STATISTICS")
    report_lines.append("-" * 80)
    
    for country in stats.keys():
        report_lines.append(f"\n{country}:")
        report_lines.append(f"  Average Inflation:    {stats[country]['mean']:.2f}%")
        report_lines.append(f"  Median Inflation:     {stats[country]['median']:.2f}%")
        report_lines.append(f"  Minimum Inflation:    {stats[country]['min']:.2f}%")
        report_lines.append(f"  Maximum Inflation:    {stats[country]['max']:.2f}%")
        report_lines.append(f"  Standard Deviation:   {stats[country]['std']:.2f}%")
    
    report_lines.append("")
    
    # Trends and Extremes
    report_lines.append("TRENDS AND EXTREMES")
    report_lines.append("-" * 80)
    
    for country in trends.keys():
        report_lines.append(f"\n{country}:")
    report_lines.append(f"  Highest Inflation: {trends[country]['highest_rate']:.2f}% in {trends[country]['highest_date']:%B %Y}")
    report_lines.append(f"  Lowest Inflation: {trends[country]['lowest_rate']:.2f}% in {trends[country]['lowest_date']:%B %Y}")
    
    report_lines.append("")
    
    # Year-by-Year Comparison
    report_lines.append("YEAR-BY-YEAR COMPARISON")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Year':<10} {'Österreich':<15} {'Deutschland':<15} {'Eurozone':<15} {'Difference':<15}")
    report_lines.append("-" * 80)
    
    for year in comparison.index:
        austria_val = comparison.loc[year, 'Österreich'] if 'Österreich' in comparison.columns else 0
        germany_val = comparison.loc[year, 'Deutschland'] if 'Deutschland' in comparison.columns else 0
        euro_val = comparison.loc[year, 'Eurozone'] if 'Eurozone' in comparison.columns else 0
        diff_val = comparison.loc[year, 'Difference (AT - EA)'] if 'Difference (AT - EA)' in comparison.columns else 0
        
        report_lines.append(
            f"{year:<10} {austria_val:>8.2f}%      {germany_val:>8.2f}%      "
            f"{euro_val:>8.2f}%      {diff_val:>8.2f}%"
        )
    
    report_lines.append("")
    
    # Analysis Summary
    report_lines.append("ANALYSIS SUMMARY")
    report_lines.append("-" * 80)
    
    if 'Difference (AT - EA)' in comparison.columns:
        avg_diff = comparison['Difference (AT - EA)'].mean()
        years_higher = comparison['Higher in Austria'].sum()
        total_years = len(comparison)
        
        report_lines.append(f"Average Difference: {avg_diff:.2f} percentage points")
        report_lines.append(f"Austria had higher inflation in {years_higher} out of {total_years} months.")
        report_lines.append(f"That's {(years_higher/total_years*100):.1f}% of the time")
        report_lines.append("")
        
        if avg_diff > 0:
            report_lines.append("On average, Austria experienced higher inflation than the Euro zone.")
        elif avg_diff < 0:
            report_lines.append("On average, Austria experienced lower inflation than the Euro zone.")
        else:
            report_lines.append("On average, Austria's inflation matched the Euro zone.")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    # Write to file
    import os
    output_path = os.path.join(output_dir, 'inflation_report.txt')
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Saved text report to {output_path}")
    return output_path


def print_summary(stats, trends):
    """
    Print a brief summary to console.
    
    Args:
        stats (dict): Statistics dictionary
        trends (dict): Trends data
    """
    print("\n" + "=" * 80)
    print("INFLATION ANALYSIS SUMMARY")
    print("=" * 80)
    
    for country in stats.keys():
        print(f"\n{country}:")
        print(f"  Latest: {stats[country]['latest']:.2f}% ({stats[country]['latest_date']:%B %Y})")
        print(f"  Average: {stats[country]['mean']:.2f}%")
        print(f"  Peak: {trends[country]['highest_rate']:.2f}% ({trends[country]['highest_date']:%B %Y})")
    
    print("\n" + "=" * 80)
