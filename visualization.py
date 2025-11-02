"""
Module for generating visualizations of inflation data.
"""
from plotnine import *
import pandas as pd
import os


def create_output_directory():
    """Create output directory for reports if it doesn't exist."""
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def plot_inflation_comparison(df, output_dir='output'):
    """
    Create a line plot comparing inflation rates with forecast.
    
    Args:
        df (pd.DataFrame): Processed inflation data
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    import pandas as pd
    import locale
    import numpy as np
    from data_fetcher import forecast_inflation
    
    # Set German locale for month names
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'German_Germany.1252')
        except:
            pass
    
    # Filter to 2020 onwards for this plot
    df = df[df['date'] >= '2020-01-01'].copy()
    
    # Generate 6-month forecast
    forecast_df = forecast_inflation(df, months_ahead=6)
    
    # Combine historical and forecast
    df_hist = df.copy()
    df_hist['type'] = 'Historisch'
    df_hist['lower_bound'] = df_hist['inflation_rate']
    df_hist['upper_bound'] = df_hist['inflation_rate']
    
    forecast_df['type'] = 'Prognose'
    
    df_combined = pd.concat([df_hist, forecast_df], ignore_index=True)
    
    # Calculate y-axis limits with 1.0 increments
    y_min = np.floor(df_combined['lower_bound'].min())
    y_max = np.ceil(df_combined['upper_bound'].max())
    y_breaks = np.arange(y_min, y_max + 1, 1.0)
    
    plot = (ggplot(df_combined, aes(x='date', y='inflation_rate', color='country', group='country'))
            + geom_line(aes(linetype='type'), size=1.3, alpha=0.9)
            + geom_point(size=1.8, alpha=0.6, data=df_combined[df_combined['type'] == 'Historisch'])
            + geom_ribbon(aes(ymin='lower_bound', ymax='upper_bound', fill='country'),
                         data=df_combined[df_combined['type'] == 'Prognose'], 
                         alpha=0.12, show_legend=False)
            + scale_color_manual(values=['#2E86AB', '#A23B72', '#F18F01'], 
                                labels=['Österreich', 'Deutschland', 'Eurozone'])
            + scale_fill_manual(values=['#2E86AB', '#A23B72', '#F18F01'])
            + scale_linetype_manual(values=['solid', 'dashed'],
                                   labels=['Historisch', 'Prognose'])
            + scale_x_datetime(date_labels='%b %Y', date_breaks='3 months')
            + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
            + theme_minimal()
            + labs(title='Inflationsrate im Vergleich (mit 6-Monats-Prognose)',
                  x='',
                  y='Inflationsrate (%)',
                  color='Region',
                  linetype='',
                  caption='Quelle: Eurostat (2025). HICP - monatliche Änderungsrate zum Vorjahresmonat. Schattierter Bereich: 95%-Konfidenzintervall.')
            + theme(
                plot_title=element_text(size=14, face="bold", margin={'b': 15}),
                plot_caption=element_text(size=9, hjust=0, margin={'t': 12}, color='#666666'),
                axis_title=element_text(size=12),
                axis_title_x=element_blank(),
                axis_text=element_text(size=10),
                axis_text_x=element_text(angle=45, hjust=1),
                legend_position='top',
                legend_title=element_blank(),
                legend_text=element_text(size=11),
                legend_box_margin=5,
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.25, linetype='dotted', size=0.5, color='#CCCCCC'),
                panel_grid_major_y=element_line(alpha=0.5, linetype='dotted', size=0.8, color='#999999'),
                figure_size=(15, 7),
                panel_background=element_rect(fill='white'),
                plot_background=element_rect(fill='#FAFAFA')
            ))
    
    output_path = os.path.join(output_dir, 'inflation_comparison.png')
    plot.save(output_path, dpi=300)
    
    print(f"Saved plot to {output_path}")
    return output_path


def plot_difference(comparison_df, output_dir='output'):
    """
    Create a bar plot showing the difference in inflation rates.
    
    Args:
        comparison_df (pd.DataFrame): Comparison DataFrame from analysis
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    if 'Difference (AT - EA)' not in comparison_df.columns:
        print("No difference column found in comparison data")
        return None
    
    # Reset index to make date a column for plotnine
    plot_df = comparison_df.reset_index()
    
    # Create color column
    plot_df['color'] = ['#2ecc71' if x < 0 else '#e74c3c' for x in plot_df['Difference (AT - EA)']]
    
    plot = (ggplot(plot_df, aes(x='date', y='Difference (AT - EA)'))
            + geom_col(aes(fill='color'), show_legend=False)
            + geom_hline(yintercept=0, color='black', size=0.5)
            + scale_fill_identity()
            + scale_x_datetime(date_labels='%B %Y', date_breaks='6 months')
            + theme_minimal()
            + labs(title='Inflationsdifferenz: Österreich zur Eurozone',
                  subtitle='Positive Werte = Höhere Inflation in Österreich',
                  x='',
                  y='Differenz (Prozentpunkte)',
                  caption='Quelle: Eurostat (2025). Eigene Berechnung.')
            + theme(
                plot_title=element_text(size=13, face="bold", margin={'b': 5}),
                plot_subtitle=element_text(size=10, margin={'b': 10}),
                plot_caption=element_text(size=8, hjust=0, margin={'t': 10}),
                axis_title=element_text(size=11),
                axis_title_x=element_blank(),
                axis_text=element_text(size=9),
                axis_text_x=element_text(angle=45, hjust=1),
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.15, linetype='dotted', size=0.3),
                panel_grid_major_y=element_line(alpha=0.3, linetype='dotted', size=0.5),
                figure_size=(12, 6),
                panel_background=element_rect(fill='white'),
                plot_background=element_rect(fill='white')
            ))
    
    output_path = os.path.join(output_dir, 'inflation_difference.png')
    plot.save(output_path, dpi=300)
    
    print(f"Saved plot to {output_path}")
    return output_path


