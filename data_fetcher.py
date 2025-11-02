"""
Module for fetching inflation data from Eurostat.
"""
import pandas as pd
import numpy as np
import eurostat
from sklearn.linear_model import LinearRegression
from datetime import timedelta


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
    
    # Filter data from 2002 onwards (Euro introduction transition period)
    df_long = df_long[df_long['date'] >= '2002-01-01']
    
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


def fetch_ecb_interest_rates():
    """
    Fetch ECB main refinancing rate and deposit facility rate from Eurostat.
    
    Returns:
        pd.DataFrame: DataFrame with both ECB interest rates since 2000
    """
    print("Fetching ECB interest rates from Eurostat...")
    
    try:
        # irt_st_m - Short-term interest rates
        df = eurostat.get_data_df('irt_st_m', flags=False)
        
        # Filter for ECB rates: MRR_RT (Main Refinancing) and DFR (Deposit Facility)
        df = df[
            ((df['int_rt'] == 'MRR_RT') | (df['int_rt'] == 'DFR')) & 
            (df['geo'] == 'EA')
        ]
        
        # Get time columns
        time_columns = [col for col in df.columns if isinstance(col, str) and '-' in str(col)]
        
        # Reshape to long format
        df_long = df.melt(
            id_vars=['geo', 'int_rt'],
            value_vars=time_columns,
            var_name='period',
            value_name='interest_rate'
        )
        
        # Convert to datetime and numeric
        df_long['date'] = pd.to_datetime(df_long['period'], format='%Y-%m', errors='coerce')
        df_long['interest_rate'] = pd.to_numeric(df_long['interest_rate'], errors='coerce')
        df_long = df_long.dropna(subset=['interest_rate', 'date'])
        
        # Filter from 2000 onwards
        df_long = df_long[df_long['date'] >= '2000-01-01']
        df_long = df_long.sort_values('date')
        
        # Map rate type to readable names
        df_long['rate_type'] = df_long['int_rt'].map({
            'MRR_RT': 'main_refinancing',
            'DFR': 'deposit_facility'
        })
        
        return df_long[['date', 'rate_type', 'interest_rate']]
        
    except Exception as e:
        print(f"Error fetching ECB interest rates: {e}")
        print("Creating synthetic interest rate data based on known ECB policy...")
        
        # Fallback: Create synthetic data based on known ECB rates since 2000
        dates = pd.date_range('2000-01', '2025-10', freq='MS')
        main_rates = []
        deposit_rates = []
        
        for date in dates:
            # Main Refinancing Rate (simplified historical values)
            if date < pd.Timestamp('2003-06-01'):
                main_rate = 4.5
            elif date < pd.Timestamp('2008-10-01'):
                main_rate = 2.0
            elif date < pd.Timestamp('2009-05-01'):
                main_rate = 1.25
            elif date < pd.Timestamp('2011-04-01'):
                main_rate = 1.0
            elif date < pd.Timestamp('2011-11-01'):
                main_rate = 1.5
            elif date < pd.Timestamp('2013-05-01'):
                main_rate = 1.0
            elif date < pd.Timestamp('2013-11-01'):
                main_rate = 0.5
            elif date < pd.Timestamp('2014-09-01'):
                main_rate = 0.25
            elif date < pd.Timestamp('2016-03-01'):
                main_rate = 0.05
            elif date < pd.Timestamp('2022-07-01'):
                main_rate = 0.0
            elif date < pd.Timestamp('2022-09-01'):
                main_rate = 0.5
            elif date < pd.Timestamp('2022-11-01'):
                main_rate = 1.25
            elif date < pd.Timestamp('2023-02-01'):
                main_rate = 2.0
            elif date < pd.Timestamp('2023-03-01'):
                main_rate = 2.5
            elif date < pd.Timestamp('2023-05-01'):
                main_rate = 3.0
            elif date < pd.Timestamp('2023-06-01'):
                main_rate = 3.5
            elif date < pd.Timestamp('2023-09-01'):
                main_rate = 4.0
            elif date < pd.Timestamp('2024-06-01'):
                main_rate = 4.5
            elif date < pd.Timestamp('2024-09-01'):
                main_rate = 4.25
            elif date < pd.Timestamp('2024-10-01'):
                main_rate = 3.65
            elif date < pd.Timestamp('2024-12-01'):
                main_rate = 3.40
            else:
                main_rate = 3.15
            
            # Deposit Facility Rate (typically 0.75-1% below main rate, negative from 2014-2022)
            if date < pd.Timestamp('2008-10-01'):
                deposit_rate = main_rate - 1.0
            elif date < pd.Timestamp('2009-05-01'):
                deposit_rate = main_rate - 0.75
            elif date < pd.Timestamp('2012-07-01'):
                deposit_rate = main_rate - 0.75
            elif date < pd.Timestamp('2014-06-01'):
                deposit_rate = 0.0
            elif date < pd.Timestamp('2014-09-01'):
                deposit_rate = -0.1
            elif date < pd.Timestamp('2015-12-01'):
                deposit_rate = -0.2
            elif date < pd.Timestamp('2016-03-01'):
                deposit_rate = -0.3
            elif date < pd.Timestamp('2019-09-01'):
                deposit_rate = -0.4
            elif date < pd.Timestamp('2022-07-01'):
                deposit_rate = -0.5
            elif date < pd.Timestamp('2022-09-01'):
                deposit_rate = 0.0
            elif date < pd.Timestamp('2022-11-01'):
                deposit_rate = 0.75
            elif date < pd.Timestamp('2023-02-01'):
                deposit_rate = 1.5
            elif date < pd.Timestamp('2023-03-01'):
                deposit_rate = 2.0
            elif date < pd.Timestamp('2023-05-01'):
                deposit_rate = 2.5
            elif date < pd.Timestamp('2023-06-01'):
                deposit_rate = 3.0
            elif date < pd.Timestamp('2023-09-01'):
                deposit_rate = 3.5
            elif date < pd.Timestamp('2024-06-01'):
                deposit_rate = 4.0
            elif date < pd.Timestamp('2024-09-01'):
                deposit_rate = 3.75
            elif date < pd.Timestamp('2024-10-01'):
                deposit_rate = 3.25
            elif date < pd.Timestamp('2024-12-01'):
                deposit_rate = 3.0
            else:
                deposit_rate = 2.75
            
            main_rates.append(main_rate)
            deposit_rates.append(deposit_rate)
        
        # Create combined dataframe
        df_main = pd.DataFrame({
            'date': dates, 
            'rate_type': 'main_refinancing',
            'interest_rate': main_rates
        })
        df_deposit = pd.DataFrame({
            'date': dates,
            'rate_type': 'deposit_facility', 
            'interest_rate': deposit_rates
        })
        
        return pd.concat([df_main, df_deposit], ignore_index=True)


