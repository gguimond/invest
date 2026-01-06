"""Decision engine for investment recommendations"""

from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class Recommendation(Enum):
    """Investment recommendation types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    AVOID = "AVOID"


class RiskTolerance(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class DecisionFactors:
    """All factors that influence the investment decision"""
    # Technical factors
    dip_percentage: float
    rsi: float
    rsi_status: str
    macd_bullish: bool
    trend: str
    price_vs_ma50: float
    price_vs_ma200: float
    golden_cross: bool
    volatility_level: str
    
    # Sentiment factors
    overall_sentiment: float
    sentiment_label: str
    market_tone: str
    bullish_ratio: float
    bearish_ratio: float
    
    # Risk factors
    recession_probability: float
    recession_level: str
    ai_bubble_risk: float
    ai_bubble_level: str
    
    # M2 Money Supply (KEY FACTOR!)
    m2_yoy_growth: Optional[float]
    m2_score: int
    m2_favorability: str
    
    # Currency factors (for S&P 500 in EUR)
    currency_risk_level: Optional[str] = None
    currency_change_pct: Optional[float] = None
    currency_impact: Optional[str] = None


class DecisionEngine:
    """
    Generate investment recommendations based on all available data
    Integrates: Technical Analysis + M2 Money Supply + Sentiment + Currency Risk
    """
    
    def __init__(self, risk_tolerance: str = "moderate"):
        self.risk_tolerance = RiskTolerance(risk_tolerance)
        
        # Score thresholds for each risk tolerance level
        self.thresholds = {
            RiskTolerance.CONSERVATIVE: {
                'strong_buy': 70,
                'buy': 50,
                'hold': 30
            },
            RiskTolerance.MODERATE: {
                'strong_buy': 60,
                'buy': 40,
                'hold': 20
            },
            RiskTolerance.AGGRESSIVE: {
                'strong_buy': 50,
                'buy': 30,
                'hold': 10
            }
        }
    
    def generate_recommendation(
        self,
        index_name: str,
        factors: DecisionFactors
    ) -> Dict:
        """
        Generate investment recommendation based on all factors
        
        Args:
            index_name: Index name (SP500 or CW8)
            factors: All decision factors
            
        Returns:
            Dictionary with recommendation and details
        """
        score = 0
        reasons = []
        risk_factors = []
        
        # ============================================================
        # 1. DIP DETECTION (Opportunity Factor)
        # ============================================================
        if factors.dip_percentage < -7:
            score += 35
            reasons.append(f"Major dip: {factors.dip_percentage:.1f}% - excellent entry point")
        elif factors.dip_percentage < -5:
            score += 30
            reasons.append(f"Significant dip: {factors.dip_percentage:.1f}%")
        elif factors.dip_percentage < -3:
            score += 20
            reasons.append(f"Moderate dip: {factors.dip_percentage:.1f}%")
        elif factors.dip_percentage < -1:
            score += 10
            reasons.append(f"Small dip: {factors.dip_percentage:.1f}%")
        else:
            score -= 5
            risk_factors.append(f"Near high ({factors.dip_percentage:+.1f}%) - limited upside")
        
        # ============================================================
        # 2. RSI - MOMENTUM INDICATOR
        # ============================================================
        if factors.rsi < 30:
            score += 25
            reasons.append(f"Oversold (RSI: {factors.rsi:.0f}) - bounce likely")
        elif factors.rsi < 40:
            score += 15
            reasons.append(f"Approaching oversold (RSI: {factors.rsi:.0f})")
        elif factors.rsi > 70:
            score -= 20
            risk_factors.append(f"Overbought (RSI: {factors.rsi:.0f}) - pullback risk")
        elif factors.rsi > 60:
            score -= 10
            risk_factors.append(f"Elevated RSI ({factors.rsi:.0f})")
        
        # ============================================================
        # 3. TREND ANALYSIS
        # ============================================================
        if factors.trend in ['strong_uptrend', 'uptrend']:
            score += 10
            reasons.append(f"Trend: {factors.trend.replace('_', ' ')}")
        elif factors.trend in ['strong_downtrend', 'downtrend']:
            score -= 15
            risk_factors.append(f"Trend: {factors.trend.replace('_', ' ')}")
        
        if factors.golden_cross:
            score += 5
            reasons.append("Golden cross (bullish)")
        
        # ============================================================
        # 4. MACD
        # ============================================================
        if factors.macd_bullish:
            score += 10
            reasons.append("MACD bullish crossover")
        else:
            score -= 5
        
        # ============================================================
        # 5. M2 MONEY SUPPLY (KEY INDICATOR!) 💵
        # ============================================================
        if factors.m2_yoy_growth is not None:
            # Add M2 score directly
            score += factors.m2_score
            
            if factors.m2_score >= 20:
                reasons.append(f"💵 Strong M2 expansion (+{factors.m2_yoy_growth:.1f}% YoY) - very supportive")
            elif factors.m2_score >= 10:
                reasons.append(f"💵 M2 expanding (+{factors.m2_yoy_growth:.1f}% YoY) - supportive")
            elif factors.m2_score <= -15:
                risk_factors.append(f"💵 M2 contracting ({factors.m2_yoy_growth:.1f}% YoY) - liquidity headwind")
            else:
                # Neutral M2
                pass
        else:
            risk_factors.append("M2 data not available")
        
        # ============================================================
        # 6. SENTIMENT ANALYSIS
        # ============================================================
        if factors.overall_sentiment > 0.2:
            score += 20
            reasons.append(f"Strong positive sentiment ({factors.overall_sentiment:+.2f})")
        elif factors.overall_sentiment > 0.05:
            score += 10
            reasons.append(f"Positive sentiment ({factors.overall_sentiment:+.2f})")
        elif factors.overall_sentiment < -0.2:
            score -= 20
            risk_factors.append(f"Negative sentiment ({factors.overall_sentiment:-.2f})")
        elif factors.overall_sentiment < -0.05:
            score -= 10
            risk_factors.append(f"Slightly negative sentiment ({factors.overall_sentiment:-.2f})")
        
        # Market tone
        if factors.market_tone == 'bullish' and factors.bullish_ratio > 0.25:
            score += 10
            reasons.append(f"Bullish market tone ({factors.bullish_ratio:.0%} bullish articles)")
        elif factors.market_tone == 'bearish':
            score -= 15
            risk_factors.append(f"Bearish market tone")
        
        # ============================================================
        # 7. RECESSION PROBABILITY
        # ============================================================
        if factors.recession_probability > 0.6:
            score -= 40
            risk_factors.append(f"High recession risk ({factors.recession_probability:.0%})")
        elif factors.recession_probability > 0.3:
            score -= 20
            risk_factors.append(f"Moderate recession risk ({factors.recession_probability:.0%})")
        elif factors.recession_probability < 0.1:
            score += 5
            reasons.append("Low recession risk")
        
        # ============================================================
        # 8. AI BUBBLE RISK
        # ============================================================
        if factors.ai_bubble_risk > 0.6:
            score -= 30
            risk_factors.append(f"High AI/tech bubble risk ({factors.ai_bubble_risk:.0%})")
        elif factors.ai_bubble_risk > 0.4:
            score -= 15
            risk_factors.append(f"Moderate AI bubble concerns ({factors.ai_bubble_risk:.0%})")
        elif factors.ai_bubble_risk < 0.2:
            score += 5
            reasons.append("Low bubble risk")
        
        # ============================================================
        # 9. VOLATILITY
        # ============================================================
        if factors.volatility_level == 'high':
            score -= 10
            risk_factors.append("High volatility")
        elif factors.volatility_level == 'low':
            score += 5
            reasons.append("Low volatility")
        
        # ============================================================
        # 10. CURRENCY RISK (for S&P 500 in EUR terms)
        # ============================================================
        if index_name == 'SP500' and factors.currency_risk_level:
            if factors.currency_risk_level == 'high':
                score -= 25
                risk_factors.append(
                    f"⚠️ CURRENCY DRAG: Dollar weakening {factors.currency_change_pct:.1f}% "
                    f"significantly reduces EUR returns"
                )
            elif factors.currency_risk_level == 'moderate':
                score -= 15
                risk_factors.append(
                    f"Currency headwind: Dollar down {factors.currency_change_pct:.1f}%"
                )
            elif factors.currency_impact == 'positive':
                score += 10
                reasons.append(
                    f"Currency tailwind: Dollar strengthening {abs(factors.currency_change_pct):.1f}%"
                )
        
        # ============================================================
        # FINAL RECOMMENDATION
        # ============================================================
        thresholds = self.thresholds[self.risk_tolerance]
        
        if score >= thresholds['strong_buy']:
            recommendation = Recommendation.STRONG_BUY
            confidence = min(score / 100, 0.95)
        elif score >= thresholds['buy']:
            recommendation = Recommendation.BUY
            confidence = min(score / 100, 0.85)
        elif score >= thresholds['hold']:
            recommendation = Recommendation.HOLD
            confidence = min(score / 100, 0.70)
        else:
            recommendation = Recommendation.AVOID
            confidence = min(abs(score) / 100, 0.80)
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'score': score,
            'reasons': reasons,
            'risk_factors': risk_factors,
            'risk_tolerance': self.risk_tolerance.value
        }
    
    def compare_recommendations(
        self,
        sp500_result: Dict,
        cw8_result: Dict
    ) -> Dict:
        """
        Compare SP500 and CW8 recommendations to provide overall advice
        
        Args:
            sp500_result: SP500 recommendation result
            cw8_result: CW8 recommendation result
            
        Returns:
            Dictionary with comparative analysis
        """
        sp500_rec = sp500_result['recommendation']
        cw8_rec = cw8_result['recommendation']
        sp500_score = sp500_result['score']
        cw8_score = cw8_result['score']
        
        # Determine best option
        if sp500_score > cw8_score + 15:
            preference = 'sp500'
            message = "🇺🇸 S&P 500 shows stronger opportunity"
        elif cw8_score > sp500_score + 15:
            preference = 'cw8'
            message = "🌍 MSCI World (CW8) shows stronger opportunity"
        else:
            preference = 'both'
            message = "⚖️ Both indices show similar opportunities"
        
        # Overall recommendation
        if sp500_rec in [Recommendation.STRONG_BUY, Recommendation.BUY] and \
           cw8_rec in [Recommendation.STRONG_BUY, Recommendation.BUY]:
            overall = "INVEST"
            action = "Good time to invest in both indices"
        elif sp500_rec in [Recommendation.STRONG_BUY, Recommendation.BUY] or \
             cw8_rec in [Recommendation.STRONG_BUY, Recommendation.BUY]:
            overall = "SELECTIVE"
            if preference == 'sp500':
                action = "Consider investing in S&P 500"
            elif preference == 'cw8':
                action = "Consider investing in MSCI World (CW8)"
            else:
                action = "Consider investing, slight preference for better-scoring index"
        elif sp500_rec == Recommendation.HOLD or cw8_rec == Recommendation.HOLD:
            overall = "WAIT"
            action = "Wait for better entry point or more clarity"
        else:
            overall = "AVOID"
            action = "Not a good time to invest - multiple risk factors present"
        
        return {
            'preference': preference,
            'message': message,
            'overall_recommendation': overall,
            'action': action,
            'sp500_score': sp500_score,
            'cw8_score': cw8_score,
            'score_difference': abs(sp500_score - cw8_score)
        }
