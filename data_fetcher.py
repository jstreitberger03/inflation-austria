"""
Module for fetching inflation data from Eurostat.
"""
import pandas as pd
import eurostat


def fetch_inflation_data():
    """
    Fetch HICP (Harmonized Index of Consumer Prices) inflation data from Eurostat.
    
    Returns:
        pd.DataFrame: DataFrame containing inflation data for Austria and Euro zone
    """
    print("Fetching inflation data from Eurostat...")
    
    # Fetch HICP annual rate of change data
    # prc_hicp_aind: HICP - annual data (index and rate of change)
    # This dataset contains annual inflation rates
    try:
        df = eurostat.get_data_df('prc_hicp_aind')
        
        # Filter for annual rate of change (RCH_A_AVG)
        # and for Austria (AT) and Euro area (EA19)
        df_filtered = df[
            (df['unit'] == 'RCH_A_AVG') &  # Annual rate of change
            (df['coicop'].str.startswith('CP00')) &  # All-items HICP
            (df['geo'].isin(['AT', 'EA19']))  # Austria and Euro area
        ].copy()
        
        print(f"Fetched {len(df_filtered)} records")
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
    # Sample data based on approximate historical values
    years = [str(year) for year in range(2015, 2024)]
    
    data = {
        'geo': ['AT'] * len(years) + ['EA19'] * len(years),
        'year': years * 2,
        'value': [
            # Austria approximate values
            0.9, 1.0, 2.2, 2.1, 1.5, 1.4, 2.8, 8.6, 7.7,
            # Euro zone approximate values
            0.0, 0.2, 1.5, 1.8, 1.2, 0.3, 2.6, 8.4, 5.4
        ]
    }
    
    return pd.DataFrame(data)


def process_inflation_data(df):
    """
    Process and clean the inflation data for analysis.
    
    Args:
        df (pd.DataFrame): Raw inflation data
        
    Returns:
        pd.DataFrame: Processed inflation data with cleaned columns
    """
    # Get all year columns (they follow pattern like '2020', '2021', etc.)
    year_columns = [col for col in df.columns if col.isdigit()]
    
    if year_columns:
        # Reshape from wide to long format
        id_cols = [col for col in df.columns if not col.isdigit()]
        df_long = df.melt(
            id_vars=id_cols,
            value_vars=year_columns,
            var_name='year',
            value_name='inflation_rate'
        )
        
        # Clean data: remove missing values and convert to numeric
        df_long['inflation_rate'] = pd.to_numeric(df_long['inflation_rate'], errors='coerce')
        df_long = df_long.dropna(subset=['inflation_rate'])
        
        # Add readable country names
        df_long['country'] = df_long['geo'].map({
            'AT': 'Austria',
            'EA19': 'Euro zone'
        })
        
        return df_long[['year', 'geo', 'country', 'inflation_rate']].sort_values('year')
    else:
        # Data is already in the right format (sample data)
        df['country'] = df['geo'].map({
            'AT': 'Austria',
            'EA19': 'Euro zone'
        })
        df.rename(columns={'value': 'inflation_rate'}, inplace=True)
        return df[['year', 'geo', 'country', 'inflation_rate']].sort_values('year')
