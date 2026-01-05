# M2 Money Supply Integration

## ✅ M2 Money Supply Feature Added

M2 Money Supply is now integrated into the Investment Advisor as a key economic indicator.

### What is M2 Money Supply?

M2 represents the total money supply in the economy, including:
- Cash and checking deposits (M1)
- Savings deposits
- Money market securities
- Other time deposits

**Why it matters for investing:**
- **M2 increasing** = More money in the economy → Supports asset prices → **FAVORABLE for buying**
- **M2 decreasing** = Money supply contracting → Headwind for assets → **LESS FAVORABLE**

### Integration Details

#### 1. **Data Source: FRED API**
- Free API from Federal Reserve Economic Data
- Monthly M2 data (series: M2SL)
- Historical data available back 20+ years
- Get your free API key: https://fred.stlouisfed.org/docs/api/api_key.html

#### 2. **Database Schema**
New table added: `economic_indicators`
```sql
CREATE TABLE economic_indicators (
    indicator_name TEXT,  -- 'M2', etc.
    date DATE,
    value REAL,
    yoy_change REAL,      -- Year-over-year % change
    mom_change REAL       -- Month-over-month % change
)
```

#### 3. **Decision Algorithm Integration**

M2 growth is now factored into BUY recommendations:

| M2 YoY Growth | Impact | Score | Message |
|---------------|--------|-------|---------|
| > +5% | Strongly Positive | +20 | Strong M2 expansion supports asset prices |
| +2% to +5% | Positive | +10 | M2 expanding moderately supports investment |
| -2% to +2% | Neutral | 0 | M2 stable - neutral environment |
| < -2% | Negative | -15 | M2 contracting - headwind for assets |

**Example:**
- Market dips 5% (Score: +30)
- RSI oversold (Score: +25)
- Positive sentiment (Score: +20)
- **M2 growing +6%** (Score: **+20**)
- **Total: 95 → STRONG BUY** 🟢

Without M2 consideration, this would be just 75 (regular BUY).

### Configuration

#### Setup FRED API Key

1. Get free API key: https://fred.stlouisfed.org/docs/api/api_key.html
2. Add to `.env` file:
```bash
FRED_API_KEY=your_actual_fred_api_key_here
```

3. Or set as environment variable:
```bash
export FRED_API_KEY="your_key_here"
```

#### M2 Thresholds (in `src/config.py`)
```python
DECISION_PARAMS = {
    "m2_growth_positive": 2.0,      # >2% YoY is positive
    "m2_growth_strong": 5.0,        # >5% YoY is strong positive
    "m2_growth_negative": -2.0,     # <-2% YoY is negative
    "m2_lookback_months": 12        # Compare to 12 months ago
}
```

### Usage

#### Initialize with M2 Data
```bash
# First time - downloads 20 years of M2 data
python3 invest_advisor.py --init
```

Output will include:
```
Fetching M2 Money Supply data from FRED...
✓ Fetched 240 M2 observations
✓ Stored 240 records for M2
✓ M2 YoY Growth: +5.2%
```

#### View M2 Statistics
```bash
python3 invest_advisor.py --stats
```

Shows:
```
💵 M2 Money Supply
Records: 240
Latest YoY Growth: +5.2%
```

#### Get Recommendations (Phase 2+)
Once Phase 2-4 are implemented, M2 will automatically be factored into investment recommendations.

### Implementation Files

#### New Files:
- `src/economic_data.py` - FRED API integration and M2 calculations

#### Modified Files:
- `src/config.py` - Added M2 configuration and thresholds
- `src/database.py` - Added economic_indicators table and M2 methods
- `invest_advisor.py` - Integrated M2 fetching and display
- `.env.example` - Added FRED_API_KEY

### API Methods

#### `EconomicDataCollector` Class
```python
from src.economic_data import EconomicDataCollector

collector = EconomicDataCollector(api_key="your_key")

# Fetch historical M2 data
m2_data = collector.fetch_m2_data(years=20)

# Update with latest data
new_m2 = collector.update_m2_data(last_date="2025-12-01")

# Calculate growth rates
stats = collector.calculate_m2_growth_rate(m2_data)
# Returns: {
#     'current_value': 21500.0,
#     'yoy_growth': 5.2,
#     'mom_growth': 0.4,
#     'trend': 'expansion'
# }

# Assess favorability for investing
assessment = collector.assess_m2_favorability(yoy_growth=5.2)
# Returns: {
#     'is_favorable': True,
#     'score': 10,
#     'message': 'M2 expanding (+5.2% YoY) moderately supports investment',
#     'impact': 'positive'
# }
```

#### Database Methods
```python
from src.database import Database

with Database() as db:
    # Store M2 data
    db.store_economic_indicator('M2', m2_dataframe)
    
    # Retrieve M2 data
    m2_data = db.get_economic_indicator('M2', 
                                        start_date='2020-01-01',
                                        end_date='2025-12-31')
    
    # Get latest growth rate
    latest_growth = db.get_latest_m2_growth()
    # Returns: 5.2 (percent)
```

### Future Enhancements

Potential additional economic indicators to integrate:
- **GDP Growth** - Overall economic health
- **Unemployment Rate** - Labor market strength  
- **CPI Inflation** - Price stability
- **10Y-2Y Yield Spread** - Recession predictor
- **Fed Funds Rate** - Monetary policy stance

### Troubleshooting

**"FRED API key not configured"**
- Get free API key from FRED website
- Add to `.env` file or environment variable
- M2 data will be skipped if API key is missing (optional feature)

**"Could not fetch M2 data"**
- Check internet connection
- Verify API key is valid
- FRED API might be temporarily unavailable
- Check API rate limits (120 requests/minute)

**"No new M2 data available"**
- M2 is released monthly, usually mid-month
- Check FRED website for release schedule
- Data might not be available yet for current month

### References

- **FRED M2 Data**: https://fred.stlouisfed.org/series/M2SL
- **FRED API Docs**: https://fred.stlouisfed.org/docs/api/
- **M2 Money Supply Explained**: https://www.federalreserve.gov/releases/h6/current/

---

**Feature Status**: ✅ **COMPLETE**  
**Version**: 1.1  
**Database Version**: 1.1
