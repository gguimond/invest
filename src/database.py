"""Database operations for storing market data and recommendations"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
from rich.console import Console

from src.config import DB_PATH

console = Console()


class Database:
    """Handles all SQLite database operations"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def initialize_schema(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Historical Prices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_name TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adj_close REAL,
                volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(index_name, date)
            )
        """)
        
        # Currency-Adjusted Returns Cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency_adjusted_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                sp500_usd_price REAL,
                sp500_eur_price REAL,
                eur_usd_rate REAL,
                sp500_usd_return REAL,
                sp500_eur_return REAL,
                currency_impact REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        """)
        
        # News Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT,
                published_at TIMESTAMP,
                url TEXT,
                sentiment_score REAL,
                sentiment_label TEXT,
                related_index TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Recommendations Log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                index_name TEXT,
                recommendation TEXT,
                confidence REAL,
                price_at_recommendation REAL,
                eur_usd_rate REAL,
                currency_impact TEXT,
                reasoning TEXT,
                market_context TEXT
            )
        """)
        
        # System Metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prices_date 
            ON historical_prices(index_name, date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_date 
            ON news_articles(published_at DESC)
        """)
        
        self.conn.commit()
        console.print("[green]✓[/green] Database schema initialized")
    
    def store_historical_prices(self, index_name: str, df: pd.DataFrame):
        """
        Store historical price data for an index
        
        Args:
            index_name: Name of the index (SP500, CW8, EURUSD)
            df: DataFrame with columns: Date, Open, High, Low, Close, Adj Close, Volume
        """
        if df.empty:
            console.print(f"[yellow]⚠[/yellow] No data to store for {index_name}")
            return
        
        df = df.copy()
        df.reset_index(inplace=True)
        df['index_name'] = index_name
        
        # Rename columns to match database schema
        df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Adj Close': 'adj_close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Select only the columns we need
        columns = ['index_name', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
        df = df[columns]
        
        # Convert date to string format for SQLite compatibility
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        # Insert or replace records
        cursor = self.conn.cursor()
        records = df.to_dict('records')
        
        for record in records:
            cursor.execute("""
                INSERT OR REPLACE INTO historical_prices 
                (index_name, date, open, high, low, close, adj_close, volume)
                VALUES (:index_name, :date, :open, :high, :low, :close, :adj_close, :volume)
            """, record)
        
        self.conn.commit()
        console.print(f"[green]✓[/green] Stored {len(df)} records for {index_name}")
    
    def get_historical_prices(self, index_name: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve historical prices for an index
        
        Args:
            index_name: Name of the index
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
        
        Returns:
            DataFrame with historical prices
        """
        query = """
            SELECT date, open, high, low, close, adj_close, volume
            FROM historical_prices
            WHERE index_name = ?
        """
        params = [index_name]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date ASC"
        
        df = pd.read_sql_query(query, self.conn, params=params, parse_dates=['date'])
        
        if not df.empty:
            df.set_index('date', inplace=True)
        
        return df
    
    def get_last_update_date(self, index_name: str) -> Optional[str]:
        """Get the date of the most recent data for an index"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MAX(date) as last_date
            FROM historical_prices
            WHERE index_name = ?
        """, (index_name,))
        
        result = cursor.fetchone()
        return result['last_date'] if result and result['last_date'] else None
    
    def set_metadata(self, key: str, value: str):
        """Store or update a metadata value"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        self.conn.commit()
    
    def get_metadata(self, key: str) -> Optional[str]:
        """Retrieve a metadata value"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else None
    
    def database_exists(self) -> bool:
        """Check if the database file exists and has tables"""
        if not Path(self.db_path).exists():
            return False
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='historical_prices'
        """)
        return cursor.fetchone() is not None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the database"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Count records for each index
        for index_name in ['SP500', 'CW8', 'EURUSD']:
            cursor.execute("""
                SELECT COUNT(*) as count, MIN(date) as first_date, MAX(date) as last_date
                FROM historical_prices
                WHERE index_name = ?
            """, (index_name,))
            result = cursor.fetchone()
            stats[index_name] = {
                'records': result['count'],
                'first_date': result['first_date'],
                'last_date': result['last_date']
            }
        
        # News articles count
        cursor.execute("SELECT COUNT(*) as count FROM news_articles")
        stats['news_articles'] = cursor.fetchone()['count']
        
        # Recommendations count
        cursor.execute("SELECT COUNT(*) as count FROM recommendations_log")
        stats['recommendations'] = cursor.fetchone()['count']
        
        # Database file size
        stats['db_size_mb'] = Path(self.db_path).stat().st_size / (1024 * 1024)
        
        return stats
    
    def store_currency_adjusted_returns(self, df: pd.DataFrame):
        """Store currency-adjusted returns for S&P 500"""
        if df.empty:
            return
        
        df = df.copy()
        
        # Reset index to get date as a column
        df.reset_index(inplace=True)
        
        # Rename index column to 'date' if needed
        if df.columns[0] != 'date':
            df.rename(columns={df.columns[0]: 'date'}, inplace=True)
        
        # Convert date to string format for SQLite compatibility
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        records = df.to_dict('records')
        
        for record in records:
            cursor.execute("""
                INSERT OR REPLACE INTO currency_adjusted_returns 
                (date, sp500_usd_price, sp500_eur_price, eur_usd_rate, 
                 sp500_usd_return, sp500_eur_return, currency_impact)
                VALUES (:date, :sp500_usd_price, :sp500_eur_price, :eur_usd_rate,
                        :sp500_usd_return, :sp500_eur_return, :currency_impact)
            """, record)
        
        self.conn.commit()
    
    def log_recommendation(self, index_name: str, recommendation: str, confidence: float,
                          price: float, eur_usd_rate: Optional[float] = None,
                          currency_impact: Optional[str] = None, reasoning: Optional[str] = None,
                          market_context: Optional[str] = None):
        """Log an investment recommendation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations_log 
            (index_name, recommendation, confidence, price_at_recommendation, 
             eur_usd_rate, currency_impact, reasoning, market_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (index_name, recommendation, confidence, price, eur_usd_rate, 
              currency_impact, reasoning, market_context))
        self.conn.commit()
    
    def export_to_csv(self, output_dir: str = "data"):
        """Export all tables to CSV files for backup"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        tables = ['historical_prices', 'currency_adjusted_returns', 
                 'news_articles', 'recommendations_log', 'metadata']
        
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
            csv_path = output_path / f"{table}.csv"
            df.to_csv(csv_path, index=False)
            console.print(f"[green]✓[/green] Exported {table} to {csv_path}")
