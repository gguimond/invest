# Investment Advisory CLI Application - Specification Document

## 1. Project Overview

### 1.1 Purpose
A command-line investment advisory tool that analyzes S&P 500 and CW8 (MSCI World) index data, current market news, and historical trends to answer one simple question: **"Should I invest now?"**

The tool provides buy/hold recommendations with the goal of maximizing returns by buying during dips while avoiding catching a falling knife.

### 1.2 Core Objective
**Strategic Timing**: Buy when indices are down to maximize gains, but avoid investing if:
- Further decline is anticipated in the coming weeks
- Economic recession indicators are present
- AI bubble burst signals are detected
- Market sentiment suggests continued bearish trends

### 1.3 Target User
Individual investor seeking data-driven timing advice for index fund investments with a focus on strategic dip-buying.

### 1.4 Core Usage
```bash
# Simple command
$ python invest_advisor.py

# Output:
# 📊 Investment Advisory Report - January 5, 2026
# 
# 🔄 Updating data...
# ✓ S&P 500 data updated (last: 2026-01-04)
# ✓ CW8 data updated (last: 2026-01-04)
# ✓ News sentiment analyzed (25 articles)
# 
# 📈 S&P 500: HOLD/WAIT ⏸️
#    Current: $4,850.50 (-3.2% from high)
#    Confidence: 45%
#    Reason: Moderate dip but sentiment deteriorating
# 
# 🌍 CW8: BUY 🟢
#    Current: €485.20 (-5.8% from high)
#    Confidence: 72%
#    Reason: Oversold conditions + improving sentiment
# 
# 💡 Recommendation: Consider investing in CW8
```

---

## 2. Functional Requirements

### 2.1 Data Collection & Storage

#### 2.1.1 Historical Data Retrieval
- **Indices to Track**:
  - S&P 500 (^GSPC or SPY ETF)
  - CW8 / MSCI World (CW8.PA or similar ticker)
  
- **Exchange Rate to Track**:
  - **EUR/USD (EURUSD=X)** - Critical for EUR-based investors
  - Accounts for currency impact on USD-denominated assets (S&P 500)
  - Tracks dollar strength/weakness trends
  
- **Data Points Required**:
  - Date/Timestamp
  - Open, High, Low, Close prices
  - Volume
  - Adjusted Close (for dividends/splits)

- **Historical Range**: 
  - **20 years of daily data**
  - Enables comprehensive trend analysis and pattern recognition across multiple market cycles

- **Storage**:
  - **SQLite database** (single file, no server needed)
  - Simple schema with time-series data
  - File location: `./data/market_data.db`

#### 2.1.2 News & Sentiment Data Collection
- **News Sources** (Free):
  - Google News RSS feeds
  - Yahoo Finance news
  - Reddit sentiment (optional - via PRAW)
  - Financial news RSS aggregators
  
- **Keywords to Monitor**:
  - Market indices (S&P 500, MSCI World)
  - Economic indicators (GDP, inflation, unemployment, recession)
  - AI sector news (for bubble detection)
  - Fed policy, interest rates
  
- **Sentiment Analysis**:
  - Use TextBlob or VADER (free, lightweight)
  - Classify news as positive/negative/neutral
  - Extract key themes (recession fears, AI bubble, market optimism)
  - Track sentiment trends over time

#### 2.1.3 Data Update Workflow
- **On Each Run**:
  1. Check last update timestamp
  2. Fetch only new data since last run (incremental)
  3. Update database with latest prices
  4. Fetch recent news (last 30 days)
  5. Perform analysis
  6. Display recommendation
  
- **Initial Setup** (First Run):
  - Download 20 years of historical data
  - Create SQLite database
  - Build initial indicators cache
  - May take 2-5 minutes

- **Data Validation**:
  - Handle market holidays (no data on weekends)
  - Detect and handle data anomalies
  - Graceful error handling if API fails

### 2.2 Analysis Engine

#### 2.2.1 Technical Analysis Indicators

**For Indices (S&P 500, CW8):**
- **Trend Analysis**:
  - Moving Averages (50-day, 200-day SMA/EMA)
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - Bollinger Bands
  
- **Volatility Metrics**:
  - VIX correlation (if available)
  - Standard deviation of returns
  - Average True Range (ATR)

- **Momentum Indicators**:
  - Rate of Change (ROC)
  - Stochastic Oscillator

**For EUR/USD Exchange Rate:**
- **Trend Analysis**:
  - 50-day and 200-day Moving Averages
  - Dollar strength/weakness trends
  - Support and resistance levels
  
- **Technical Indicators**:
  - RSI (overbought/oversold dollar)
  - MACD for trend reversals
  - Rate of change (currency momentum)
  
- **Currency Impact Analysis**:
  - Calculate S&P 500 returns in EUR terms
  - Identify when dollar weakness erodes EUR-based gains
  - Track correlation between dollar moves and index performance

