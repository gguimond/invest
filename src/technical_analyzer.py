"""Technical analysis module for calculating market indicators"""

import pandas as pd
import numpy as np
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from typing import Dict, Optional, Tuple
from src.config import TECHNICAL_PARAMS


class TechnicalAnalyzer:
    """Calculate technical indicators for market data"""
    
    def __init__(self):
        self.rsi_period = TECHNICAL_PARAMS['rsi_period']
        self.ma_short = TECHNICAL_PARAMS['ma_short']
        self.ma_long = TECHNICAL_PARAMS['ma_long']
        self.macd_fast = TECHNICAL_PARAMS['macd_fast']
        self.macd_slow = TECHNICAL_PARAMS['macd_slow']
        self.macd_signal = TECHNICAL_PARAMS['macd_signal']
        self.lookback_window = TECHNICAL_PARAMS['lookback_window']
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for a given dataframe
        
        Args:
            df: DataFrame with 'close', 'high', 'low' columns
            
        Returns:
            DataFrame with all indicators added
        """
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        # Ensure column names are lowercase for consistency
        df.columns = [col.lower() for col in df.columns]
        
        # Check required columns exist
        required_cols = ['close', 'high', 'low']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame missing required columns. Has: {list(df.columns)}, needs: {required_cols}")
        
        # Calculate all indicators
        df = self._calculate_moving_averages(df)
        df = self._calculate_rsi(df)
        df = self._calculate_macd(df)
        df = self._calculate_bollinger_bands(df)
        df = self._calculate_stochastic(df)
        df = self._calculate_atr(df)
        
        return df
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Simple and Exponential Moving Averages"""
        # Short-term MA (50-day)
        sma_short = SMAIndicator(close=df['close'], window=self.ma_short)
        df['sma_50'] = sma_short.sma_indicator()
        
        ema_short = EMAIndicator(close=df['close'], window=self.ma_short)
        df['ema_50'] = ema_short.ema_indicator()
        
        # Long-term MA (200-day)
        sma_long = SMAIndicator(close=df['close'], window=self.ma_long)
        df['sma_200'] = sma_long.sma_indicator()
        
        ema_long = EMAIndicator(close=df['close'], window=self.ma_long)
        df['ema_200'] = ema_long.ema_indicator()
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        rsi = RSIIndicator(close=df['close'], window=self.rsi_period)
        df['rsi'] = rsi.rsi()
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        macd = MACD(
            close=df['close'],
            window_slow=self.macd_slow,
            window_fast=self.macd_fast,
            window_sign=self.macd_signal
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        return df
    
    def _calculate_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        stoch = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14,
            smooth_window=3
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        return df
    
    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Average True Range (volatility)"""
        atr = AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        )
        df['atr'] = atr.average_true_range()
        return df
    
    def detect_dip(self, df: pd.DataFrame, window: int = None) -> Dict:
        """
        Detect if current price is in a dip
        
        Args:
            df: DataFrame with price data
            window: Lookback window (default from config)
            
        Returns:
            Dictionary with dip analysis
        """
        if window is None:
            window = self.lookback_window
        
        if len(df) < window:
            window = len(df)
        
        recent_data = df.tail(window)
        recent_high = recent_data['high'].max()
        current_price = df['close'].iloc[-1]
        
        dip_percentage = ((current_price - recent_high) / recent_high) * 100
        
        return {
            'dip_percentage': dip_percentage,
            'is_significant_dip': dip_percentage < -3,
            'is_major_dip': dip_percentage < -5,
            'recent_high': recent_high,
            'current_price': current_price,
            'days_from_high': (df.index[-1] - recent_data[recent_data['high'] == recent_high].index[0]).days
        }
    
    def analyze_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze overall trend using moving averages
        
        Returns:
            Dictionary with trend analysis
        """
        if 'sma_50' not in df.columns or 'sma_200' not in df.columns:
            df = self.calculate_all_indicators(df)
        
        current_price = df['close'].iloc[-1]
        sma_50 = df['sma_50'].iloc[-1]
        sma_200 = df['sma_200'].iloc[-1]
        
        # Golden cross / Death cross
        golden_cross = sma_50 > sma_200
        
        # Price position relative to MAs
        above_50 = current_price > sma_50
        above_200 = current_price > sma_200
        
        # Determine trend
        if above_50 and above_200 and golden_cross:
            trend = 'strong_uptrend'
        elif above_50 and above_200:
            trend = 'uptrend'
        elif not above_50 and not above_200 and not golden_cross:
            trend = 'strong_downtrend'
        elif not above_50 and not above_200:
            trend = 'downtrend'
        else:
            trend = 'sideways'
        
        return {
            'trend': trend,
            'golden_cross': golden_cross,
            'price_vs_sma50': ((current_price - sma_50) / sma_50) * 100,
            'price_vs_sma200': ((current_price - sma_200) / sma_200) * 100,
            'sma50_vs_sma200': ((sma_50 - sma_200) / sma_200) * 100
        }
    
    def analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """
        Analyze momentum indicators
        
        Returns:
            Dictionary with momentum analysis
        """
        if 'rsi' not in df.columns:
            df = self.calculate_all_indicators(df)
        
        rsi = df['rsi'].iloc[-1]
        macd = df['macd'].iloc[-1]
        macd_signal = df['macd_signal'].iloc[-1]
        macd_diff = df['macd_diff'].iloc[-1]
        stoch_k = df['stoch_k'].iloc[-1]
        
        # RSI interpretation
        if rsi < 30:
            rsi_status = 'oversold'
        elif rsi > 70:
            rsi_status = 'overbought'
        else:
            rsi_status = 'neutral'
        
        # MACD interpretation
        macd_bullish = macd > macd_signal
        
        # Stochastic interpretation
        if stoch_k < 20:
            stoch_status = 'oversold'
        elif stoch_k > 80:
            stoch_status = 'overbought'
        else:
            stoch_status = 'neutral'
        
        return {
            'rsi': rsi,
            'rsi_status': rsi_status,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_diff': macd_diff,
            'macd_bullish': macd_bullish,
            'stochastic_k': stoch_k,
            'stochastic_status': stoch_status
        }
    
    def analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """
        Analyze volatility metrics
        
        Returns:
            Dictionary with volatility analysis
        """
        if 'bb_upper' not in df.columns or 'atr' not in df.columns:
            df = self.calculate_all_indicators(df)
        
        current_price = df['close'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_width = df['bb_width'].iloc[-1]
        atr = df['atr'].iloc[-1]
        
        # Bollinger Band position
        bb_range = bb_upper - bb_lower
        if bb_range > 0:
            bb_position = ((current_price - bb_lower) / bb_range) * 100
        else:
            bb_position = 50
        
        # Calculate recent volatility (std dev of returns)
        returns = df['close'].pct_change().tail(30)
        recent_volatility = returns.std() * np.sqrt(252) * 100  # Annualized
        
        return {
            'bollinger_position': bb_position,
            'bollinger_width': bb_width,
            'atr': atr,
            'atr_percentage': (atr / current_price) * 100,
            'recent_volatility': recent_volatility,
            'volatility_level': 'high' if recent_volatility > 20 else 'moderate' if recent_volatility > 10 else 'low'
        }
    
    def get_support_resistance(self, df: pd.DataFrame, window: int = 90) -> Dict:
        """
        Identify support and resistance levels
        
        Args:
            df: DataFrame with price data
            window: Lookback window for identifying levels
            
        Returns:
            Dictionary with support/resistance levels
        """
        recent_data = df.tail(window)
        
        # Simple approach: recent highs and lows
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        
        # Current price position
        current_price = df['close'].iloc[-1]
        price_range = resistance - support
        
        if price_range > 0:
            position = ((current_price - support) / price_range) * 100
        else:
            position = 50
        
        return {
            'resistance': resistance,
            'support': support,
            'current_price': current_price,
            'position_in_range': position,
            'distance_to_resistance': ((resistance - current_price) / current_price) * 100,
            'distance_to_support': ((current_price - support) / current_price) * 100
        }
    
    def calculate_comprehensive_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive technical analysis
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with all technical analysis results
        """
        # Calculate all indicators first
        df = self.calculate_all_indicators(df)
        
        # Get all analyses
        dip_analysis = self.detect_dip(df)
        trend_analysis = self.analyze_trend(df)
        momentum_analysis = self.analyze_momentum(df)
        volatility_analysis = self.analyze_volatility(df)
        support_resistance = self.get_support_resistance(df)
        
        return {
            'dip': dip_analysis,
            'trend': trend_analysis,
            'momentum': momentum_analysis,
            'volatility': volatility_analysis,
            'support_resistance': support_resistance,
            'dataframe': df  # Return updated dataframe with indicators
        }


def calculate_currency_adjusted_returns(
    sp500_df: pd.DataFrame,
    eurusd_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate S&P 500 returns in EUR terms for EUR-based investors
    
    Args:
        sp500_df: DataFrame with S&P 500 USD prices
        eurusd_df: DataFrame with EUR/USD exchange rates
    
    Returns:
        DataFrame with currency-adjusted returns and impact
    """
    # Align dates
    merged = pd.merge(
        sp500_df[['close']].rename(columns={'close': 'sp500_usd'}),
        eurusd_df[['close']].rename(columns={'close': 'eurusd_rate'}),
        left_index=True,
        right_index=True,
        how='inner'
    )
    
    # Convert S&P 500 USD prices to EUR
    merged['sp500_eur'] = merged['sp500_usd'] / merged['eurusd_rate']
    
    # Calculate returns
    merged['sp500_usd_return'] = merged['sp500_usd'].pct_change() * 100
    merged['sp500_eur_return'] = merged['sp500_eur'].pct_change() * 100
    merged['currency_return'] = merged['eurusd_rate'].pct_change() * 100
    
    # Currency impact = difference between EUR and USD returns
    merged['currency_impact'] = merged['sp500_eur_return'] - merged['sp500_usd_return']
    
    return merged


def assess_currency_risk(eurusd_df: pd.DataFrame, window: int = 30) -> Dict:
    """
    Assess dollar strength/weakness trend
    
    Args:
        eurusd_df: DataFrame with EUR/USD rates
        window: Lookback window in days
    
    Returns:
        Dictionary with currency risk assessment
    """
    if len(eurusd_df) < window:
        window = len(eurusd_df)
    
    recent_rate = eurusd_df['close'].iloc[-1]
    past_rate = eurusd_df['close'].iloc[-window]
    
    recent_change = ((recent_rate - past_rate) / past_rate) * 100
    
    # Determine trend and risk
    if recent_change < -2:  # Dollar strengthening (EUR/USD decreasing)
        trend = 'strengthening'
        risk_level = 'low'  # Good for EUR investors in USD assets
        impact = 'positive'
    elif recent_change > 2:  # Dollar weakening (EUR/USD increasing)
        trend = 'weakening'
        if recent_change > 5:
            risk_level = 'high'  # Significant drag on returns
            impact = 'very_negative'
        else:
            risk_level = 'moderate'
            impact = 'negative'
    else:
        trend = 'stable'
        risk_level = 'low'
        impact = 'neutral'
    
    return {
        'trend': trend,
        'change_pct': recent_change,
        'risk_level': risk_level,
        'impact': impact,
        'current_rate': recent_rate,
        'window_days': window
    }