def plot_statistics_comparison(stats, output_dir='output'):
    """
    Create a bar plot comparing key statistics between regions.
    
    Args:
        stats (dict): Statistics dictionary from analysis
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    # Convert stats dictionary to DataFrame for plotting
    metrics = ['mean', 'median', 'min', 'max']
    metric_names = {
        'mean': 'Durchschnittliche Inflationsrate (%)',
        'median': 'Median Inflationsrate (%)',
        'min': 'Minimale Inflationsrate (%)',
        'max': 'Maximale Inflationsrate (%)'
    }
    
    plot_data = []
    for country in stats:
        for metric in metrics:
            plot_data.append({
                'country': country,
                'metric': metric_names[metric],
                'value': stats[country][metric]
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Add formatted labels to the DataFrame
    plot_df['label'] = plot_df['value'].apply(lambda x: f'{x:.1f}%')
    
    plot = (ggplot(plot_df, aes(x='country', y='value', fill='country'))
            + geom_col(alpha=0.7, show_legend=False)
            + scale_fill_manual(values=['#1f77b4', '#2ca02c', '#ff7f0e'])
            + geom_text(aes(label='label'), 
                       va='bottom',
                       position=position_dodge(width=0.9), size=8)
            + facet_wrap('~metric', ncol=2, scales='free_y')
            + theme_minimal()
            + labs(title='Deskriptive Statistik der Inflationsraten (seit 2020)',
                  x='',
                  y='Rate (%)',
                  caption='Quelle: Eurostat (2025). Eigene Berechnung.')
            + theme(
                plot_title=element_text(size=13, face="bold", margin={'b': 10}),
                plot_caption=element_text(size=8, hjust=0, margin={'t': 10}),
                strip_text=element_text(size=11, face="bold"),
                axis_title=element_text(size=11),
                axis_text=element_text(size=9),
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.15, linetype='dotted', size=0.3),
                panel_grid_major_y=element_line(alpha=0.3, linetype='dotted', size=0.5),
                figure_size=(12, 9),
                panel_background=element_rect(fill='white'),
                plot_background=element_rect(fill='white')
            ))
    
    output_path = os.path.join(output_dir, 'statistics_comparison.png')
    plot.save(output_path, dpi=300)
    
    print(f"Saved plot to {output_path}")
    return output_path


def plot_inflation_with_forecast(df, forecast_df, output_dir='output'):
    """
    Separate detailed forecast plot (now integrated into main comparison).
    This function kept for backward compatibility.
    """
    # This is now integrated into plot_inflation_comparison
    return plot_inflation_comparison(df, output_dir)


def plot_ecb_interest_rates(interest_df, output_dir='output'):
    """
    Create a plot showing ECB interest rates over time.
    
    Args:
        interest_df (pd.DataFrame): ECB interest rate data
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    import locale
    import numpy as np
    
    # Set German locale
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'German_Germany.1252')
        except:
            pass
    
    # If interest_df has multiple rate types
    if 'rate_type' in interest_df.columns:
        y_min = np.floor(interest_df['interest_rate'].min())
        y_max = np.ceil(interest_df['interest_rate'].max())
        y_breaks = np.arange(y_min, y_max + 1, 1.0)
        
        plot = (ggplot(interest_df, aes(x='date', y='interest_rate', color='rate_type'))
                + geom_line(size=1.4, alpha=0.9)
                + scale_color_manual(values=['#2C3E50', '#E74C3C'],
                                    labels=['Hauptrefinanzierungssatz', 'Einlagenfazilität'])
                + scale_x_datetime(date_labels='%Y', date_breaks='3 years')
                + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
                + theme_minimal()
                + labs(title='EZB-Leitzinsen seit 2000',
                      x='',
                      y='Zinssatz (%)',
                      color='Zinstyp',
                      caption='Quelle: EZB (2025). Hauptrefinanzierungssatz und Einlagenfazilität der Europäischen Zentralbank.')
                + theme(
                    plot_title=element_text(size=14, face="bold", margin={'b': 15}),
                    plot_caption=element_text(size=9, hjust=0, margin={'t': 12}, color='#666666'),
                    axis_title=element_text(size=12),
                    axis_title_x=element_blank(),
                    axis_text=element_text(size=10),
                    axis_text_x=element_text(angle=0, hjust=0.5),
                    legend_position='top',
                    legend_title=element_blank(),
                    legend_text=element_text(size=11),
                    legend_box_margin=5,
                    panel_grid_minor_x=element_blank(),
                    panel_grid_major_x=element_blank(),
                    panel_grid_minor_y=element_line(alpha=0.25, linetype='dotted', size=0.5, color='#CCCCCC'),
                    panel_grid_major_y=element_line(alpha=0.5, linetype='dotted', size=0.8, color='#999999'),
                    figure_size=(15, 7),
                    panel_background=element_rect(fill='white'),
                    plot_background=element_rect(fill='#FAFAFA')
                ))
    else:
        y_breaks = np.arange(0, 6, 1.0)
        
        plot = (ggplot(interest_df, aes(x='date', y='interest_rate'))
                + geom_line(color='#2C3E50', size=1.5, alpha=0.9)
                + geom_area(fill='#34495E', alpha=0.15)
                + scale_x_datetime(date_labels='%Y', date_breaks='3 years')
                + scale_y_continuous(breaks=y_breaks)
                + theme_minimal()
                + labs(title='EZB-Hauptrefinanzierungssatz seit 2000',
                      x='',
                      y='Leitzins (%)',
                      caption='Quelle: EZB (2025). Hauptrefinanzierungssatz der Europäischen Zentralbank.')
                + theme(
                    plot_title=element_text(size=14, face="bold", margin={'b': 15}),
                    plot_caption=element_text(size=9, hjust=0, margin={'t': 12}, color='#666666'),
                    axis_title=element_text(size=12),
                    axis_title_x=element_blank(),
                    axis_text=element_text(size=10),
                    axis_text_x=element_text(angle=0, hjust=0.5),
                    legend_position='none',
                    panel_grid_minor_x=element_blank(),
                    panel_grid_major_x=element_blank(),
                    panel_grid_minor_y=element_line(alpha=0.25, linetype='dotted', size=0.5, color='#CCCCCC'),
                    panel_grid_major_y=element_line(alpha=0.5, linetype='dotted', size=0.8, color='#999999'),
                    figure_size=(15, 7),
                    panel_background=element_rect(fill='white'),
                    plot_background=element_rect(fill='#FAFAFA')
                ))
    
    output_path = os.path.join(output_dir, 'ecb_interest_rates.png')
    plot.save(output_path, dpi=300)
    
    print(f"Saved interest rate plot to {output_path}")
    return output_path