#### 2.2.2 Fundamental Analysis
- **Economic Indicators**:
  - **M2 Money Supply** - Monetary expansion/contraction (KEY INDICATOR)
    - Year-over-year growth rate
    - M2 increasing = favorable for asset prices (more liquidity)
    - M2 decreasing = headwind for investments (liquidity contraction)
  - Yield curve (2Y vs 10Y treasuries - recession indicator)
  - Unemployment rate trends
  - Inflation data (CPI)
  - GDP growth rates
  
- **Market-Specific Metrics**:
  - P/E ratio of S&P 500
  - Sector performance (especially tech for AI bubble detection)
  - Market breadth indicators

#### 2.2.3 Sentiment Analysis

**Market Sentiment:**
- **News Sentiment Score**:
  - Aggregate sentiment from recent news (last 7-30 days)
  - Weight recent news more heavily
  - Identify emerging themes
  
- **AI Bubble Detection**:
  - Monitor AI/tech sector valuations
  - Track mentions of "overvaluation", "bubble", "correction"
  - Compare current valuations to historical peaks

- **Recession Probability**:
  - Analyze recession-related keywords frequency
  - Track economic indicator deterioration
  - Monitor central bank hawkish/dovish sentiment

**Currency Sentiment (EUR/USD):**
- **Dollar Strength/Weakness Sentiment**:
  - Track news about Fed policy, interest rates
  - Monitor ECB (European Central Bank) policy changes
  - Identify dollar bullish/bearish sentiment
  - Keywords: "dollar strengthening", "dollar weakness", "euro parity", "Fed rate hikes"
  
- **Currency Risk Assessment**:
  - Evaluate if dollar decline is likely to continue
  - Monitor geopolitical events affecting USD/EUR
  - Track interest rate differentials (US vs Eurozone)
  - Assess impact on EUR-based investment returns

#### 2.2.4 Decision Logic

**Investment Recommendation Categories**:
1. **STRONG BUY**: High confidence dip opportunity
2. **BUY**: Favorable entry point
3. **HOLD/WAIT**: Uncertain conditions, wait for clarity
4. **AVOID**: High risk of further decline

**Decision Factors**:
```
IF index is down X% from recent high:
  CHECK sentiment analysis
  CHECK technical indicators (oversold?)
  CHECK recession probability
  CHECK AI bubble risk
  CHECK M2 money supply growth (liquidity environment)
  CHECK currency impact (for S&P 500 in EUR terms)
  
  IF (sentiment improving OR bottoming out) AND
     (technical indicators show oversold) AND
     (low recession risk) AND
     (low AI bubble risk) AND
     (M2 growing OR stable - liquidity supportive) AND
     (dollar stable OR strengthening for S&P 500):
       → RECOMMEND: BUY
       
  ELSE IF (sentiment deteriorating) AND
          (technical indicators show continued weakness) AND
          (high recession risk OR AI bubble concerns) OR
          (M2 contracting - liquidity headwind) OR
          (dollar weakening significantly - reducing EUR returns):
       → RECOMMEND: AVOID / WAIT
       
  ELSE:
       → RECOMMEND: HOLD / WAIT for more data
```

**Currency-Adjusted Logic (for S&P 500):**
```
Real EUR Return = Index Return (%) + Currency Return (%)

Examples:
- S&P 500 up 5% + USD up 2% vs EUR = +7% gain in EUR
- S&P 500 up 5% + USD down 3% vs EUR = +2% gain in EUR (currency drag!)
- S&P 500 down 2% + USD down 3% vs EUR = -5% loss in EUR (amplified loss!)

Decision adjustments:
- If dollar is weakening > 2% recently → Reduce BUY confidence for S&P 500
- If dollar is strengthening → Increase attractiveness of S&P 500 for EUR investors
- Strong dollar weakness → May prefer CW8 (EUR-denominated) over S&P 500
```

**Risk Levels**:
- Conservative: Only buy on strong signals with low risk
- Moderate: Accept some uncertainty
- Aggressive: Buy dips more readily

### 2.3 CLI Interface Design

#### 2.3.1 Main Command
```bash
# Primary usage - simple and direct
$ python invest_advisor.py

# With options
$ python invest_advisor.py --risk moderate
$ python invest_advisor.py --index sp500
$ python invest_advisor.py --verbose
$ python invest_advisor.py --force-update  # Force full data refresh
```

#### 2.3.2 Optional Commands
```bash
# Initialize database (first-time setup)
$ python invest_advisor.py --init

# Show historical data
$ python invest_advisor.py --history 30  # Last 30 days

# Show current indicators
$ python invest_advisor.py --indicators

# Export recommendation log
$ python invest_advisor.py --export-log recommendations.csv
```

