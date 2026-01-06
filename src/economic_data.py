"""Economic data collection from FRED (Federal Reserve Economic Data)"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
import pandas as pd
from rich.console import Console

from src.config import FRED_API_KEY, FRED_API_URL, ECONOMIC_INDICATORS, HISTORICAL_YEARS

console = Console()


class EconomicDataCollector:
    """Collects economic indicators from FRED API"""
    
    def __init__(self, api_key: Optional[str] = FRED_API_KEY):
        self.api_key = api_key
        self.base_url = FRED_API_URL
        self.indicators = ECONOMIC_INDICATORS
        
        if not self.api_key:
            console.print("[yellow]⚠[/yellow] FRED API key not configured.")
            console.print("[dim]Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html[/dim]")
    
    def fetch_m2_data(self, years: int = HISTORICAL_YEARS, region: str = "US") -> pd.DataFrame:
        """
        Fetch M2 Money Supply data from FRED
        
        Args:
            years: Number of years of historical data
            region: 'US' or 'EUROZONE'
        
        Returns:
            DataFrame with date index and value column
        """
        if not self.api_key:
            console.print("[red]✗[/red] Cannot fetch M2 data: FRED API key not configured")
            return pd.DataFrame()
        
        # Select appropriate series
        if region == "EUROZONE":
            series_id = self.indicators['M2_EUROZONE']['fred_series']
            console.print(f"[dim]Fetching Eurozone M2 Money Supply data from FRED...[/dim]")
        else:
            series_id = self.indicators['M2']['fred_series']
            console.print(f"[dim]Fetching US M2 Money Supply data from FRED...[/dim]")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' not in data:
                console.print(f"[red]✗[/red] No {region} M2 data returned from FRED")
                return pd.DataFrame()
            
            observations = data['observations']
            
            # Convert to DataFrame
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Remove any rows with missing values
            df = df.dropna(subset=['value'])
            
            # Set date as index
            df = df.set_index('date')[['value']]
            
            console.print(f"[green]✓[/green] Fetched {len(df)} {region} M2 observations")
            
            return df
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗[/red] Error fetching {region} M2 data: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            console.print(f"[red]✗[/red] Unexpected error: {str(e)}")
            return pd.DataFrame()
    
    def update_m2_data(self, last_date: str, region: str = "US") -> Optional[pd.DataFrame]:
        """
        Fetch M2 data since last update
        
        Args:
            last_date: Last date in database (YYYY-MM-DD)
            region: 'US' or 'EUROZONE'
        
        Returns:
            DataFrame with new data or None
        """
        if not self.api_key:
            return None
        
        # Select appropriate series
        if region == "EUROZONE":
            series_id = self.indicators['M2_EUROZONE']['fred_series']
        else:
            series_id = self.indicators['M2']['fred_series']
        
        try:
            last_dt = datetime.strptime(last_date, '%Y-%m-%d')
            start_date = last_dt + timedelta(days=1)
            end_date = datetime.now()
            
            if start_date.date() >= end_date.date():
                console.print(f"[blue]ℹ[/blue] {region} M2 data already up to date")
                return None
            
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'observation_start': start_date.strftime('%Y-%m-%d'),
                'observation_end': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' not in data or len(data['observations']) == 0:
                console.print(f"[blue]ℹ[/blue] No new {region} M2 data available")
                return None
            
            observations = data['observations']
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            df = df.set_index('date')[['value']]
            
            if not df.empty:
                console.print(f"[green]✓[/green] {region} M2 updated to {df.index[-1].strftime('%Y-%m-%d')}")
            
            return df if not df.empty else None
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error updating {region} M2 data: {str(e)}")
            return None
    
    def calculate_m2_growth_rate(self, m2_data: pd.DataFrame, 
                                 months_back: int = 12) -> Dict[str, float]:
        """
        Calculate M2 growth rates
        
        Args:
            m2_data: DataFrame with M2 values
            months_back: Number of months to look back for YoY calculation
        
        Returns:
            Dictionary with current value, YoY growth, and trend
        """
        if m2_data.empty or len(m2_data) < months_back:
            return {
                'current_value': None,
                'yoy_growth': None,
                'mom_growth': None,
                'trend': 'unknown'
            }
        
        current_value = m2_data['value'].iloc[-1]
        
        # Year-over-year growth
        if len(m2_data) >= months_back:
            past_value = m2_data['value'].iloc[-months_back]
            yoy_growth = ((current_value - past_value) / past_value) * 100
        else:
            yoy_growth = None
        
        # Month-over-month growth (last available)
        if len(m2_data) >= 2:
            prev_value = m2_data['value'].iloc[-2]
            mom_growth = ((current_value - prev_value) / prev_value) * 100
        else:
            mom_growth = None
        
        # Determine trend
        if yoy_growth is not None:
            if yoy_growth > 5:
                trend = 'strong_expansion'
            elif yoy_growth > 2:
                trend = 'expansion'
            elif yoy_growth > -2:
                trend = 'stable'
            else:
                trend = 'contraction'
        else:
            trend = 'unknown'
        
        return {
            'current_value': current_value,
            'yoy_growth': yoy_growth,
            'mom_growth': mom_growth,
            'trend': trend
        }
    
    def assess_m2_favorability(self, yoy_growth: Optional[float]) -> Dict[str, any]:
        """
        Assess whether M2 growth is favorable for investing
        
        Args:
            yoy_growth: Year-over-year growth percentage
        
        Returns:
            Dictionary with favorability assessment
        """
        if yoy_growth is None:
            return {
                'is_favorable': None,
                'score': 0,
                'message': 'M2 data not available',
                'impact': 'neutral'
            }
        
        if yoy_growth > 5:
            return {
                'is_favorable': True,
                'score': 20,
                'message': f'Strong M2 expansion (+{yoy_growth:.1f}% YoY) supports asset prices',
                'impact': 'strongly_positive'
            }
        elif yoy_growth > 2:
            return {
                'is_favorable': True,
                'score': 10,
                'message': f'M2 expanding (+{yoy_growth:.1f}% YoY) moderately supports investment',
                'impact': 'positive'
            }
        elif yoy_growth > -2:
            return {
                'is_favorable': None,
                'score': 0,
                'message': f'M2 stable ({yoy_growth:+.1f}% YoY) - neutral environment',
                'impact': 'neutral'
            }
        else:
            return {
                'is_favorable': False,
                'score': -15,
                'message': f'M2 contracting ({yoy_growth:.1f}% YoY) - headwind for assets',
                'impact': 'negative'
            }
