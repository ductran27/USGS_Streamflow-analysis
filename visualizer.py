"""
Visualizer Module
Creates plots and visualizations for hydrological data
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pathlib import Path
import seaborn as sns


class DataVisualizer:
    """Create visualizations for streamflow data"""
    
    def __init__(self, config):
        """Initialize visualizer with configuration"""
        self.config = config
        self.plots_dir = Path('plots')
        self.plots_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def create_plots(self, df, results):
        """
        Create all visualizations
        
        Args:
            df: pandas.DataFrame with streamflow data
            results: dict with analysis results
        
        Returns:
            list: Paths to created plot files
        """
        plots = []
        
        # Time series plot
        plots.append(self._plot_time_series(df, results))
        
        # Distribution plot
        plots.append(self._plot_distribution(df))
        
        # Statistics summary plot
        plots.append(self._plot_statistics(results))
        
        return plots
    
    def _plot_time_series(self, df, results):
        """Create time series plot of streamflow"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        df_sorted = df.sort_values('dateTime')
        
        # Plot data by site
        for site in df['site_code'].unique():
            site_data = df_sorted[df_sorted['site_code'] == site]
            ax.plot(site_data['dateTime'], site_data['discharge_cfs'], 
                   label=site_data['site_name'].iloc[0], marker='o', markersize=3, alpha=0.7)
        
        # Add mean line
        ax.axhline(y=results['mean_flow'], color='red', linestyle='--', 
                   label=f"Mean: {results['mean_flow']:.0f} cfs", linewidth=2)
        
        # Formatting
        ax.set_xlabel('Date/Time', fontsize=12)
        ax.set_ylabel('Discharge (cubic feet per second)', fontsize=12)
        ax.set_title('Streamflow Time Series', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        plt.xticks(rotation=45)
        
        # Add status text
        status_text = f"Status: {results['flow_status']['status']}\nTrend: {results['trend_direction']}"
        ax.text(0.02, 0.98, status_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'timeseries_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _plot_distribution(self, df):
        """Create distribution plot"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(df['discharge_cfs'].dropna(), bins=30, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Discharge (cfs)', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Distribution of Streamflow', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(df['discharge_cfs'].dropna(), vert=True)
        ax2.set_ylabel('Discharge (cfs)', fontsize=11)
        ax2.set_title('Streamflow Box Plot', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'distribution_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _plot_statistics(self, results):
        """Create statistics summary visualization"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data
        stats_labels = ['Mean', 'Median', 'Min', 'Max', 'Q25', 'Q75', 'Q90']
        stats_values = [
            results['mean_flow'],
            results['median_flow'],
            results['min_flow'],
            results['max_flow'],
            results['percentile_25'],
            results['percentile_75'],
            results['percentile_90']
        ]
        
        # Create bar chart
        bars = ax.barh(stats_labels, stats_values, color='steelblue', alpha=0.7, edgecolor='black')
        
        # Add value labels
        for i, (label, value) in enumerate(zip(stats_labels, stats_values)):
            ax.text(value, i, f' {value:.0f}', va='center', fontsize=10)
        
        ax.set_xlabel('Discharge (cubic feet per second)', fontsize=12)
        ax.set_title('Statistical Summary', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add status info
        info_text = (f"Flow Status: {results['flow_status']['status']}\n"
                    f"Trend: {results['trend_direction']}\n"
                    f"Records: {results['total_records']}\n"
                    f"Anomalies: {results['anomaly_count']}")
        ax.text(0.98, 0.02, info_text, transform=ax.transAxes, 
                fontsize=9, verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'statistics_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