#### 2.3.3 Output Format
```
📊 Investment Advisory Report - January 5, 2026
═══════════════════════════════════════════════

🔄 Updating market data...
✓ S&P 500: Updated to 2026-01-04 (1 new day)
✓ CW8: Updated to 2026-01-04 (1 new day)
✓ EUR/USD: Updated to 2026-01-04 (1 new day)
✓ News: 18 articles analyzed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

� EUR/USD Exchange Rate Analysis
───────────────────────────────────────────────
Current Rate:     1.0850 (€1 = $1.0850)
30-day change:    -2.8% (Dollar weakening)
RSI (14):         58.2 (Neutral)
50-day MA:        1.0920
Trend:            ⚠️  Dollar weakness continues

Currency Impact:
  ⚠ Dollar down 2.8% in last 30 days
  ⚠ Reduces EUR returns on USD investments
  ✓ Dollar approaching support level (1.08)
  
Sentiment: Bearish on USD (Fed rate cut expectations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

�📈 S&P 500 Analysis
───────────────────────────────────────────────
Current Price (USD): $4,850.50
Current Price (EUR): €4,470.05
Change from High:    -3.2% (30-day high: $5,010.20)
EUR-adjusted Return: -5.9% (includes -2.8% currency drag)
RSI (14):            45.2 (Neutral)
50-day MA:           $4,920.15
200-day MA:          $4,650.80

Recommendation:   ⏸️  HOLD/WAIT
Confidence:       40%

Reasons:
  ✓ Moderate dip detected (-3.2% in USD)
  ⚠ Sentiment deteriorating (score: -0.15)
  ⚠ RSI neutral, no oversold signal
  ⚠ Moderate recession concerns (probability: 35%)

Risk Factors:
  • Negative market sentiment in recent news
  • Economic uncertainty elevated
  ⚠️ CURRENCY DRAG: Dollar weakness (-2.8%) eroding EUR returns
  • Real EUR loss: -5.9% (worse than USD performance)
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 CW8 (MSCI World) Analysis
───────────────────────────────────────────────
Current Price:    €485.20
Change from High: -5.8% (30-day high: €515.40)
RSI (14):         32.5 (Oversold)
50-day MA:        €492.30
200-day MA:       €465.10
Currency Impact:  ✓ No currency risk (EUR-denominated)

Recommendation:   🟢 BUY
Confidence:       75%

Reasons:
  ✓ Significant dip detected (-5.8%)
  ✓ Oversold conditions (RSI: 32.5)
  ✓ Sentiment improving (score: +0.25)
  ✓ Low recession risk (probability: 18%)
  ✓ Price below 50-day MA (support level)
  ✓ No currency headwind (EUR-based)

Risk Factors:
  • Moderate AI bubble concerns (40%)
  • Volatility slightly elevated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 OVERALL RECOMMENDATION
═══════════════════════════════════════════════

🟢 STRONG PREFERENCE: Invest in CW8 (MSCI World)
  
The CW8 index shows a favorable entry point with 
oversold conditions and improving sentiment. 

⚠️  AVOID S&P 500 for now: Dollar weakness is creating
   significant currency drag for EUR-based investors.
   Your actual EUR return is -5.9% vs -3.2% in USD terms.
   
   Consider S&P 500 only when:
   • Dollar stabilizes or strengthens, OR
   • S&P 500 dips significantly more (>7%)

💱 Currency Outlook: Dollar may stabilize around 1.08 support.
   Monitor Fed policy announcements.

⚠️  DISCLAIMER: This is not financial advice. 
    Past performance does not guarantee future results.
    Invest at your own risk.

═══════════════════════════════════════════════
Report saved to: ./reports/2026-01-05_report.txt
```

---

## 3. Technical Architecture

### 3.1 Technology Stack

#### Backend
- **Language**: Python 3.11+
- **CLI Framework**: Click or argparse (for command-line interface)
- **Data Analysis**: pandas, numpy
- **Technical Analysis**: pandas-ta (pure Python, no C dependencies)
- **Sentiment Analysis**: 
  - VADER (vaderSentiment) - optimized for social media/news
  - or TextBlob - simple and effective
- **HTTP Client**: requests (for fetching data)

#### Database
- **SQLite** (single file database, zero configuration)
- **Location**: `./data/market_data.db`
- **Backup**: Optional export to CSV for portability

#### Data Sources (All FREE)
- **Market Data**: 
  - **yfinance** (Yahoo Finance - free, unlimited for personal use)
  - 20 years of historical data available
  - Daily updates
  - Supports: indices, ETFs, and forex pairs (EUR/USD)
  
- **News Sources**: 
  - **Google News RSS** (free, no API key needed)
  - **Yahoo Finance RSS** (free)
  - **BeautifulSoup4** for web scraping if needed
  - Alternative: **newsapi** (100 requests/day free tier)
  - **Currency-specific news**: Fed policy, ECB announcements
  
- **Economic Data** (Optional): 
  - **FRED API** (Federal Reserve - free with API key)
  - Yield curve, unemployment, GDP data
  - Interest rate differentials (US vs Eurozone)

#### Deployment
- **Local**: Simple Python script
- **Distribution**: Single executable with PyInstaller (optional)
- **Requirements**: Python 3.11+ with pip

