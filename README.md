# Investment Advisory CLI Application

A command-line investment advisory tool that analyzes S&P 500 and MSCI World index data, current market news, and historical trends to answer one simple question: **"Should I invest now?"**

## 🎯 Purpose

Strategic timing for index fund investments:
- Buy during dips to maximize gains
- Avoid catching a falling knife
- Consider EUR/USD currency impact for European investors
- Data-driven recommendations based on technical analysis and market sentiment

## 📋 Current Status

**Phase 1: Foundation & Database** ✅ **COMPLETE**
- ✅ Project structure setup
- ✅ SQLite database schema
- ✅ Data collector using yfinance
- ✅ 20 years historical data download
- ✅ Currency-adjusted returns calculator
- ✅ Data validation and storage

**Coming Next:**
- Phase 2: Technical Analysis (RSI, moving averages, MACD, etc.)
- Phase 3: News & Sentiment Analysis
- Phase 4: Decision Engine & Recommendations
- Phase 5: CLI Interface Enhancement

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
cd /home/qbnl4836/dev/invest
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### First Run - Initialize Database

Download 20 years of historical market data (~2-5 minutes):

```bash
python invest_advisor.py --init
```

This will:
- Create SQLite database
- Download S&P 500 historical data (^GSPC)
- Download MSCI World ETF data (URTH)
- Download EUR/USD exchange rates
- Calculate currency-adjusted returns
- Store everything in `./data/market_data.db`

### Regular Usage

```bash
# Get investment recommendations (once Phase 2+ complete)
python invest_advisor.py

# Show database statistics
python invest_advisor.py --stats

# Update with latest market data
python invest_advisor.py --force-update

# Export database to CSV
python invest_advisor.py --export-db
```

## 📊 What Data Is Collected

### Indices Tracked
- **S&P 500** (^GSPC) - US large-cap stocks
- **MSCI World** (URTH ETF) - Global developed markets
- **EUR/USD** (EURUSD=X) - Currency exchange rate

### Data Points
- Daily OHLCV (Open, High, Low, Close, Volume)
- Adjusted Close (accounts for dividends/splits)
- 20 years of historical data
- Currency-adjusted returns for S&P 500 (EUR perspective)

### Storage
- SQLite database: `./data/market_data.db`
- Typical size: ~20-50 MB
- No cloud storage - all data local

## 🛠️ Technical Stack

- **Python 3.10+**
- **yfinance** - Free market data from Yahoo Finance
- **pandas** - Data analysis
- **pandas-ta** - Technical indicators (Phase 2)
- **SQLite** - Local database
- **Rich** - Beautiful terminal output

## 📁 Project Structure

```
invest-advisor/
├── invest_advisor.py        # Main CLI entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env.example            # Environment template
├── .gitignore
├── data/
│   └── market_data.db      # SQLite database (gitignored)
├── reports/                # Saved reports (gitignored)
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration
│   ├── database.py         # Database operations
│   ├── data_collector.py   # Market data fetching
│   ├── analyzer.py         # Technical analysis (Phase 2)
│   ├── sentiment.py        # Sentiment analysis (Phase 3)
│   ├── advisor.py          # Decision engine (Phase 4)
│   └── display.py          # Output formatting (Phase 5)
└── tests/                  # Unit tests (Phase 6)
```

## 🔧 Configuration

Optional `.env` file for customization:

```bash
# Application Settings
DEFAULT_RISK_TOLERANCE=moderate
HISTORICAL_YEARS=20
NEWS_LOOKBACK_DAYS=30

# Database
DB_PATH=./data/market_data.db
```

## 📈 Planned Features

### Phase 2: Technical Analysis
- RSI (Relative Strength Index)
- Moving Averages (50-day, 200-day)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Dip detection algorithm

### Phase 3: News & Sentiment
- Google News RSS parsing
- VADER sentiment analysis
- Recession probability calculator
- AI bubble risk detection

### Phase 4: Decision Engine
- BUY/HOLD/AVOID recommendations
- Confidence scoring
- Currency impact assessment
- Risk profile handling

### Phase 5: CLI Enhancement
- Colored output formatting
- Report generation
- Historical performance tracking

## ⚠️ Disclaimer

**This application is for educational and informational purposes only.**

- NOT professional financial advice
- Past performance does not guarantee future results
- User assumes all investment risk
- Consult with licensed financial advisor for investment decisions

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a personal project. Feel free to fork and adapt for your own use.

## 📞 Support

For issues or questions, please check:
1. This README
2. The specification document: `INVESTMENT_ADVISOR_PLAN.md`
3. Code comments and docstrings

---

**Current Version**: 1.0.0 (Phase 1 Complete)  
**Last Updated**: January 5, 2026
