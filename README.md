# Investment Advisory CLI Application

A command-line investment advisory tool that analyzes **S&P 500**, **MSCI World**, and **STOXX Europe 600** index data, current market news, and historical trends to answer one simple question: **"Should I invest now?"**

## 🎯 Purpose

Strategic timing for index fund investments across three major indices:
- Buy during dips to maximize gains
- Avoid catching a falling knife
- Compare US (S&P 500) vs Global (MSCI World) vs European (STOXX 600) markets
- EUR-denominated analysis for STOXX 600 (no currency risk for European investors)
- Consider EUR/USD currency impact for US investments
- Data-driven recommendations based on technical analysis and market sentiment

## 📋 Current Status

**Phase 1: Foundation & Database** ✅ **COMPLETE**
- ✅ SQLite database schema
- ✅ Data collector using yfinance
- ✅ 20 years historical data download
- ✅ Currency-adjusted returns calculator

**Phase 2: Technical Analysis** ✅ **COMPLETE**
- ✅ RSI, MACD, Moving Averages
- ✅ Trend detection & volatility analysis
- ✅ Dip detection algorithm

**Phase 3: News & Sentiment Analysis** ✅ **COMPLETE**
- ✅ Google News RSS parsing
- ✅ VADER sentiment analysis
- ✅ Recession probability calculator
- ✅ AI bubble risk detection

**Phase 4: Decision Engine** ✅ **COMPLETE**
- ✅ BUY/STRONG BUY/HOLD/AVOID recommendations
- ✅ Confidence scoring & risk factors
- ✅ M2 money supply analysis (US & Eurozone)

**Phase 5: CLI Enhancement & Reporting** ✅ **COMPLETE**
- ✅ Rich terminal output with colors
- ✅ Summary tables & reports
- ✅ Export to TXT/JSON/CSV

**Phase 6: STOXX Europe 600 Integration** ✅ **COMPLETE**
- ✅ **Phase 6A**: Basic STOXX 600 support
- ✅ **Phase 6B**: Eurozone M2 money supply
- ✅ **Phase 6C**: Diversification suggestions
- ✅ **Phase 6D**: Enhanced 3-index reporting

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

Download 20 years of historical market data (~3-7 minutes):

```bash
python invest_advisor.py --init
```

This will:
- Create SQLite database
- Download S&P 500 historical data (^GSPC)
- Download MSCI World ETF data (URTH)
- Download STOXX Europe 600 data (^STOXX)
- Download EUR/USD exchange rates
- Fetch US M2 money supply data (Federal Reserve)
- Fetch Eurozone M2 money supply data (ECB)
- Calculate currency-adjusted returns
- Store everything in `./data/market_data.db`

### Regular Usage

```bash
# Analyze all three indices with recommendations
python invest_advisor.py --index all

# Analyze specific index
python invest_advisor.py --index sp500
python invest_advisor.py --index cw8
python invest_advisor.py --index stoxx600

# Show executive summary tables
python invest_advisor.py --index all --summary

# Export comprehensive report (TXT/JSON/CSV)
python invest_advisor.py --index all --export-report all

# Update database with latest data
python invest_advisor.py --update

# Show database statistics
python invest_advisor.py --stats

# Force fresh data download
python invest_advisor.py --force-update
```

### Advanced Options

```bash
# Analyze with specific risk profile
python invest_advisor.py --risk conservative
python invest_advisor.py --risk moderate      # default
python invest_advisor.py --risk aggressive

# Update specific data
python invest_advisor.py --update --index stoxx600
python invest_advisor.py --update-m2           # Update M2 money supply
python invest_advisor.py --update-news         # Update news sentiment

# Verbose output
python invest_advisor.py --index all --verbose
```

## 📊 What Data Is Collected

### Indices Tracked
- **S&P 500** (^GSPC) - US large-cap stocks, USD-denominated
- **MSCI World** (URTH ETF) - Global developed markets, USD-denominated
- **STOXX Europe 600** (^STOXX) - European stocks, EUR-denominated ✨
- **EUR/USD** (EURUSD=X) - Currency exchange rate

### Data Points

**Market Data (per index):**
- Daily OHLCV (Open, High, Low, Close, Volume)
- Adjusted Close (accounts for dividends/splits)
- 20 years of historical data
- Technical indicators (RSI, MACD, Moving Averages)
- Currency-adjusted returns for S&P 500 (EUR perspective)

**News & Sentiment:**
- ~75 articles per analysis (25 per index)
- S&P 500 related news
- MSCI World / global market news
- STOXX 600 / European market news
- VADER sentiment scores
- Recession probability indicators
- AI bubble risk assessment

**Economic Data (FRED API):**
- US M2 Money Supply (for S&P 500 & MSCI World)
- Eurozone M3 Money Supply (for STOXX 600)
- Year-over-year growth rates
- Monthly updates

### Storage
- SQLite database: `./data/market_data.db`
- Typical size: ~50-100 MB
- No cloud storage - all data local
- Reports exported to: `./reports/`