### 3.2 Project Structure
```
invest-advisor/
├── invest_advisor.py        # Main CLI entry point
├── requirements.txt         # Python dependencies
├── README.md               # Setup and usage guide
├── .env.example            # Template for configuration
├── .gitignore
├── data/
│   ├── market_data.db      # SQLite database (gitignored)
│   └── .gitkeep
├── reports/                # Saved reports (gitignored)
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── data_collector.py   # Fetch market data (yfinance)
│   ├── news_collector.py   # Fetch news & sentiment
│   ├── analyzer.py         # Technical analysis
│   ├── sentiment.py        # Sentiment analysis
│   ├── advisor.py          # Decision engine
│   ├── database.py         # SQLite operations
│   ├── display.py          # CLI output formatting
│   └── config.py           # Configuration management
├── tests/
│   ├── test_analyzer.py
│   ├── test_advisor.py
│   └── test_data_collector.py
└── docs/
    └── strategy_explanation.md
```

### 3.3 Database Schema (SQLite)

```sql
-- Historical Prices
CREATE TABLE historical_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_name TEXT NOT NULL,  -- 'SP500', 'CW8', or 'EURUSD'
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    adj_close REAL,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_name, date)
);

-- Currency-Adjusted Returns Cache (for S&P 500 in EUR)
CREATE TABLE currency_adjusted_returns (
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
);

-- News Articles
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    source TEXT,
    published_at TIMESTAMP,
    url TEXT,
    sentiment_score REAL,  -- -1 to 1
    sentiment_label TEXT,   -- positive/negative/neutral
    related_index TEXT,     -- SP500, CW8, EURUSD, GENERAL
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations Log
CREATE TABLE recommendations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    index_name TEXT,
    recommendation TEXT,  -- BUY, HOLD, AVOID, STRONG_BUY
    confidence REAL,
    price_at_recommendation REAL,
    eur_usd_rate REAL,     -- Currency rate at recommendation
    currency_impact TEXT,  -- Currency impact assessment
    reasoning TEXT,        -- JSON string
    market_context TEXT    -- JSON string
);

-- System Metadata
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Stores: last_update_sp500, last_update_cw8, last_update_eurusd, db_version, etc.
```

### 3.4 Data Flow

```
1. First Run (Initialization):
   User → CLI: python invest_advisor.py
   CLI → Check if database exists
   CLI → Download 20 years historical data (yfinance)
   CLI → Create SQLite database
   CLI → Store historical data
   CLI → Display "Setup complete"
   
2. Regular Run:
   User → CLI: python invest_advisor.py
   CLI → Load database
   CLI → Check last update (from metadata table)
   CLI → Fetch new prices since last update (yfinance)
   CLI → Update database with new data
   CLI → Fetch recent news (RSS/Google News)
   CLI → Analyze sentiment (VADER)
   CLI → Calculate technical indicators (pandas-ta)
   CLI → Run decision engine
   CLI → Format and display results
   CLI → Log recommendation to database
   CLI → Save report to file (optional)
```

---

## 4. Implementation Phases

### Phase 1: Foundation & Database (Week 1)
- [x] Setup project structure
- [x] Create SQLite database schema
- [x] Implement data collector using yfinance
- [x] Download 20 years of historical data for SP500, CW8 & EUR/USD
- [x] Implement currency-adjusted returns calculator
- [x] Test data storage and retrieval
- [x] Implement database backup/export
- [x] Integrate M2 Money Supply data (FRED API)

### Phase 2: Technical Analysis (Week 1-2)
- [x] Install ta library (technical analysis)
- [x] Implement technical indicators for indices:
  - [x] RSI (Relative Strength Index)
  - [x] Moving Averages (50-day, 200-day SMA/EMA)
  - [x] MACD
  - [x] Bollinger Bands
  - [x] Stochastic Oscillator
  - [x] ATR (Average True Range)
- [x] Implement technical indicators for EUR/USD
- [x] Create currency impact calculator
- [x] Calculate S&P 500 returns in EUR terms
- [x] Implement dip detection algorithm
- [x] Implement trend analysis (Golden Cross, price vs MAs)
- [x] Implement momentum analysis (RSI, MACD, Stochastic)
- [x] Implement volatility analysis (Bollinger Bands, ATR)
- [x] Support/resistance level detection
- [x] Currency risk assessment
- [x] Integrate M2 Money Supply into analysis display
- [x] Test on historical data
- [x] Optimize for performance

### Phase 3: News & Sentiment (Week 2)
- [ ] Implement Google News RSS parser
- [ ] Implement Yahoo Finance RSS parser
- [ ] Add currency-specific news collection (Fed, ECB)
- [ ] Install VADER sentiment analyzer
- [ ] Create sentiment aggregation logic
- [ ] Implement dollar strength/weakness sentiment analysis
- [ ] Test sentiment analysis accuracy
- [ ] Store news with sentiment scores

