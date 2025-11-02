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
    Create a line plot comparing inflation in Austria and Euro zone.
    
    Args:
        df (pd.DataFrame): Processed inflation data
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    import pandas as pd
    
    # Define important events (cornerstones) - APA style with exact dates
    events = [
        {'date': pd.Timestamp('2020-03-16'), 'label': 'COVID-19\nLockdown\nMärz 2020', 'color': '#e74c3c', 'y_pos': 0.95},
        {'date': pd.Timestamp('2022-02-24'), 'label': 'Ukraine-\nKrieg\nFebruar 2022', 'color': '#e67e22', 'y_pos': 0.95},
        {'date': pd.Timestamp('2022-09-01'), 'label': 'Energiekrise\nEskalation\nSeptember 2022', 'color': '#8e44ad', 'y_pos': 0.55},
        {'date': pd.Timestamp('2025-04-01'), 'label': 'Liberation Day\nUS-Zölle\nApril 2025', 'color': '#16a085', 'y_pos': 0.95}
    ]
    
    plot = (ggplot(df, aes(x='date', y='inflation_rate', color='country', group='country'))
            + geom_line(size=1.2)
            + geom_point(size=1.5, alpha=0.4)
            + scale_color_manual(values=['#1f77b4', '#2ca02c', '#ff7f0e'])  # Blue=AT, Green=DE, Orange=EA
            + theme_minimal()
            + labs(title='Monatliche Inflationsrate im Vergleich',
                  x='',
                  y='Inflationsrate (%)',
                  color='',
                  caption='Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex, monatliche Änderungsrate zum Vorjahresmonat.')
            + theme(
                plot_title=element_text(size=13, face="bold", margin={'b': 10}),
                plot_caption=element_text(size=8, hjust=0, margin={'t': 10}),
                axis_title=element_text(size=11),
                axis_title_x=element_blank(),
                axis_text=element_text(size=9),
                axis_text_x=element_text(angle=45, hjust=1),
                legend_position='top',
                legend_title=element_blank(),
                legend_text=element_text(size=10),
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.4, linetype='dotted', size=0.5),
                panel_grid_major_y=element_line(alpha=0.7, linetype='dotted', size=0.8),
                figure_size=(12, 7),
                panel_background=element_rect(fill='white'),
                plot_background=element_rect(fill='white')
            ))
    
    # Add vertical lines for important events
    for event in events:
        plot = plot + geom_vline(xintercept=event['date'], 
                                 linetype='dashed', 
                                 color=event['color'], 
                                 size=0.6, 
                                 alpha=0.6)
        plot = plot + annotate('text', 
                              x=event['date'], 
                              y=df['inflation_rate'].max() * event['y_pos'],
                              label=event['label'],
                              color=event['color'],
                              size=7,
                              fontweight='bold',
                              ha='left',
                              va='top')
    
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
                panel_grid_minor_y=element_line(alpha=0.4, linetype='dotted', size=0.5),
                panel_grid_major_y=element_line(alpha=0.7, linetype='dotted', size=0.8),
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
                panel_grid_minor_y=element_line(alpha=0.4, linetype='dotted', size=0.5),
                panel_grid_major_y=element_line(alpha=0.7, linetype='dotted', size=0.8),
                figure_size=(12, 9),
                panel_background=element_rect(fill='white'),
                plot_background=element_rect(fill='white')
            ))
    
    output_path = os.path.join(output_dir, 'statistics_comparison.png')
    plot.save(output_path, dpi=300)
    
    print(f"Saved plot to {output_path}")
    return output_path


def plot_cumulative_inflation(cumulative, output_dir='output'):
    """
    Create a bar plot showing cumulative inflation.
    
    Args:
        cumulative (dict): Cumulative inflation dictionary
        output_dir (str): Directory to save the plot
        
    Returns:
        str: Path to the saved plot
    """
    # Convert dictionary to DataFrame for plotting
    plot_df = pd.DataFrame({
        'country': list(cumulative.keys()),
        'value': list(cumulative.values())
    })
    
    # Add formatted labels to the DataFrame
    plot_df['label'] = plot_df['value'].apply(lambda x: f'{x:.1f}%')
    
    plot = (ggplot(plot_df, aes(x='country', y='value', fill='country'))
            + geom_col(alpha=0.7, show_legend=False)
            + scale_fill_manual(values=['#1f77b4', '#ff7f0e'])
            + geom_text(aes(label='label'),
                       va='bottom', size=11)
            + theme_minimal()
            + labs(title='Kumulative Inflation seit 2020',
                  x='',
                  y='Kumulative Inflationsrate (%)')
            + theme(
                plot_title=element_text(size=14, face="bold"),
                axis_title=element_text(size=12),
                axis_text=element_text(size=10),
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.2, linetype='dotted'),
                panel_grid_major_y=element_line(alpha=0.4, linetype='dotted'),
                figure_size=(10, 6)
            ))
    
    output_path = os.path.join(output_dir, 'cumulative_inflation.png')
    plot.save(output_path, dpi=300)
    
    print(f"Saved plot to {output_path}")
    return output_path
