"""
Analyzer Module
Performs statistical analysis on hydrological data
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path


class StreamflowAnalyzer:
    """Analyze streamflow data and compute statistics"""
    
    def __init__(self, config):
        """Initialize analyzer with configuration"""
        self.config = config
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
    
    def analyze(self, df):
        """
        Perform comprehensive analysis on streamflow data
        
        Args:
            df: pandas.DataFrame with streamflow data
        
        Returns:
            dict: Analysis results
        """
        results = {}
        
        # Basic statistics
        results['mean_flow'] = df['discharge_cfs'].mean()
        results['median_flow'] = df['discharge_cfs'].median()
        results['std_flow'] = df['discharge_cfs'].std()
        results['min_flow'] = df['discharge_cfs'].min()
        results['max_flow'] = df['discharge_cfs'].max()
        results['total_records'] = len(df)
        
        # Percentiles
        results['percentile_25'] = df['discharge_cfs'].quantile(0.25)
        results['percentile_75'] = df['discharge_cfs'].quantile(0.75)
        results['percentile_90'] = df['discharge_cfs'].quantile(0.90)
        
        # Trend analysis
        results['trend'] = self._analyze_trend(df)
        results['trend_slope'] = results['trend']['slope']
        results['trend_direction'] = results['trend']['direction']
        
        # Anomaly detection
        results['anomalies'] = self._detect_anomalies(df)
        results['anomaly_count'] = len(results['anomalies'])
        
        # Flow classification
        results['flow_status'] = self._classify_flow(df)
        
        # Recent change
        results['recent_change'] = self._calculate_recent_change(df)
        
        # Summary message
        results['summary'] = self._generate_summary(results)
        
        # Metadata
        results['analysis_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        results['sites_analyzed'] = df['site_code'].unique().tolist()
        
        return results
    
    def _analyze_trend(self, df):
        """Analyze trend using linear regression"""
        df_sorted = df.sort_values('dateTime').copy()
        df_sorted['time_numeric'] = (df_sorted['dateTime'] - df_sorted['dateTime'].min()).dt.total_seconds()
        
        # Remove NaN values
        valid_data = df_sorted[['time_numeric', 'discharge_cfs']].dropna()
        
        if len(valid_data) < 3:
            return {'slope': 0, 'direction': 'insufficient data', 'p_value': 1.0}
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            valid_data['time_numeric'], 
            valid_data['discharge_cfs']
        )
        
        # Determine trend direction
        if p_value > 0.05:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        return {
            'slope': float(slope),
            'direction': direction,
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value)
        }
    
    def _detect_anomalies(self, df):
        """Detect anomalous values using IQR method"""
        Q1 = df['discharge_cfs'].quantile(0.25)
        Q3 = df['discharge_cfs'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = df[
            (df['discharge_cfs'] < lower_bound) | 
            (df['discharge_cfs'] > upper_bound)
        ].copy()
        
        return anomalies[['dateTime', 'discharge_cfs', 'site_name']].to_dict('records')
    
    def _classify_flow(self, df):
        """Classify current flow conditions"""
        latest_flow = df.sort_values('dateTime').iloc[-1]['discharge_cfs']
        mean_flow = df['discharge_cfs'].mean()
        
        percentile = (df['discharge_cfs'] <= latest_flow).mean() * 100
        
        if percentile >= 90:
            status = 'High Flow'
        elif percentile >= 75:
            status = 'Above Normal'
        elif percentile >= 25:
            status = 'Normal'
        elif percentile >= 10:
            status = 'Below Normal'
        else:
            status = 'Low Flow'
        
        return {
            'status': status,
            'latest_flow': float(latest_flow),
            'percentile': float(percentile)
        }
    
    def _calculate_recent_change(self, df):
        """Calculate recent change in flow"""
        df_sorted = df.sort_values('dateTime')
        
        if len(df_sorted) < 2:
            return {'change_pct': 0, 'change_cfs': 0}
        
        latest = df_sorted.iloc[-1]['discharge_cfs']
        previous = df_sorted.iloc[-24]['discharge_cfs'] if len(df_sorted) >= 24 else df_sorted.iloc[0]['discharge_cfs']
        
        change_cfs = latest - previous
        change_pct = (change_cfs / previous * 100) if previous != 0 else 0
        
        return {
            'change_cfs': float(change_cfs),
            'change_pct': float(change_pct)
        }
    
    def _generate_summary(self, results):
        """Generate a human-readable summary"""
        status = results['flow_status']['status']
        trend = results['trend_direction']
        mean = results['mean_flow']
        
        summary = f"{status} conditions (avg: {mean:.0f} cfs, trend: {trend})"
        
        if results['anomaly_count'] > 0:
            summary += f", {results['anomaly_count']} anomalies detected"
        
        return summary
    
    def save_results(self, results, filepath):
        """Save analysis results to JSON file"""
        # Convert any numpy types to native Python types
        results_serializable = self._make_serializable(results)
        
        with open(filepath, 'w') as f:
            json.dump(results_serializable, f, indent=2)
    
    def _make_serializable(self, obj):
        """Convert numpy/pandas types to native Python types"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
