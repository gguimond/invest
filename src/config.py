"""Configuration management for the investment advisor"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Database configuration
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "market_data.db"))

# Application settings
DEFAULT_RISK_TOLERANCE = os.getenv("DEFAULT_RISK_TOLERANCE", "moderate")
HISTORICAL_YEARS = int(os.getenv("HISTORICAL_YEARS", "20"))
NEWS_LOOKBACK_DAYS = int(os.getenv("NEWS_LOOKBACK_DAYS", "30"))
VERBOSE_OUTPUT = os.getenv("VERBOSE_OUTPUT", "False").lower() == "true"

# Market data tickers
TICKERS = {
    "SP500": {
        "ticker": "^GSPC",
        "name": "S&P 500",
        "currency": "USD",
        "region": "US",
        "adjust_for_eur": True,
        "needs_currency_adjustment": True
    },
    "CW8": {
        "ticker": "URTH",  # iShares MSCI World ETF (fallback: IWDA.AS)
        "name": "MSCI World (URTH)",
        "currency": "USD",
        "region": "Global",
        "adjust_for_eur": False,
        "needs_currency_adjustment": False
    },
    "STOXX600": {  # NEW: EuroStoxx 600
        "ticker": "^STOXX",  # Primary ticker (fallback: EXSA.DE for ETF)
        "name": "STOXX Europe 600",
        "currency": "EUR",
        "region": "Europe",
        "adjust_for_eur": False,
        "needs_currency_adjustment": False,
        "use_eurozone_m2": True,  # Will use Eurozone M2 in Phase 6B
        "use_eurozone_recession": True  # Will use Eurozone recession data in Phase 6B
    },
    "EURUSD": {
        "ticker": "EURUSD=X",
        "name": "EUR/USD"
    }
}

# Economic indicators (FRED data)
# Note: Requires FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html
ECONOMIC_INDICATORS = {
    "M2": {
        "fred_series": "M2SL",  # M2 Money Stock (seasonally adjusted)
        "name": "M2 Money Supply",
        "unit": "Billions of Dollars",
        "frequency": "monthly"
    },
    "M2_REAL": {
        "fred_series": "M2REAL",  # Real M2 Money Stock
        "name": "Real M2 Money Supply",
        "unit": "Billions of 1982 Dollars",
        "frequency": "monthly"
    }
}

# FRED API configuration
FRED_API_KEY = os.getenv("FRED_API_KEY", None)
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"

# Technical analysis parameters
TECHNICAL_PARAMS = {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "ma_short": 50,
    "ma_long": 200,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "lookback_window": 30  # For dip detection
}

# Decision engine thresholds
DECISION_PARAMS = {
    "dip_threshold_moderate": -3.0,
    "dip_threshold_significant": -5.0,
    "recession_high_threshold": 0.5,
    "recession_moderate_threshold": 0.3,
    "ai_bubble_high_threshold": 0.6,
    "ai_bubble_moderate_threshold": 0.4,
    "currency_risk_high": 2.5,
    "currency_risk_moderate": 1.5,
    # M2 Money Supply thresholds
    "m2_growth_positive": 2.0,      # >2% YoY growth is positive
    "m2_growth_strong": 5.0,        # >5% YoY growth is strong positive
    "m2_growth_negative": -2.0,     # <-2% YoY growth is negative
    "m2_lookback_months": 12        # Compare to 12 months ago
}

# Risk profiles
RISK_PROFILES = {
    "conservative": {
        "strong_buy_score": 60,
        "buy_score": 40,
        "hold_score": 20
    },
    "moderate": {
        "strong_buy_score": 50,
        "buy_score": 30,
        "hold_score": 10
    },
    "aggressive": {
        "strong_buy_score": 40,
        "buy_score": 20,
        "hold_score": 0
    }
}