## 🛠️ Technical Stack

- **Python 3.10+**
- **yfinance** - Free market data from Yahoo Finance
- **pandas** - Data analysis and manipulation
- **pandas-ta** - Technical indicators (RSI, MACD, etc.)
- **vaderSentiment** - News sentiment analysis
- **feedparser** - Google News RSS parsing
- **requests** - FRED API for economic data
- **SQLite** - Local database
- **Rich** - Beautiful terminal output with tables
- **click** - CLI framework

## 📁 Project Structure

```
invest/
├── invest_advisor.py           # Main CLI entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env.example                # Environment template
├── .gitignore
├── data/
│   └── market_data.db         # SQLite database (gitignored)
├── reports/                    # Saved reports (gitignored)
│   ├── *.txt                  # Text reports
│   ├── *.json                 # JSON reports
│   └── *.csv                  # CSV reports
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration & settings
│   ├── database.py            # Database operations
│   ├── data_collector.py      # Market data fetching (yfinance)
│   ├── economic_data.py       # M2 money supply (FRED API)
│   ├── technical_analyzer.py  # Technical indicators
│   ├── news_collector.py      # Google News RSS fetching
│   ├── sentiment_analyzer.py  # VADER sentiment analysis
│   ├── decision_engine.py     # Investment recommendations
│   └── report_generator.py    # Rich tables & exports
└── docs/
    ├── PHASE*.md              # Implementation guides
    └── EUROSTOXX_INTEGRATION_PLAN.md
```

## 🔧 Configuration

Create a `.env` file for customization (optional):

```bash
# Application Settings
DEFAULT_RISK_TOLERANCE=moderate    # conservative, moderate, aggressive
HISTORICAL_YEARS=20                # Years of data to download
NEWS_LOOKBACK_DAYS=30              # Days to analyze news

# Database
DB_PATH=./data/market_data.db

# API Keys (optional but recommended)
FRED_API_KEY=your_fred_api_key_here  # Get from https://fred.stlouisfed.org/

# Output
VERBOSE_OUTPUT=False
```

### Getting a FRED API Key

The Federal Reserve Economic Data (FRED) API provides M2 money supply data:

1. Visit https://fred.stlouisfed.org/
2. Create free account
3. Request API key: https://fred.stlouisfed.org/docs/api/api_key.html
4. Add to `.env` file

**Note:** The app works without FRED API key but M2 analysis will be limited.

## ✨ Key Features

### Multi-Index Analysis
- **3-way comparison**: S&P 500 vs MSCI World vs STOXX 600
- **Currency awareness**: EUR/USD impact for US indices
- **EUR-based investing**: STOXX 600 has zero currency risk for Europeans
- **Best index highlighting**: ⭐ marks the recommended index

### Technical Analysis
- **Dip Detection**: Identify buying opportunities (3%, 5%, 10% thresholds)
- **RSI Analysis**: Overbought (>70) / Oversold (<30) detection
- **Trend Analysis**: Moving averages (50-day, 200-day), golden/death cross
- **MACD Momentum**: Bullish/bearish crossovers
- **Volatility**: Recent volatility vs historical averages

### Sentiment Analysis
- **News Coverage**: ~75 articles analyzed per run
- **VADER Sentiment**: Positive/neutral/negative scoring
- **Market Tone**: Overall bullish/bearish ratio
- **Recession Probability**: Economic indicator tracking
- **AI Bubble Risk**: Tech sector overvaluation detection

### Economic Indicators
- **US M2 Money Supply**: Federal Reserve data for S&P 500 & MSCI World
- **Eurozone M3**: ECB data for STOXX 600
- **YoY Growth Rates**: Monetary expansion/contraction analysis
- **Liquidity Impact**: How money supply affects market recommendations

### Decision Engine
- **Smart Recommendations**: STRONG BUY / BUY / HOLD / AVOID
- **Confidence Scores**: 0-100% recommendation confidence
- **Risk Factors**: Clear enumeration of concerns
- **Positive Factors**: Reasons supporting the recommendation
- **Diversification**: Conservative/Moderate/Aggressive portfolio allocations

### Reporting
- **Executive Summary**: Beautiful terminal tables with color coding
- **3-Index Comparison**: Side-by-side metrics
- **Risk Assessment**: Recession, bubble, sentiment analysis
- **Export Formats**: TXT, JSON, CSV for further analysis
- **Historical Tracking**: All analyses stored in database

## 🎨 Sample Output