### Phase 4: Decision Engine (Week 3)
- [ ] Implement dip detection algorithm
- [ ] Create recession probability calculator
- [ ] Implement AI bubble risk detector
- [ ] Implement currency risk assessment
- [ ] Build main recommendation logic with currency adjustments
- [ ] Implement confidence scoring (adjusted for currency risk)
- [ ] Create risk profile handling

### Phase 5: CLI Interface (Week 3-4)
- [ ] Design CLI output format
- [ ] Implement colored terminal output (rich library)
- [ ] Create report formatter
- [ ] Add command-line arguments parsing
- [ ] Implement progress indicators
- [ ] Create report export functionality

### Phase 6: Testing & Polish (Week 4)
- [ ] Unit tests for all components
- [ ] Integration testing
- [ ] Manual testing with real data
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Documentation (README, docstrings)

### Phase 7: Optional Enhancements
- [ ] Export to CSV/Excel
- [ ] Historical performance tracking
- [ ] Simple backtesting
- [ ] Email notifications (optional)
- [ ] PyInstaller executable build

---

## 5. Key Algorithms & Logic

### 5.1 Dip Detection Algorithm
```python
def detect_dip(prices, window=30):
    """
    Detect if current price is in a dip
    
    Returns:
        - dip_percentage: % from recent high
        - is_significant_dip: bool (> 3% down)
        - recent_high: price level
    """
    recent_high = prices[-window:].max()
    current_price = prices[-1]
    dip_percentage = ((current_price - recent_high) / recent_high) * 100
    
    return {
        'dip_percentage': dip_percentage,
        'is_significant_dip': dip_percentage < -3,
        'recent_high': recent_high
    }
```

### 5.2 Currency-Adjusted Returns Calculator
```python
def calculate_eur_adjusted_returns(sp500_prices, eur_usd_rates):
    """
    Calculate S&P 500 returns in EUR terms for EUR-based investors
    
    Args:
        sp500_prices: DataFrame with S&P 500 USD prices
        eur_usd_rates: DataFrame with EUR/USD exchange rates
    
    Returns:
        DataFrame with currency-adjusted returns and impact
    """
    # Convert S&P 500 USD prices to EUR
    sp500_eur = sp500_prices / eur_usd_rates
    
    # Calculate returns
    sp500_usd_return = sp500_prices.pct_change() * 100
    sp500_eur_return = sp500_eur.pct_change() * 100
    currency_return = eur_usd_rates.pct_change() * 100
    
    # Currency impact = difference between EUR and USD returns
    currency_impact = sp500_eur_return - sp500_usd_return
    
    return {
        'sp500_eur_price': sp500_eur,
        'sp500_usd_return': sp500_usd_return,
        'sp500_eur_return': sp500_eur_return,
        'currency_return': currency_return,
        'currency_impact': currency_impact
    }

def assess_currency_risk(eur_usd_rates, window=30):
    """
    Assess dollar strength/weakness trend
    
    Returns:
        - trend: 'strengthening', 'weakening', 'stable'
        - impact: percentage impact over window
        - risk_level: 'low', 'moderate', 'high'
    """
    recent_change = ((eur_usd_rates[-1] - eur_usd_rates[-window]) / 
                     eur_usd_rates[-window]) * 100
    
    if recent_change < -2:  # Dollar strengthening
        trend = 'strengthening'
        risk_level = 'low'  # Good for EUR investors in USD assets
    elif recent_change > 2:  # Dollar weakening
        trend = 'weakening'
        if recent_change > 5:
            risk_level = 'high'  # Significant drag on returns
        else:
            risk_level = 'moderate'
    else:
        trend = 'stable'
        risk_level = 'low'
    
    return {
        'trend': trend,
        'change_pct': recent_change,
        'risk_level': risk_level
    }
```

### 5.3 Sentiment Aggregation
```python
def aggregate_sentiment(news_articles, decay_factor=0.9):
    """
    Calculate weighted sentiment (recent news weighted more)
    
    Args:
        news_articles: List of articles with timestamps and sentiment
        decay_factor: Weight decay for older news
    """
    sorted_news = sorted(news_articles, key=lambda x: x.published_at)
    weighted_sum = 0
    total_weight = 0
    
    for i, article in enumerate(sorted_news):
        age_days = (now - article.published_at).days
        weight = decay_factor ** age_days
        weighted_sum += article.sentiment_score * weight
        total_weight += weight
    
    return weighted_sum / total_weight if total_weight > 0 else 0
```

### 5.4 Recession Probability
```python
def calculate_recession_probability(
    yield_curve_inversion,
    unemployment_trend,
    gdp_growth,
    sentiment
):
    """
    Estimate recession probability based on indicators
    
    Factors:
        - Yield curve inversion (strong indicator)
        - Rising unemployment
        - Negative GDP growth
        - Negative sentiment
    """
    score = 0
    
    # Yield curve (0-40 points)
    if yield_curve_inversion:
        score += 40
    
    # Unemployment trend (0-25 points)
    if unemployment_trend > 0.5:  # Increasing significantly
        score += 25
    elif unemployment_trend > 0.2:
        score += 15
    
    # GDP growth (0-25 points)
    if gdp_growth < 0:
        score += 25
    elif gdp_growth < 1:
        score += 15
    
    # Sentiment (0-10 points)
    if sentiment < -0.5:
        score += 10
    
    return score / 100  # Return as probability 0-1
```

