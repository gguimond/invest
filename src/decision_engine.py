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
        elif index_name == 'STOXX600':
            # BONUS: No currency risk for EUR investors!
            score += 5
            reasons.append("✅ No currency risk (EUR-denominated)")
            # Phase 6B: STOXX600 uses Eurozone M2 data (not US M2)
        
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
        cw8_result: Dict,
        stoxx600_result: Optional[Dict] = None
    ) -> Dict:
        """
        Compare recommendations to provide overall advice
        Supports 2 or 3 indices
        
        Args:
            sp500_result: SP500 recommendation result
            cw8_result: CW8 recommendation result
            stoxx600_result: STOXX600 recommendation result (optional)
            
        Returns:
            Dictionary with comparative analysis
        """
        # Collect scores
        scores = {
            'sp500': sp500_result['score'],
            'cw8': cw8_result['score']
        }
        
        if stoxx600_result:
            scores['stoxx600'] = stoxx600_result['score']
        
        # Find best option
        best_index = max(scores, key=scores.get)
        best_score = scores[best_index]
        worst_score = min(scores.values())
        
        # Determine preference message
        if stoxx600_result:
            # 3-way comparison
            if best_index == 'stoxx600':
                message = "🇪🇺 STOXX 600 shows strongest opportunity (+ no currency risk!)"
            elif best_index == 'sp500':
                message = "🇺🇸 S&P 500 shows strongest opportunity (watch dollar impact)"
            else:  # cw8
                message = "🌍 MSCI World shows strongest opportunity (global diversification)"
            
            # Check if scores are close (within 10 points) - suggest diversification
            if best_score - worst_score < 10:
                message = "⚖️ All indices show similar opportunities - consider diversifying"
                preference = 'multiple'
            else:
                preference = best_index
        else:
            # 2-way comparison (original logic)
            if scores['sp500'] > scores['cw8'] + 15:
                preference = 'sp500'
                message = "🇺🇸 S&P 500 shows stronger opportunity"
            elif scores['cw8'] > scores['sp500'] + 15:
                preference = 'cw8'
                message = "🌍 MSCI World (CW8) shows stronger opportunity"
            else:
                preference = 'both'
                message = "⚖️ Both indices show similar opportunities"
        
        # Overall recommendation logic
        results = [sp500_result, cw8_result]
        if stoxx600_result:
            results.append(stoxx600_result)
        
        buy_count = sum(1 for r in results if r['recommendation'] in [Recommendation.STRONG_BUY, Recommendation.BUY])
        hold_count = sum(1 for r in results if r['recommendation'] == Recommendation.HOLD)
        
        if buy_count >= 2:
            overall = "INVEST"
            action = f"Good time to invest - {buy_count} of {len(results)} indices show buy signals"
        elif buy_count >= 1:
            overall = "SELECTIVE"
            if stoxx600_result and preference == 'stoxx600':
                action = "Consider investing in STOXX 600 (European focus, no FX risk)"
            elif preference == 'sp500':
                action = "Consider investing in S&P 500"
            elif preference == 'cw8':
                action = "Consider investing in MSCI World (CW8)"
            else:
                action = "Consider selective investment in better-performing indices"
        elif hold_count > 0:
            overall = "WAIT"
            action = "Wait for better entry point or more clarity"
        else:
            overall = "AVOID"
            action = "Not a good time to invest - multiple risk factors present"
        
        # Generate diversification suggestions
        diversification = self._generate_diversification_suggestions(
            scores, 
            preference, 
            stoxx600_result is not None
        )
        
        return {
            'preference': preference,
            'message': message,
            'overall_recommendation': overall,
            'action': action,
            'sp500_score': scores['sp500'],
            'cw8_score': scores['cw8'],
            'stoxx600_score': scores.get('stoxx600'),
            'score_difference': best_score - worst_score,
            'scores': scores,
            'diversification': diversification
        }
    
    def _generate_diversification_suggestions(
        self, 
        scores: Dict[str, int], 
        preference: str,
        has_stoxx600: bool
    ) -> Dict:
        """
        Generate portfolio allocation suggestions based on scores
        
        Args:
            scores: Dictionary of index scores
            preference: Preferred index or 'multiple'
            has_stoxx600: Whether STOXX600 is analyzed
            
        Returns:
            Dictionary with allocation suggestions
        """
        allocations = {}
        
        if not has_stoxx600:
            # 2-way allocation (SP500 vs CW8)
            total = scores['sp500'] + scores['cw8']
            if total > 0:
                sp500_pct = max(0, min(100, int((scores['sp500'] / total) * 100)))
                cw8_pct = 100 - sp500_pct
            else:
                sp500_pct = 50
                cw8_pct = 50
            
            allocations = {
                'conservative': {
                    'sp500': min(sp500_pct, 40),
                    'cw8': 100 - min(sp500_pct, 40),
                    'description': 'Lower risk, favor global diversification'
                },
                'moderate': {
                    'sp500': sp500_pct,
                    'cw8': cw8_pct,
                    'description': 'Balanced allocation based on current scores'
                },
                'aggressive': {
                    'sp500': min(sp500_pct + 10, 70),
                    'cw8': max(cw8_pct - 10, 30),
                    'description': 'Higher concentration in best performer'
                }
            }
        else:
            # 3-way allocation (SP500 vs CW8 vs STOXX600)
            total = scores['sp500'] + scores['cw8'] + scores['stoxx600']
            
            if total > 0:
                sp500_base = max(0, int((scores['sp500'] / total) * 100))
                cw8_base = max(0, int((scores['cw8'] / total) * 100))
                stoxx_base = 100 - sp500_base - cw8_base  # Ensure 100% total
            else:
                sp500_base = 33
                cw8_base = 33
                stoxx_base = 34
            
            # Conservative: Favor STOXX600 (no currency risk), balanced otherwise
            allocations['conservative'] = {
                'sp500': max(10, min(sp500_base, 30)),
                'cw8': max(20, min(cw8_base, 40)),
                'stoxx600': None,  # Calculate remainder
                'description': 'EUR investor focus: Favor European exposure, no currency risk'
            }
            allocations['conservative']['stoxx600'] = (
                100 - allocations['conservative']['sp500'] - allocations['conservative']['cw8']
            )
            
            # Moderate: Score-based allocation
            allocations['moderate'] = {
                'sp500': sp500_base,
                'cw8': cw8_base,
                'stoxx600': stoxx_base,
                'description': 'Balanced allocation based on current opportunity scores'
            }
            
            # Aggressive: Concentrate in top 2 performers
            sorted_indices = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best = sorted_indices[0][0]
            second = sorted_indices[1][0]
            
            if best == 'sp500':
                best_key = 'sp500'
            elif best == 'cw8':
                best_key = 'cw8'
            else:
                best_key = 'stoxx600'
            
            if second == 'sp500':
                second_key = 'sp500'
            elif second == 'cw8':
                second_key = 'cw8'
            else:
                second_key = 'stoxx600'
            
            allocations['aggressive'] = {
                'sp500': 0,
                'cw8': 0,
                'stoxx600': 0,
                'description': f'Concentrated in best performers: {best.upper()} and {second.upper()}'
            }
            allocations['aggressive'][best_key] = 60
            allocations['aggressive'][second_key] = 40
        
        # Add investment rationale
        if has_stoxx600:
            if preference == 'stoxx600':
                rationale = (
                    "🇪🇺 STOXX 600 is preferred: No currency risk for EUR investors, "
                    "strong European opportunity. Consider 50-60% allocation."
                )
            elif preference == 'sp500':
                rationale = (
                    "🇺🇸 S&P 500 shows strength, but watch USD/EUR exchange rate. "
                    "Consider hedging currency risk or limiting exposure."
                )
            elif preference == 'cw8':
                rationale = (
                    "🌍 MSCI World offers global diversification with mixed currency exposure. "
                    "Good balance between growth and risk management."
                )
            else:
                rationale = (
                    "⚖️ All indices show similar opportunities. Diversify across all three "
                    "for geographic and currency diversification."
                )
        else:
            if preference == 'sp500':
                rationale = "🇺🇸 S&P 500 preferred, but monitor currency impact for EUR investors."
            elif preference == 'cw8':
                rationale = "🌍 MSCI World preferred for global diversification."
            else:
                rationale = "⚖️ Similar opportunities - diversify between both indices."
        
        return {
            'allocations': allocations,
            'rationale': rationale,
            'recommended_profile': self.risk_tolerance.value
        }
