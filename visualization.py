"""
Module for generating visualizations of inflation data.
"""
import matplotlib.pyplot as plt
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
    plt.figure(figsize=(12, 6))
    
    for geo in df['geo'].unique():
        region_data = df[df['geo'] == geo].sort_values('year')
        country_name = region_data['country'].iloc[0]
        plt.plot(region_data['year'], region_data['inflation_rate'], 
                marker='o', label=country_name, linewidth=2)
    
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Inflation Rate (%)', fontsize=12)
    plt.title('Inflation Comparison: Austria vs Euro Zone', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'inflation_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
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
    
    plt.figure(figsize=(12, 6))
    
    colors = ['green' if x < 0 else 'red' for x in comparison_df['Difference (AT - EA)']]
    
    plt.bar(comparison_df.index, comparison_df['Difference (AT - EA)'], 
            color=colors, alpha=0.7)
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Difference in Inflation Rate (% points)', fontsize=12)
    plt.title('Austria Inflation Rate Difference from Euro Zone\n(Positive = Higher in Austria)', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'inflation_difference.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
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
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Statistical Comparison: Austria vs Euro Zone', fontsize=16, fontweight='bold')
    
    metrics = [
        ('mean', 'Average Inflation Rate (%)', axes[0, 0]),
        ('median', 'Median Inflation Rate (%)', axes[0, 1]),
        ('min', 'Minimum Inflation Rate (%)', axes[1, 0]),
        ('max', 'Maximum Inflation Rate (%)', axes[1, 1])
    ]
    
    countries = list(stats.keys())
    
    for metric, title, ax in metrics:
        values = [stats[country][metric] for country in countries]
        bars = ax.bar(countries, values, color=['#1f77b4', '#ff7f0e'], alpha=0.7)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('Rate (%)', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}%', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'statistics_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
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
    plt.figure(figsize=(10, 6))
    
    countries = list(cumulative.keys())
    values = list(cumulative.values())
    
    bars = plt.bar(countries, values, color=['#1f77b4', '#ff7f0e'], alpha=0.7)
    
    plt.ylabel('Cumulative Inflation Rate (%)', fontsize=12)
    plt.title('Cumulative Inflation Over the Period', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'cumulative_inflation.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved plot to {output_path}")
    return output_path