### 5.5 Buy Recommendation Logic (with Currency Adjustment)
```python
def generate_recommendation(
    dip_percentage,
    rsi,
    sentiment,
    recession_prob,
    ai_bubble_risk,
    risk_tolerance,
    index_name='SP500',
    currency_risk=None  # For S&P 500 only
):
    """
    Main decision engine with currency adjustment
    """
    score = 0
    reasons = []
    risk_factors = []
    
    # Dip opportunity (positive factor)
    if dip_percentage < -5:
        score += 30
        reasons.append(f"Significant dip: {dip_percentage:.1f}%")
    elif dip_percentage < -3:
        score += 15
        reasons.append(f"Moderate dip: {dip_percentage:.1f}%")
    
    # RSI oversold (positive factor)
    if rsi < 30:
        score += 25
        reasons.append(f"Oversold conditions (RSI: {rsi})")
    elif rsi < 40:
        score += 15
    
    # Sentiment (positive/negative factor)
    if sentiment > 0.3:
        score += 20
        reasons.append("Positive market sentiment")
    elif sentiment < -0.3:
        score -= 20
        risk_factors.append("Negative sentiment")
    
    # Recession risk (negative factor)
    if recession_prob > 0.5:
        score -= 40
        risk_factors.append(f"High recession risk ({recession_prob:.0%})")
    elif recession_prob > 0.3:
        score -= 20
        risk_factors.append(f"Moderate recession risk ({recession_prob:.0%})")
    
    # AI bubble risk (negative factor)
    if ai_bubble_risk > 0.6:
        score -= 30
        risk_factors.append(f"High AI bubble risk ({ai_bubble_risk:.0%})")
    elif ai_bubble_risk > 0.4:
        score -= 15
        risk_factors.append(f"Moderate AI bubble concerns")
    
    # CURRENCY RISK ADJUSTMENT (for S&P 500 in EUR)
    if index_name == 'SP500' and currency_risk:
        if currency_risk['risk_level'] == 'high':
            score -= 25
            risk_factors.append(
                f"CURRENCY DRAG: Dollar weakening {currency_risk['change_pct']:.1f}% "
                f"significantly reduces EUR returns"
            )
        elif currency_risk['risk_level'] == 'moderate':
            score -= 15
            risk_factors.append(
                f"Currency headwind: Dollar down {currency_risk['change_pct']:.1f}%"
            )
        elif currency_risk['trend'] == 'strengthening':
            score += 10
            reasons.append(
                f"Currency tailwind: Dollar strengthening {abs(currency_risk['change_pct']):.1f}%"
            )
    
    # Adjust for risk tolerance
    thresholds = {
        'conservative': (60, 40, 20),  # STRONG_BUY, BUY, HOLD thresholds
        'moderate': (50, 30, 10),
        'aggressive': (40, 20, 0)
    }
    
    strong_buy, buy, hold = thresholds[risk_tolerance]
    
    if score >= strong_buy:
        return 'STRONG_BUY', score/100, reasons, risk_factors
    elif score >= buy:
        return 'BUY', score/100, reasons, risk_factors
    elif score >= hold:
        return 'HOLD', score/100, reasons, risk_factors
    else:
        return 'AVOID', score/100, reasons, risk_factors
```

### 5.6 M2 Money Supply Assessment
```python
def assess_m2_favorability(m2_yoy_growth):
    """
    Assess whether M2 growth is favorable for investing
    
    Args:
        m2_yoy_growth: Year-over-year M2 growth percentage
    
    Returns:
        Dictionary with favorability assessment and score
    """
    if m2_yoy_growth is None:
        return {
            'is_favorable': None,
            'score': 0,
            'message': 'M2 data not available',
            'impact': 'neutral'
        }
    
    if m2_yoy_growth > 5:
        return {
            'is_favorable': True,
            'score': 20,
            'message': f'Strong M2 expansion (+{m2_yoy_growth:.1f}% YoY) supports asset prices',
            'impact': 'strongly_positive'
        }
    elif m2_yoy_growth > 2:
        return {
            'is_favorable': True,
            'score': 10,
            'message': f'M2 expanding (+{m2_yoy_growth:.1f}% YoY) moderately supports investment',
            'impact': 'positive'
        }
    elif m2_yoy_growth > -2:
        return {
            'is_favorable': None,
            'score': 0,
            'message': f'M2 stable ({m2_yoy_growth:+.1f}% YoY) - neutral environment',
            'impact': 'neutral'
        }
    else:
        return {
            'is_favorable': False,
            'score': -15,
            'message': f'M2 contracting ({m2_yoy_growth:.1f}% YoY) - headwind for assets',
            'impact': 'negative'
        }
```