```
📊 MARKET SUMMARY
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Metric              ┃ S&P 500         ┃ MSCI World      ┃ STOXX 600       ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Current Price       │ $5,842.91       │ €125.32         │ €487.45         │
│ Dip from High       │ -2.3%           │ -1.8%           │ -3.5%           │
│ RSI (14)            │ 58.3            │ 61.2            │ 52.1            │
│ Trend               │ Upward          │ Upward          │ Sideways        │
│ Sentiment           │ +0.145          │ +0.089          │ +0.112          │
│ 💱 EUR/USD Rate     │ 1.0421          │ N/A (EUR-based) │ N/A (EUR-based) │
│ Currency Impact     │ Moderate (2.1%) │ No impact       │ ✅ None (EUR)   │
│ 💵 M2 Growth (YoY)  │ +3.2% (US)      │ +3.2% (US)      │ +4.1% (EUR)     │
│ M2 Impact           │ Favorable       │ Favorable       │ Strong Positive │
└─────────────────────┴─────────────────┴─────────────────┴─────────────────┘

🎯 INVESTMENT RECOMMENDATIONS
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Index         ┃ Recommendation┃ Confidence ┃ Score    ┃ Key Factors   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 📈 S&P 500    │ 💰 BUY        │ 72%        │ +35      │ Good dip...   │
│ 🌍 MSCI World │ 💰 BUY        │ 68%        │ +28      │ Positive...   │
│ 🇪🇺 STOXX 600⭐│ 💎 STRONG BUY │ 85%        │ +48      │ Great dip...  │
│ 📊 OVERALL    │ INVEST NOW    │            │          │ Best: STOXX600│
└───────────────┴───────────────┴────────────┴──────────┴───────────────┘
```

## 🇪🇺 STOXX Europe 600 Features

### Why STOXX 600?
- **EUR-denominated**: No currency conversion risk for European investors
- **European focus**: 600 largest companies across 17 European countries
- **Diversification**: Different from US-heavy S&P 500 and MSCI World
- **+5 Score Bonus**: Decision engine favors EUR-based assets for EUR investors

### What's Included
- ✅ Full technical analysis (same as S&P 500 & MSCI World)
- ✅ European news sentiment (25 articles per analysis)
- ✅ Eurozone M3 money supply tracking
- ✅ 3-way comparison with other indices
- ✅ Diversification portfolio suggestions
- ✅ Export to all report formats

### Ticker Information
- **Primary**: ^STOXX (STOXX Europe 600 Price Index)
- **Fallback**: EXSA.DE (ETF alternative if primary unavailable)
- **Currency**: EUR
- **Region**: Europe
- **Coverage**: 17 European countries

## 🎓 Understanding the Recommendations

### Recommendation Levels
- **💎 STRONG BUY**: High confidence opportunity (score 50+)
- **💰 BUY**: Good opportunity, moderate risk (score 30-49)
- **⏸️ HOLD**: Wait for better timing (score 10-29)
- **⚠️ AVOID**: High risk, poor timing (score <10)

### Score Components
Each index gets a score based on:
- **Dip Analysis**: +10 for 5%+ dip, +5 for 3-5% dip
- **RSI**: +10 if oversold (<30), -10 if overbought (>70)
- **Trend**: +15 for upward trend, -10 for downward
- **Sentiment**: +10 for positive news, -10 for negative
- **M2 Growth**: +10 for strong growth (>5%), -10 for contraction (<-2%)
- **Currency Bonus**: +5 for STOXX 600 (EUR-based, no FX risk)
- **Risk Penalties**: -15 for high recession risk, -10 for AI bubble

### Diversification Suggestions
The tool provides three portfolio allocation strategies:

**Conservative** (Lower risk, balanced)
- Example: 40% S&P 500, 30% MSCI World, 30% STOXX 600

**Moderate** (Balanced risk/reward)
- Example: 50% STOXX 600, 30% S&P 500, 20% MSCI World

**Aggressive** (Higher concentration in best performer)
- Example: 70% STOXX 600, 20% S&P 500, 10% MSCI World

## ⚠️ Disclaimer

**This application is for educational and informational purposes only.**

- NOT professional financial advice
- Past performance does not guarantee future results
- User assumes all investment risk
- Consult with licensed financial advisor for investment decisions
- Market data from free sources may have delays
- News sentiment is automated and may not reflect market reality

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a personal project. Feel free to fork and adapt for your own use.

## 📞 Support

For issues or questions, please check:
1. This README
2. Implementation guides: `PHASE*.md` files
3. Integration plan: `EUROSTOXX_INTEGRATION_PLAN.md`
4. Code comments and docstrings

## 🗺️ Roadmap

**Completed (v2.0.0):**
- ✅ All 5 original phases
- ✅ STOXX Europe 600 integration (Phases 6A-6D)
- ✅ Dual M2 tracking (US + Eurozone)
- ✅ 3-way index comparison
- ✅ Portfolio diversification suggestions

**Future Enhancements (Optional):**
- 📊 Phase 6E: Comprehensive testing suite
- 📈 Historical backtest performance tracking
- 🌍 Additional indices (Nikkei, FTSE, etc.)
- 📱 Web interface or mobile app
- 🔔 Price alerts and notifications
- 📊 Interactive charts and visualizations

---

**Current Version**: 2.0.0 (Phases 1-6D Complete)  
**Last Updated**: January 6, 2026  
**Indices Supported**: S&P 500, MSCI World, STOXX Europe 600
