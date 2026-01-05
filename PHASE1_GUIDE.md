# Phase 1 Installation Guide

## ✅ Phase 1: Foundation & Database - COMPLETE

This phase implements:
- Project structure
- SQLite database schema
- Market data collector using yfinance
- 20 years historical data download capability
- Currency-adjusted returns calculator
- Data validation and storage

## Installation Steps

### 1. Install Dependencies

```bash
cd /home/qbnl4836/dev/invest
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data analysis)
- yfinance (free market data)
- rich (beautiful terminal output)
- click (CLI framework)
- python-dotenv (configuration)
- and other dependencies

### 2. Test Installation

```bash
python test_phase1.py
```

This verifies:
- All packages installed correctly
- Project structure is correct
- Database can be created
- Modules can be imported

### 3. Initialize Database

**⚠️ First-time setup (takes 2-5 minutes):**

```bash
python invest_advisor.py --init
```

This will:
- Create SQLite database at `./data/market_data.db`
- Download 20 years of S&P 500 data (^GSPC)
- Download 20 years of MSCI World data (URTH ETF)
- Download 20 years of EUR/USD rates (EURUSD=X)
- Calculate currency-adjusted returns
- Store all data in the database

### 4. Verify Data

```bash
python invest_advisor.py --stats
```

Shows:
- Number of records per index
- Date range of data
- Database file size
- Number of news articles (0 for now)
- Number of recommendations (0 for now)

## Usage Examples

```bash
# Show database stats
python invest_advisor.py --stats

# Force update with latest data
python invest_advisor.py --force-update

# Export database to CSV files
python invest_advisor.py --export-db

# Reinitialize database (downloads everything again)
python invest_advisor.py --force-init
```

## What's Been Implemented

### ✅ Configuration (`src/config.py`)
- All application settings
- Ticker symbols for indices
- Technical analysis parameters
- Database path configuration

### ✅ Database (`src/database.py`)
- SQLite schema creation
- Historical prices storage
- Currency-adjusted returns storage
- News articles table (for Phase 3)
- Recommendations log table (for Phase 4)
- Metadata management
- Export to CSV functionality

### ✅ Data Collector (`src/data_collector.py`)
- Download historical data from Yahoo Finance
- Incremental updates (only fetch new data)
- Currency-adjusted returns calculator
- Data validation
- Error handling for missing/bad data

### ✅ Main CLI (`invest_advisor.py`)
- Command-line interface with Click
- Beautiful terminal output with Rich
- Database initialization
- Data updates
- Statistics display
- Database export

## Database Schema

### `historical_prices`
Stores daily OHLCV data for all indices:
- index_name (SP500, CW8, EURUSD)
- date, open, high, low, close, adj_close, volume

### `currency_adjusted_returns`
Stores S&P 500 returns in EUR terms:
- sp500_usd_price, sp500_eur_price
- eur_usd_rate
- Returns and currency impact

### `news_articles` (Phase 3)
Will store news with sentiment:
- title, description, source, url
- sentiment_score, sentiment_label
- published_at

### `recommendations_log` (Phase 4)
Will store investment recommendations:
- index_name, recommendation
- confidence, price
- reasoning, market_context

### `metadata`
System metadata:
- last_update_sp500, last_update_cw8, last_update_eurusd
- db_version, db_initialized

## Data Sources

All data from **Yahoo Finance (free, no API key needed)**:

| Index | Ticker | Description |
|-------|--------|-------------|
| S&P 500 | ^GSPC | US large-cap stocks (USD) |
| MSCI World | URTH | Global developed markets ETF (USD) |
| EUR/USD | EURUSD=X | Euro to US Dollar exchange rate |

## Troubleshooting

### Import errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or: . venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### Database errors
```bash
# Remove and reinitialize
rm data/market_data.db
python invest_advisor.py --init
```

### No data downloaded
- Check internet connection
- Yahoo Finance might be temporarily unavailable
- Try again in a few minutes

### Wrong ticker (CW8.PA not found)
The app uses URTH (iShares MSCI World ETF) as a fallback.
If you want to use a different ticker, edit `src/config.py`:

```python
TICKERS = {
    "CW8": {
        "ticker": "IWDA.AS",  # or another MSCI World ETF
        "name": "MSCI World",
        ...
    }
}
```

## Next Steps

Phase 1 is complete! Coming in future phases:

**Phase 2: Technical Analysis**
- RSI (Relative Strength Index)
- Moving Averages (50-day, 200-day)
- MACD
- Bollinger Bands
- Dip detection

**Phase 3: News & Sentiment**
- Google News RSS parsing
- VADER sentiment analysis
- Recession probability
- AI bubble detection

**Phase 4: Decision Engine**
- BUY/HOLD/AVOID recommendations
- Confidence scoring
- Currency risk assessment

**Phase 5: CLI Enhancement**
- Full report formatting
- Chart visualization
- Historical performance tracking

## Questions?

- Check the main README.md
- Review INVESTMENT_ADVISOR_PLAN.md for full specification
- Check inline code comments

---

**Phase 1 Status**: ✅ **COMPLETE**  
**Ready for**: Phase 2 - Technical Analysis