def plot_eu_heatmap(output_dir='output'):
    """
    Create a heatmap showing inflation rates for all EU countries since 2020.
    
    Args:
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    import pandas as pd
    import numpy as np
    import locale
    
    # Set German locale
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'German_Germany.1252')
        except:
            pass
    
    print("Fetching EU-wide inflation data for heatmap...")
    try:
        import eurostat
        df = eurostat.get_data_df('prc_hicp_manr', flags=False)
        
        if 'geo\\TIME_PERIOD' in df.columns:
            df = df.rename(columns={'geo\\TIME_PERIOD': 'geo'})
        
        # Filter for all EU countries and all-items HICP
        df_filtered = df[df['coicop'].str.startswith('CP00')].copy()
        
        # Get time columns
        time_columns = [col for col in df_filtered.columns if isinstance(col, str) and '-' in str(col)]
        
        # Reshape data
        df_long = df_filtered.melt(
            id_vars=['geo'],
            value_vars=time_columns,
            var_name='period',
            value_name='inflation_rate'
        )
        
        df_long['date'] = pd.to_datetime(df_long['period'], format='%Y-%m', errors='coerce')
        df_long['inflation_rate'] = pd.to_numeric(df_long['inflation_rate'], errors='coerce')
        df_long = df_long.dropna(subset=['inflation_rate', 'date'])
        
        # Filter from 2020 onwards
        df_long = df_long[df_long['date'] >= '2020-01-01']
        
        # Get top 15 countries with most complete data
        country_counts = df_long.groupby('geo').size().sort_values(ascending=False)
        top_countries = country_counts.head(15).index.tolist()
        df_long = df_long[df_long['geo'].isin(top_countries)]
        
        # Create year-month column for better grouping
        df_long['year_month'] = df_long['date'].dt.to_period('M').astype(str)
        
        # Aggregate to quarterly data to make heatmap more readable
        df_long['quarter'] = df_long['date'].dt.to_period('Q')
        df_quarterly = df_long.groupby(['geo', 'quarter'])['inflation_rate'].mean().reset_index()
        df_quarterly['quarter_str'] = df_quarterly['quarter'].astype(str)
        
        plot = (ggplot(df_quarterly, aes(x='quarter_str', y='geo', fill='inflation_rate'))
                + geom_tile(color='white', size=0.5)
                + scale_fill_gradient2(low='#3498db', mid='#f1c40f', high='#e74c3c', 
                                       midpoint=4, limits=[df_quarterly['inflation_rate'].min(), 
                                                          df_quarterly['inflation_rate'].max()])
                + theme_minimal()
                + labs(title='Inflationsrate EU-Länder im Vergleich (Quartalsdurchschnitt seit 2020)',
                      x='Quartal',
                      y='Land',
                      fill='Inflation (%)',
                      caption='Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.')
                + theme(
                    plot_title=element_text(size=12, face="bold", margin={'b': 10}),
                    plot_caption=element_text(size=8, hjust=0, margin={'t': 10}),
                    axis_title=element_text(size=10),
                    axis_text=element_text(size=8),
                    axis_text_x=element_text(angle=90, hjust=1, vjust=0.5),
                    legend_position='right',
                    legend_title=element_text(size=9),
                    legend_text=element_text(size=8),
                    figure_size=(16, 10),
                    panel_background=element_rect(fill='white'),
                    plot_background=element_rect(fill='white')
                ))
        
        output_path = os.path.join(output_dir, 'eu_inflation_heatmap.png')
        plot.save(output_path, dpi=300)
        
        print(f"Saved heatmap to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_historical_comparison(output_dir='output'):
    """
    Create a historical comparison plot since Euro introduction with financial crisis markers.
    
    Args:
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    import pandas as pd
    import numpy as np
    import locale
    
    # Set German locale for month names
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'German_Germany.1252')
        except:
            pass
    
    # Fetch historical data from 1999 (Euro introduction)
    print("Fetching historical data since Euro introduction...")
    try:
        import eurostat
        df = eurostat.get_data_df('prc_hicp_manr', flags=False)
        
        if 'geo\\TIME_PERIOD' in df.columns:
            df = df.rename(columns={'geo\\TIME_PERIOD': 'geo'})
        
        df_filtered = df[
            (df['coicop'].str.startswith('CP00')) &
            (df['geo'].isin(['AT', 'DE', 'EA20', 'EA19']))
        ].copy()
        
        if 'EA20' in df_filtered['geo'].values and 'EA19' in df_filtered['geo'].values:
            df_filtered = df_filtered[df_filtered['geo'] != 'EA19']
        
        # Get time columns
        time_columns = [col for col in df_filtered.columns if isinstance(col, str) and '-' in str(col)]
        
        df_long = df_filtered.melt(
            id_vars=['geo'],
            value_vars=time_columns,
            var_name='period',
            value_name='inflation_rate'
        )
        
        df_long['date'] = pd.to_datetime(df_long['period'], format='%Y-%m', errors='coerce')
        df_long['inflation_rate'] = pd.to_numeric(df_long['inflation_rate'], errors='coerce')
        df_long = df_long.dropna(subset=['inflation_rate', 'date'])
        
        # Filter from 2002 onwards 
        df_long = df_long[df_long['date'] >= '2002-01-01']
        
        df_long['country'] = df_long['geo'].map({
            'AT': 'Österreich',
            'DE': 'Deutschland',
            'EA20': 'Eurozone',
            'EA19': 'Eurozone'
        })
        
        # Remove any rows where country mapping failed
        df_long = df_long.dropna(subset=['country'])
        
        # Define key events
        events = pd.DataFrame({
            'date': pd.to_datetime(['2008-09-15', '2020-03-11', '2022-02-24']),
            'label': ['Finanzkrise', 'COVID-19', 'Ukraine-Krieg'],
            'y_pos': [8, 2, 9]
        })
        
        # Calculate y-axis limits with 1.0 increments
        y_min = np.floor(df_long['inflation_rate'].min())
        y_max = np.ceil(df_long['inflation_rate'].max())
        y_breaks = np.arange(y_min, y_max + 1, 1.0)
        
        plot = (ggplot(df_long, aes(x='date', y='inflation_rate', color='country'))
                + geom_line(size=1.3, alpha=0.9)
                + geom_point(size=1.8, alpha=0.6)
                + geom_vline(data=events, mapping=aes(xintercept='date'), 
                            linetype='dashed', alpha=0.4, color='#333333')
                + geom_text(data=events, mapping=aes(x='date', y='y_pos', label='label'),
                           angle=90, va='bottom', ha='right', size=9, color='#333333',
                           nudge_y=0.3)
                + scale_color_manual(values=['#2E86AB', '#A23B72', '#F18F01'],
                                    labels=['Österreich', 'Deutschland', 'Eurozone'])
                + scale_x_datetime(date_labels='%Y', date_breaks='2 years')
                + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
                + theme_minimal()
                + labs(title='Langfristige Inflationsentwicklung (seit 2002)',
                      x='',
                      y='Inflationsrate (%)',
                      color='Region',
                      caption='Quelle: Eurostat (2025). Markierte kritische Ereignisse: Finanzkrise 2008, COVID-19 Pandemie, Ukraine-Krieg.')
                + theme(
                    plot_title=element_text(size=14, face="bold", margin={'b': 15}),
                    plot_caption=element_text(size=9, hjust=0, margin={'t': 12}, color='#666666'),
                    axis_title=element_text(size=12),
                    axis_title_x=element_blank(),
                    axis_text=element_text(size=10),
                    axis_text_x=element_text(angle=0, hjust=0.5),
                    legend_position='top',
                    legend_title=element_blank(),
                    legend_text=element_text(size=11),
                    legend_box_margin=5,
                    panel_grid_minor_x=element_blank(),
                    panel_grid_major_x=element_blank(),
                    panel_grid_minor_y=element_line(alpha=0.25, linetype='dotted', size=0.5, color='#CCCCCC'),
                    panel_grid_major_y=element_line(alpha=0.5, linetype='dotted', size=0.8, color='#999999'),
                    figure_size=(15, 7),
                    panel_background=element_rect(fill='white'),
                    plot_background=element_rect(fill='#FAFAFA')
                ))
        
        output_path = os.path.join(output_dir, 'historical_comparison.png')
        plot.save(output_path, dpi=300)
        
        print(f"Saved plot to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error creating historical plot: {e}")
        return None