---

## 6. Configuration & Settings

### 6.1 Environment Variables (.env)
```bash
# Optional - only needed if using NewsAPI or FRED
NEWS_API_KEY=your_key_here  # Optional (100 free requests/day)
FRED_API_KEY=your_key_here  # Optional (for economic data)

# Application Settings
DEFAULT_RISK_TOLERANCE=moderate
HISTORICAL_YEARS=20
NEWS_LOOKBACK_DAYS=30
VERBOSE_OUTPUT=False

# Database
DB_PATH=./data/market_data.db
```

### 6.2 Configuration File (config.yaml) - Optional
```yaml
indices:
  sp500:
    ticker: ^GSPC
    name: "S&P 500"
    currency: USD
    adjust_for_eur: true  # Calculate EUR-adjusted returns
  cw8:
    ticker: CW8.PA
    name: "MSCI World (CW8)"
    currency: EUR
    adjust_for_eur: false  # Already in EUR

exchange_rates:
  eur_usd:
    ticker: EURUSD=X
    name: "EUR/USD"

technical_analysis:
  rsi_period: 14
  rsi_oversold: 30
  rsi_overbought: 70
  ma_short: 50
  ma_long: 200
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9

sentiment_analysis:
  news_sources:
    - google_news_rss
    - yahoo_finance_rss
  lookback_days: 30
  sentiment_decay_factor: 0.9
  keywords:
    - "S&P 500"
    - "stock market"
    - "recession"
    - "AI bubble"
    - "Federal Reserve"
    - "dollar strength"
    - "EUR/USD"
    - "ECB policy"

decision_engine:
  dip_threshold_moderate: -3.0
  dip_threshold_significant: -5.0
  recession_high_threshold: 0.5
  recession_moderate_threshold: 0.3
  ai_bubble_high_threshold: 0.6
  ai_bubble_moderate_threshold: 0.4
  
  # Currency risk thresholds
  currency_risk_high: 2.5      # > 2.5% move is high risk
  currency_risk_moderate: 1.5  # > 1.5% move is moderate risk

risk_profiles:
  conservative:
    strong_buy_score: 60
    buy_score: 40
    hold_score: 20
  moderate:
    strong_buy_score: 50
    buy_score: 30
    hold_score: 10
  aggressive:
    strong_buy_score: 40
    buy_score: 20
    hold_score: 0
```

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Data collector functions (mock yfinance responses)
- Technical indicators calculations (known test data)
- Sentiment analysis accuracy
- Decision engine logic with various scenarios

### 7.2 Integration Tests
- Database operations (create, read, update)
- End-to-end CLI flow
- Data update mechanism

### 7.3 Manual Testing
- Test with real market data
- Verify calculations manually
- Check output formatting
- Test error scenarios (no internet, bad data)

### 7.4 Performance
- Ensure < 30 seconds for full run
- Optimize database queries
- Cache indicators when possible

---

## 8. Dependencies & Installation

### 8.1 Python Dependencies (requirements.txt)
```txt
# Core
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.28         # Free market data

# Technical Analysis
pandas-ta>=0.3.14b       # Pure Python, no C deps

# Sentiment Analysis
vaderSentiment>=3.3.2    # Best for news/social media
# or textblob>=0.17.1    # Alternative

# News Collection
feedparser>=6.0.10       # RSS parser
requests>=2.31.0         # HTTP requests
beautifulsoup4>=4.12.0   # Web scraping (optional)

# CLI & Display
rich>=13.5.0             # Beautiful terminal output
click>=8.1.0             # CLI framework

# Database
# (sqlite3 is built-in to Python)

# Configuration
python-dotenv>=1.0.0     # .env file support
pyyaml>=6.0              # YAML config (optional)

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

### 8.2 Installation Steps
```bash
# 1. Clone or download the project
git clone <repository-url>
cd invest-advisor

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. First run (initializes database with 20 years data)
python invest_advisor.py --init

