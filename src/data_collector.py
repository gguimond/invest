"""Data collection from Yahoo Finance using yfinance"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import TICKERS, HISTORICAL_YEARS

console = Console()


class DataCollector:
    """Collects market data from Yahoo Finance"""
    
    def __init__(self):
        self.tickers = TICKERS
        self.historical_years = HISTORICAL_YEARS
    
    def download_historical_data(self, ticker: str, years: int = None) -> pd.DataFrame:
        """
        Download historical data for a ticker
        
        Args:
            ticker: Yahoo Finance ticker symbol
            years: Number of years of historical data (default from config)
        
        Returns:
            DataFrame with OHLCV data
        """
        if years is None:
            years = self.historical_years
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Downloading {ticker}...", total=None)
                
                data = yf.download(
                    ticker,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    progress=False,
                    auto_adjust=False
                )
                
                progress.update(task, completed=True)
            
            if data.empty:
                console.print(f"[yellow]⚠[/yellow] No data returned for {ticker}")
                return pd.DataFrame()
            
            # Handle multi-index columns (when downloading multiple tickers)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            console.print(f"[green]✓[/green] Downloaded {len(data)} days for {ticker}")
            return data
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error downloading {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def download_incremental_data(self, ticker: str, 
                                  last_date: str) -> pd.DataFrame:
        """
        Download data since the last update
        
        Args:
            ticker: Yahoo Finance ticker symbol
            last_date: Last date in database (YYYY-MM-DD)
        
        Returns:
            DataFrame with new data
        """
        try:
            last_dt = datetime.strptime(last_date, '%Y-%m-%d')
            start_date = last_dt + timedelta(days=1)
            end_date = datetime.now()
            
            # If dates are the same or start > end, no new data needed
            if start_date.date() >= end_date.date():
                return pd.DataFrame()
            
            data = yf.download(
                ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False,
                auto_adjust=False
            )
            
            # Handle multi-index columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            if not data.empty:
                console.print(f"[green]✓[/green] Downloaded {len(data)} new days for {ticker}")
            
            return data
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error downloading incremental data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get the current/latest price for a ticker"""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            # Try different price fields
            price = info.get('currentPrice') or info.get('regularMarketPrice') or \
                    info.get('previousClose')
            
            return float(price) if price else None
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Could not get current price for {ticker}: {str(e)}")
            return None
    
    def download_all_indices(self) -> dict:
        """
        Download historical data for all configured indices
        
        Returns:
            Dictionary with index_name -> DataFrame
        """
        results = {}
        
        console.print("\n[bold cyan]📊 Downloading Market Data[/bold cyan]")
        console.print("━" * 50)
        
        for index_name, config in self.tickers.items():
            ticker = config['ticker']
            name = config['name']
            
            console.print(f"\n[bold]{name}[/bold] ({ticker})")
            data = self.download_historical_data(ticker)
            
            if not data.empty:
                results[index_name] = data
            else:
                console.print(f"[red]✗[/red] Failed to download {name}")
        
        console.print("\n" + "━" * 50)
        return results
    
    def update_index_data(self, index_name: str, last_date: str) -> Optional[pd.DataFrame]:
        """
        Update data for a single index since last_date
        
        Args:
            index_name: Name of the index (SP500, CW8, EURUSD)
            last_date: Last date in database
        
        Returns:
            DataFrame with new data or None
        """
        if index_name not in self.tickers:
            console.print(f"[red]✗[/red] Unknown index: {index_name}")
            return None
        
        ticker = self.tickers[index_name]['ticker']
        name = self.tickers[index_name]['name']
        
        data = self.download_incremental_data(ticker, last_date)
        
        if not data.empty:
            console.print(f"[green]✓[/green] {name}: Updated to {data.index[-1].strftime('%Y-%m-%d')}")
        else:
            console.print(f"[blue]ℹ[/blue] {name}: Already up to date")
        
        return data if not data.empty else None
    
    def calculate_currency_adjusted_returns(self, sp500_data: pd.DataFrame, 
                                           eur_usd_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate S&P 500 returns in EUR terms
        
        Args:
            sp500_data: S&P 500 price data (USD)
            eur_usd_data: EUR/USD exchange rate data
        
        Returns:
            DataFrame with currency-adjusted returns
        """
        # Align data by date
        df = pd.DataFrame()
        df['sp500_usd_price'] = sp500_data['Adj Close']
        df['eur_usd_rate'] = eur_usd_data['Adj Close']
        
        # Remove NaN values
        df = df.dropna()
        
        # Calculate EUR price
        df['sp500_eur_price'] = df['sp500_usd_price'] / df['eur_usd_rate']
        
        # Calculate returns
        df['sp500_usd_return'] = df['sp500_usd_price'].pct_change() * 100
        df['sp500_eur_return'] = df['sp500_eur_price'].pct_change() * 100
        df['currency_return'] = df['eur_usd_rate'].pct_change() * 100
        
        # Currency impact
        df['currency_impact'] = df['sp500_eur_return'] - df['sp500_usd_return']
        
        # Remove first row (NaN from pct_change)
        df = df.iloc[1:]
        
        return df
    
    def validate_data(self, df: pd.DataFrame, ticker: str) -> Tuple[bool, str]:
        """
        Validate downloaded data for anomalies
        
        Returns:
            Tuple of (is_valid, message)
        """
        if df.empty:
            return False, "No data"
        
        # Check for required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing columns: {', '.join(missing_cols)}"
        
        # Check for excessive NaN values
        nan_pct = (df.isnull().sum() / len(df) * 100).max()
        if nan_pct > 10:
            return False, f"Too many missing values: {nan_pct:.1f}%"
        
        # Check for data continuity (weekends are OK)
        date_range = (df.index[-1] - df.index[0]).days
        expected_days = date_range * 5 / 7  # Approximately 5 trading days per week
        
        if len(df) < expected_days * 0.7:  # Allow 30% gap for holidays
            return False, f"Data appears incomplete: {len(df)} days over {date_range} days"
        
        return True, "Data validated successfully"