def forecast_inflation(df, months_ahead=12):
    """
    Forecast inflation using recent trend with confidence intervals.
    
    Args:
        df (pd.DataFrame): Historical inflation data
        months_ahead (int): Number of months to forecast
        
    Returns:
        pd.DataFrame: Forecast data with confidence bands
    """
    forecasts = []
    
    for geo in df['geo'].unique():
        region_data = df[df['geo'] == geo].sort_values('date').copy()
        country_name = region_data['country'].iloc[0]
        
        # Use last 12 months for trend
        recent_data = region_data.tail(12).copy()
        
        # Convert dates to numeric (months since first date)
        min_date = recent_data['date'].min()
        recent_data['months'] = (recent_data['date'] - min_date).dt.days / 30.44
        
        # Simple linear regression on recent trend
        X = recent_data['months'].values.reshape(-1, 1)
        y = recent_data['inflation_rate'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate residual standard deviation for confidence bands
        predictions = model.predict(X)
        residuals = y - predictions
        std_error = np.std(residuals)
        
        # Generate future dates
        last_date = region_data['date'].max()
        future_dates = [last_date + timedelta(days=30.44 * i) for i in range(1, months_ahead + 1)]
        
        # Predict future values
        future_months = np.array([(date - min_date).days / 30.44 for date in future_dates]).reshape(-1, 1)
        future_values = model.predict(future_months)
        
        # Add confidence bands (95% confidence = ~1.96 * std_error)
        # Increase uncertainty over time
        for i, (date, value) in enumerate(zip(future_dates, future_values)):
            uncertainty = std_error * 1.96 * (1 + i / months_ahead)  # Growing uncertainty
            forecasts.append({
                'date': date,
                'geo': geo,
                'country': country_name,
                'inflation_rate': value,
                'lower_bound': max(0, value - uncertainty),  # Can't be negative
                'upper_bound': value + uncertainty,
                'is_forecast': True
            })
    
    return pd.DataFrame(forecasts)