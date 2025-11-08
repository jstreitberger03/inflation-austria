"""
Module for analyzing inflation data and comparing Austria with Euro zone.
"""
import pandas as pd


def calculate_statistics(df, config):
    """
    Calculate statistical measures for inflation data.
    
    Args:
        df (pd.DataFrame): Processed inflation data
        
    Returns:
        dict: Dictionary containing statistics for each region
    """
    # Filter to 2020 onwards for statistics
    df_filtered = df[df['date'] >= config['analysis_start_date']].copy()
    
    stats = {}
    
    for geo in df_filtered['geo'].unique():
        region_data = df_filtered[df_filtered['geo'] == geo]
        country_name = region_data['country'].iloc[0]
        
        stats[country_name] = {
            'mean': region_data['inflation_rate'].mean(),
            'median': region_data['inflation_rate'].median(),
            'min': region_data['inflation_rate'].min(),
            'max': region_data['inflation_rate'].max(),
            'std': region_data['inflation_rate'].std(),
            'latest': region_data.sort_values('date', ascending=False)['inflation_rate'].iloc[0] if len(region_data) > 0 else None,
            'latest_date': region_data.sort_values('date', ascending=False)['date'].iloc[0] if len(region_data) > 0 else None
        }
    
    return stats


def compare_regions(df):
    """
    Compare inflation between Austria and Euro zone.
    
    Args:
        df (pd.DataFrame): Processed inflation data
        
    Returns:
        pd.DataFrame: Month-by-month comparison with differences
    """
    # Filter for overall inflation (CP00) to avoid duplicates before pivoting
    df_overall = df[df['coicop'] == 'CP00'].copy()
    
    # Pivot to have Austria and Euro zone as columns
    comparison = df_overall.pivot(index='date', columns='country', values='inflation_rate')
    
    if 'Österreich' in comparison.columns and 'Eurozone' in comparison.columns:
        comparison['Difference (AT - EA)'] = comparison['Österreich'] - comparison['Eurozone']
        comparison['Higher in Austria'] = comparison['Difference (AT - EA)'] > 0
    
    return comparison


def identify_trends(df):
    """
    Identify trends and periods of high/low inflation.
    
    Args:
        df (pd.DataFrame): Processed inflation data
        
    Returns:
        dict: Dictionary containing trend information
    """
    trends = {}
    
    for geo in df['geo'].unique():
        region_data = df[df['geo'] == geo].sort_values('date')
        country_name = region_data['country'].iloc[0]
        
        # Find dates with highest and lowest inflation
        max_idx = region_data['inflation_rate'].idxmax()
        min_idx = region_data['inflation_rate'].idxmin()
        
        max_date = region_data.loc[max_idx, 'date']
        max_rate = region_data.loc[max_idx, 'inflation_rate']
        
        min_date = region_data.loc[min_idx, 'date']
        min_rate = region_data.loc[min_idx, 'inflation_rate']
        
        trends[country_name] = {
            'highest_date': max_date,
            'highest_rate': max_rate,
            'lowest_date': min_date,
            'lowest_rate': min_rate
        }
    
    return trends
