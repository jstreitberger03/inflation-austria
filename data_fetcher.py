"""
Module for fetching inflation data from Eurostat.
"""
import pandas as pd
import numpy as np
import eurostat


def fetch_inflation_data():
    """
    Fetch HICP (Harmonized Index of Consumer Prices) inflation data from Eurostat.
    
    Returns:
        pd.DataFrame: DataFrame containing inflation data for Austria and Euro zone
    """
    print("Fetching inflation data from Eurostat...")
    
    # Fetch HICP monthly rate of change data
    # prc_hicp_manr: HICP - monthly data (annual rate of change)
    # This dataset contains monthly inflation rates compared to same month of previous year
    try:
        # Get the data from Eurostat
        df = eurostat.get_data_df('prc_hicp_manr', flags=False)
        
        print(f"Data shape: {df.shape}")
        
        # The geo column is named 'geo\\TIME_PERIOD' in the Eurostat data
        # Rename it to just 'geo' for easier handling
        if 'geo\\TIME_PERIOD' in df.columns:
            df = df.rename(columns={'geo\\TIME_PERIOD': 'geo'})
        
        # Filter for Austria (AT), Germany (DE) and Euro area (EA20 or EA19)
        # Also filter for all-items HICP (CP00)
        # Prefer EA20 over EA19 if both exist
        df_filtered = df[
            (df['coicop'].str.startswith('CP00')) &  # All-items HICP
            (df['geo'].isin(['AT', 'DE', 'EA20', 'EA19']))  # Austria, Germany and Euro area
        ].copy()
        
        # If we have both EA19 and EA20, keep only EA20
        if 'EA20' in df_filtered['geo'].values and 'EA19' in df_filtered['geo'].values:
            df_filtered = df_filtered[df_filtered['geo'] != 'EA19']
        
        print(f"Fetched {len(df_filtered)} records for Austria, Germany and Euro zone")
        print(f"Date range: {[col for col in df_filtered.columns if '-' in str(col)][:3]} to {[col for col in df_filtered.columns if '-' in str(col)][-3:]}")
        return df_filtered
        
    except Exception as e:
        print(f"Error fetching data from Eurostat: {e}")
        print("Returning sample data for demonstration purposes...")
        return _get_sample_data()


def _get_sample_data():
    """
    Provide sample inflation data for demonstration if API fetch fails.
    
    Returns:
        pd.DataFrame: Sample inflation data
    """
    # Sample monthly data for recent years
    dates = pd.date_range('2023-01-01', '2025-10-31', freq='ME')
    periods = [f"{d.year}-{d.month:02d}" for d in dates]
    
    # Create sample data with monthly values
    data = pd.DataFrame()
    data['geo'] = ['AT', 'DE', 'EA20']  # Austria, Germany, Euro zone
    
    # Generate some realistic-looking monthly inflation rates
    for period in periods:
        if period.startswith('2023'):
            data[period] = [6.8 + np.random.normal(0, 0.5), 6.1 + np.random.normal(0, 0.5), 6.1 + np.random.normal(0, 0.5)]
        elif period.startswith('2024'):
            data[period] = [4.2 + np.random.normal(0, 0.5), 3.8 + np.random.normal(0, 0.5), 3.8 + np.random.normal(0, 0.5)]
        else:  # 2025
            data[period] = [2.8 + np.random.normal(0, 0.5), 2.3 + np.random.normal(0, 0.5), 2.5 + np.random.normal(0, 0.5)]
    
    return data


def process_inflation_data(df):
    """
    Process and clean the inflation data for analysis.
    
    Args:
        df (pd.DataFrame): Raw inflation data
        
    Returns:
        pd.DataFrame: Processed inflation data with cleaned columns
    """
    # The data has timestamps as column names
    # Get all timestamp columns (they follow pattern like '1997-01', '2023-05', etc.)
    time_columns = [col for col in df.columns if isinstance(col, str) and '-' in str(col)]
    
    # Reshape from wide to long format
    df_long = df.melt(
        id_vars=['geo'],
        value_vars=time_columns,
        var_name='period',
        value_name='inflation_rate'
    )
    
    # Convert period strings to datetime
    # Periods are in format 'YYYY-MM'
    df_long['date'] = pd.to_datetime(df_long['period'], format='%Y-%m', errors='coerce')
    
    # Clean data: convert to numeric and remove missing values
    df_long['inflation_rate'] = pd.to_numeric(df_long['inflation_rate'], errors='coerce')
    df_long = df_long.dropna(subset=['inflation_rate', 'date'])
    
    # Filter data from 2020 onwards
    df_long = df_long[df_long['date'] >= '2020-01-01']
    
    # Add readable country names
    df_long['country'] = df_long['geo'].map({
        'AT': 'Österreich',
        'DE': 'Deutschland',
        'EA20': 'Eurozone',
        'EA19': 'Eurozone'  # Support both EA19 and EA20
    })
    
    # Add year column for compatibility
    df_long['year'] = df_long['date'].dt.year
    
    # Sort by date
    df_long = df_long.sort_values('date')
    
    return df_long[['date', 'year', 'geo', 'country', 'inflation_rate']]