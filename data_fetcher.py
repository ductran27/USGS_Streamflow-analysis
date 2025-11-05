"""
Data Fetcher Module
Fetches hydrological data from USGS Water Services API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json


class USGSDataFetcher:
    """Fetch streamflow data from USGS Water Services"""
    
    BASE_URL = "https://waterservices.usgs.gov/nwis/iv/"
    
    def __init__(self, config):
        """Initialize data fetcher with configuration"""
        self.config = config
        self.site_codes = config.get('usgs_sites', ['01646500'])  # Default: Potomac River at DC
        self.parameter = config.get('parameter', '00060')  # 00060 = Discharge (cfs)
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
    
    def fetch_latest_data(self, days=7):
        """
        Fetch latest streamflow data for configured sites
        
        Args:
            days: Number of days of historical data to fetch
        
        Returns:
            pandas.DataFrame: Streamflow data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_data = []
        
        for site in self.site_codes:
            try:
                print(f"  Fetching data for site {site}...")
                data = self._fetch_site_data(site, start_date, end_date)
                if data is not None:
                    all_data.append(data)
            except Exception as e:
                print(f"  ⚠ Error fetching site {site}: {str(e)}")
                continue
        
        if not all_data:
            return None
        
        # Combine all site data
        df = pd.concat(all_data, ignore_index=True)
        
        # Save raw data
        self._save_data(df)
        
        return df
    
    def _fetch_site_data(self, site_code, start_date, end_date):
        """Fetch data for a single site"""
        params = {
            'format': 'json',
            'sites': site_code,
            'parameterCd': self.parameter,
            'startDT': start_date.strftime('%Y-%m-%d'),
            'endDT': end_date.strftime('%Y-%m-%d'),
            'siteStatus': 'all'
        }
        
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse JSON response
        time_series = data['value']['timeSeries']
        if not time_series:
            return None
        
        values = time_series[0]['values'][0]['value']
        site_name = time_series[0]['sourceInfo']['siteName']
        
        # Convert to DataFrame
        df = pd.DataFrame(values)
        # Normalize timestamps to naive UTC to avoid timezone arithmetic issues (e.g., DST transitions)
        df['dateTime'] = pd.to_datetime(df['dateTime'], utc=True).dt.tz_localize(None)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['site_code'] = site_code
        df['site_name'] = site_name
        df.rename(columns={'value': 'discharge_cfs'}, inplace=True)
        
        return df[['dateTime', 'site_code', 'site_name', 'discharge_cfs']]
    
    def _save_data(self, df):
        """Save data to local storage"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = self.data_dir / f"usgs_data_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"  Data saved to {filename}")
    
    def get_site_info(self, site_code):
        """Get information about a USGS site"""
        url = f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={site_code}&siteOutput=expanded"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
