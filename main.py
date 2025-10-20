#!/usr/bin/env python3
"""
Daily Hydrology Data Automation System
Fetches USGS streamflow data, performs analysis, and auto-commits to GitHub
"""

import os
import sys
from datetime import datetime
import yaml
from pathlib import Path

from data_fetcher import USGSDataFetcher
from analyzer import StreamflowAnalyzer
from visualizer import DataVisualizer
from git_manager import GitManager


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution function"""
    print(f"=== Hydrology Automation System ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config = load_config()
        print(f"✓ Configuration loaded")
        
        # Initialize modules
        fetcher = USGSDataFetcher(config['data_sources'])
        analyzer = StreamflowAnalyzer(config['analysis'])
        visualizer = DataVisualizer(config['visualization'])
        git_mgr = GitManager(config['git'])
        print(f"✓ Modules initialized")
        
        # Fetch data
        print(f"\nFetching data from USGS...")
        data = fetcher.fetch_latest_data()
        if data is None or data.empty:
            print("⚠ No new data available. Skipping today.")
            return
        print(f"✓ Data fetched: {len(data)} records")
        
        # Perform analysis
        print(f"\nPerforming analysis...")
        results = analyzer.analyze(data)
        print(f"✓ Analysis complete")
        print(f"  - Mean flow: {results['mean_flow']:.2f} cfs")
        print(f"  - Max flow: {results['max_flow']:.2f} cfs")
        print(f"  - Trend: {results['trend']}")
        
        # Generate visualizations
        print(f"\nGenerating visualizations...")
        plots = visualizer.create_plots(data, results)
        print(f"✓ Visualizations created: {len(plots)} plots")
        
        # Save results
        print(f"\nSaving results...")
        result_file = Path('results') / f"analysis_{datetime.now().strftime('%Y%m%d')}.json"
        result_file.parent.mkdir(exist_ok=True)
        analyzer.save_results(results, result_file)
        print(f"✓ Results saved to {result_file}")
        
        # Git commit and push
        if config['git']['auto_commit']:
            print(f"\nCommitting to GitHub...")
            commit_msg = f"Daily update: {datetime.now().strftime('%Y-%m-%d')} - {results['summary']}"
            success = git_mgr.commit_and_push(commit_msg)
            if success:
                print(f"✓ Changes committed and pushed to GitHub")
            else:
                print(f"⚠ Git operations skipped (no changes or error)")
        
        print(f"\n=== Automation Complete ===")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
