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
        "adjust_for_eur": True
    },
    "CW8": {
        "ticker": "URTH",  # iShares MSCI World ETF (fallback: IWDA.AS)
        "name": "MSCI World (URTH)",
        "currency": "USD",
        "adjust_for_eur": False
    },
    "EURUSD": {
        "ticker": "EURUSD=X",
        "name": "EUR/USD"
    }
}

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
    "currency_risk_moderate": 1.5
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
