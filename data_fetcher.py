"""
Data Fetcher Module
Fetches hydrological data from the USGS Water Data API
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class USGSDataFetcher:
    """Fetch streamflow data from the USGS Water Data API"""
    
    BASE_URL = "https://api.waterdata.usgs.gov/ogcapi/v1/collections"
    
    def __init__(self, config):
        """Initialize data fetcher with configuration"""
        self.config = config
        self.site_codes = config.get('usgs_sites', ['01646500'])  # Default: Potomac River at DC
        self.parameter = config.get('parameter', '00060')  # 00060 = Discharge (cfs)
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.fetch_errors = {}  # site code -> why that site gave no data
        self.session = self._build_session()
    
    def _build_session(self):
        """Build a session that rides out short outages and rate limits"""
        retry = Retry(
            total=4,
            backoff_factor=5,
            status_forcelist=(429, 500, 502, 503, 504),
            respect_retry_after_header=False,
            raise_on_status=False
        )
        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=retry))
        api_key = os.getenv('USGS_API_KEY')
        if api_key:
            session.headers['X-Api-Key'] = api_key
        return session
    
    def fetch_latest_data(self, days=7):
        """
        Fetch latest streamflow data for configured sites
        
        Args:
            days: Number of days of historical data to fetch
        
        Returns:
            pandas.DataFrame: Streamflow data
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        all_data = []
        self.fetch_errors = {}
        
        for site in self.site_codes:
            try:
                print(f"  Fetching data for site {site}...")
                data = self._fetch_site_data(site, start_date, end_date)
                if data is not None:
                    all_data.append(data)
                else:
                    self.fetch_errors[site] = 'No records returned'
            except Exception as e:
                print(f"  ⚠ Error fetching site {site}: {str(e)}")
                self.fetch_errors[site] = str(e)
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
            'f': 'json',
            'monitoring_location_id': f'USGS-{site_code}',
            'parameter_code': self.parameter,
            'time': f"{start_date:%Y-%m-%dT%H:%M:%SZ}/{end_date:%Y-%m-%dT%H:%M:%SZ}",
            'limit': 10000
        }
        
        # Follow the "next" links until the whole window is read
        url = f"{self.BASE_URL}/continuous/items"
        values = []
        while url:
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            page = response.json()
            values.extend(feature['properties'] for feature in page['features'])
            url = next((link['href'] for link in page.get('links', []) if link.get('rel') == 'next'), None)
            params = None
        
        if not values:
            return None
        
        site_name = self.get_site_info(site_code)['monitoring_location_name']
        
        # Convert to DataFrame
        df = pd.DataFrame(values)
        # Normalize timestamps to naive UTC to avoid timezone arithmetic issues (e.g., DST transitions)
        df['dateTime'] = pd.to_datetime(df['time'], utc=True).dt.tz_localize(None)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['site_code'] = site_code
        df['site_name'] = site_name
        df = df.rename(columns={'value': 'discharge_cfs'})
        
        return df[['dateTime', 'site_code', 'site_name', 'discharge_cfs']]
    
    def _save_data(self, df):
        """Save data to local storage"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = self.data_dir / f"usgs_data_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"  Data saved to {filename}")
    
    def save_fetch_failure(self):
        """Record a run that got no data, so that it still leaves a commit"""
        filepath = Path('results') / f"fetch_failure_{datetime.now().strftime('%Y%m%d')}.json"
        filepath.parent.mkdir(exist_ok=True)
        record = {
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'errors': self.fetch_errors
        }
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2)
        return filepath
    
    def get_site_info(self, site_code):
        """Get information about a USGS site"""
        url = f"{self.BASE_URL}/monitoring-locations/items/USGS-{site_code}"
        response = self.session.get(url, params={'f': 'json'}, timeout=60)
        response.raise_for_status()
        return response.json()['properties']
