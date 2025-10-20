# Streamflow Data Analysis

Automated system for monitoring and analyzing USGS streamflow data. Fetches real-time hydrological data, performs statistical analysis, and generates visualizations.

## Overview

This project monitors streamflow conditions at USGS gauging stations. It analyzes trends, detects anomalies, and creates visualizations to track water flow patterns over time.

## Setup

Install the required Python packages:
```bash
pip install -r requirements.txt
```

Configure monitoring sites by editing `config.yaml`:
```yaml
data_sources:
  usgs_sites:
    - "01646500"  # Your USGS site codes here
```

Run the analysis:
```bash
python main.py
```

## Data Source

Uses USGS Water Services API (public domain, no authentication required):
- Real-time streamflow measurements
- Historical data available
- Free access for research and analysis

## Analysis Features

The system performs:
- Statistical summaries (mean, median, percentiles)
- Trend detection using linear regression
- Anomaly identification
- Flow condition classification
- Time series visualization

## Automated Updates

GitHub Actions workflow runs daily to fetch new data and update analysis results. The workflow file is located in `.github/workflows/daily-update.yml`.

To enable automatic updates:
1. Push this repository to GitHub
2. GitHub Actions will run automatically
3. Results are committed daily with current analysis

## Project Structure

```
.
├── main.py              - Main script
├── data_fetcher.py      - USGS API interface
├── analyzer.py          - Statistical analysis
├── visualizer.py        - Plot generation
├── git_manager.py       - Repository management
├── config.yaml          - Configuration
├── requirements.txt     - Dependencies
└── .github/workflows/   - Automation schedule
```

## Output

Generated files:
- `data/` - Raw data files
- `results/` - Analysis JSON files
- `plots/` - Visualization images

## Notes

This is a research tool for hydrological data analysis. All data comes from public sources and analysis code is original work.