# 6. Regular usage
python invest_advisor.py
```

---

## 9. Security & Privacy

- [ ] All data stored locally (no cloud uploads)
- [ ] No personal financial information collected
- [ ] API keys (if used) stored in .env file (gitignored)
- [ ] No telemetry or tracking
- [ ] Open source - auditable code

---

## 10. Limitations & Disclaimers

### 10.1 Important Disclaimers
⚠️ **This application is for educational and informational purposes only**
- Not professional financial advice
- Past performance does not guarantee future results
- User assumes all investment risk
- Consult with licensed financial advisor for investment decisions

### 10.2 Known Limitations
- Market data may have delays
- News sentiment analysis is not 100% accurate
- Cannot predict black swan events
- Technical analysis has inherent uncertainties
- No guarantee of profitability

---

## 11. Future Enhancements (Optional)

### 11.1 Advanced Features
- [ ] Simple backtesting to validate strategy
- [ ] Support for additional indices (NASDAQ, DAX, etc.)
- [ ] Historical performance tracking of recommendations
- [ ] Export recommendations to Excel
- [ ] Price alerts (email notifications)

### 11.2 User Experience
- [ ] Interactive mode (multiple queries in one session)
- [ ] Web dashboard (simple Flask/Streamlit app)
- [ ] Charts and visualizations
- [ ] Customizable thresholds

### 11.3 Analysis Improvements
- [ ] Machine learning predictions (optional)
- [ ] Sector rotation analysis
- [ ] Correlation analysis between indices
- [ ] Support for individual stocks

---

## 12. Success Metrics

### 12.1 Technical Metrics
- Execution time: < 30 seconds per run
- Database size: < 50 MB for 20 years data
- Memory usage: < 500 MB during execution
- Zero crashes or unhandled errors

### 12.2 Usability Metrics
- Simple one-command usage
- Clear, actionable output
- Easy to understand recommendations
- Minimal configuration required

### 12.3 Accuracy Goals (via manual validation)
- Technical indicators match reference calculations
- Sentiment analysis reasonable accuracy (>70%)
- Recommendations align with market conditions

---

## 13. Documentation Requirements

- [ ] README.md with:
  - Installation instructions
  - Usage examples
  - Configuration options
  - Troubleshooting guide
- [ ] Code comments and docstrings
- [ ] Strategy explanation document
- [ ] Example output screenshots
- [ ] FAQ section

---

## Appendix A: Example Usage

### Installation
```bash
# Setup
git clone <repo-url>
cd invest-advisor
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# First run - initialize database
python invest_advisor.py --init
# This downloads 20 years of data (takes 2-5 minutes)

# Regular usage
python invest_advisor.py
```

### Daily Usage
```bash
# Check if you should invest today
$ python invest_advisor.py

# With specific risk profile
$ python invest_advisor.py --risk conservative

# Focus on specific index
$ python invest_advisor.py --index sp500

# Verbose output with more details
$ python invest_advisor.py --verbose

# Force full data refresh
$ python invest_advisor.py --force-update
```

### Additional Commands
```bash
# View historical data
$ python invest_advisor.py --history 30

# Export recommendation log
$ python invest_advisor.py --export-log my_recommendations.csv

# Show database statistics
$ python invest_advisor.py --stats
```

---

## Appendix B: Risk Assessment Matrix

| Market Condition | Dip % | RSI | Sentiment | Recession Risk | AI Bubble Risk | Currency Impact | Recommendation |
|-----------------|-------|-----|-----------|----------------|----------------|-----------------|----------------|
| Strong Opportunity (EUR) | -7% | 25 | +0.4 | 10% | 20% | USD +1% | STRONG BUY |
| Good Entry (EUR) | -5% | 32 | +0.2 | 15% | 35% | USD stable | BUY |
| Currency Drag | -3% | 35 | +0.1 | 20% | 30% | USD -3% | HOLD/WAIT |
| Uncertain | -3% | 45 | 0.0 | 30% | 50% | USD -1% | HOLD/WAIT |
| High Risk | -8% | 28 | -0.5 | 60% | 70% | USD -2% | AVOID |
| Falling Knife | -12% | 22 | -0.7 | 75% | 40% | USD stable | AVOID |
| EUR Investor Alert | -2% | 40 | +0.2 | 15% | 30% | USD -5% | AVOID (currency) |

---

## Questions & Decisions Summary

### ✅ Confirmed Decisions:
1. **Interface**: CLI (command-line) - Simple `python invest_advisor.py`
2. **Database**: SQLite (local file, no server)
3. **Data Source**: yfinance (free, 20 years historical data)
4. **News**: Google News RSS + Yahoo Finance RSS (free)
5. **Sentiment**: VADER or TextBlob (free, no API keys)
6. **Historical Data**: 20 years
7. **Update Frequency**: On-demand (each time you run it)
8. **Analysis**: Technical indicators + Sentiment analysis
9. **Free Services**: 100% free, no paid APIs required

### ✅ User Configuration:
1. **Risk Profile**: **Moderate** (balanced approach to buy signals)
2. **Operating System**: **Linux**
3. **Python Version**: **Python 3.10.12** ✓ (Compatible - minimum 3.9+ required)
4. **Display Preferences**: Colored terminal output (default)
5. **Initial Setup**: 2-5 minute wait acceptable

---

## Next Steps

1. ✅ **Specification reviewed and approved**
2. ✅ **User configuration confirmed**
3. ⏳ **Ready to start implementation when requested**

**Implementation will begin with Phase 1**:
   - Create project structure
   - Setup SQLite database
   - Implement yfinance data collector
   - Download initial 20 years of data

---

**Document Version**: 2.0  
**Date**: January 5, 2026  
**Status**: ✅ **Specification Approved - Awaiting Implementation Start**

**Target Environment**: 
- Linux
- Python 3.10.12
- Moderate risk tolerance (default)
