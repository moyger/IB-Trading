"""
Market Regime Detection for Bybit Strategy
Identifies favorable vs unfavorable trading conditions
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from enum import Enum

class MarketRegime(Enum):
    """Market regime classifications"""
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"  
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    WHIPSAW = "whipsaw"
    BREAKOUT = "breakout"

class MarketRegimeDetector:
    """
    Detects market regimes to filter trading conditions
    """
    
    def __init__(self, lookback_periods: int = 50):
        self.lookback_periods = lookback_periods
        
        # Regime thresholds
        self.adx_trend_threshold = 25  # Above = trending
        self.adx_strong_threshold = 40  # Above = strong trend
        self.bb_squeeze_threshold = 0.10  # Below = low volatility
        self.atr_percentile_high = 0.8  # Above = high volatility
        self.atr_percentile_low = 0.2   # Below = low volatility
        self.whipsaw_threshold = 3      # Reversals in N periods
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                     period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (trend strength)
        Key indicator for trend vs range detection
        """
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Directional Movement
        dm_plus = np.where((high - high.shift()) > (low.shift() - low), 
                          np.maximum(high - high.shift(), 0), 0)
        dm_minus = np.where((low.shift() - low) > (high - high.shift()), 
                           np.maximum(low.shift() - low, 0), 0)
        
        # Smooth with Wilder's smoothing
        tr_smooth = tr.ewm(alpha=1/period, adjust=False).mean()
        dm_plus_smooth = pd.Series(dm_plus, index=close.index).ewm(alpha=1/period, adjust=False).mean()
        dm_minus_smooth = pd.Series(dm_minus, index=close.index).ewm(alpha=1/period, adjust=False).mean()
        
        # Directional Indicators
        di_plus = 100 * dm_plus_smooth / tr_smooth
        di_minus = 100 * dm_minus_smooth / tr_smooth
        
        # ADX calculation
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()
        
        return adx
    
    def calculate_bollinger_squeeze(self, close: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Bollinger Band squeeze (volatility measure)
        Low values = low volatility (ranging markets)
        """
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        bb_squeeze = (2 * std) / sma
        return bb_squeeze
    
    def calculate_atr_percentile(self, high: pd.Series, low: pd.Series, 
                                close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate ATR percentile over lookback period
        High percentile = high volatility period
        """
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR
        atr = tr.rolling(window=period).mean()
        
        # Calculate percentile rank over lookback period
        atr_percentile = atr.rolling(window=self.lookback_periods).rank() / self.lookback_periods
        
        return atr_percentile
    
    def detect_whipsaw(self, close: pd.Series, ema_fast: pd.Series, 
                      lookback: int = 10) -> pd.Series:
        """
        Detect whipsaw conditions (frequent trend changes)
        High values = choppy/whipsaw market
        """
        # Detect when price crosses EMA
        above_ema = close > ema_fast
        crosses = above_ema.astype(int).diff().abs()
        
        # Count crosses in lookback period
        whipsaw_count = crosses.rolling(window=lookback).sum()
        
        return whipsaw_count
    
    def calculate_trend_consistency(self, close: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate trend consistency over period
        High values = consistent trend, Low values = choppy
        """
        returns = close.pct_change()
        
        # Rolling correlation with linear trend
        x = np.arange(period)
        
        def rolling_trend_r2(window):
            if len(window) < period:
                return 0
            y = window.values
            correlation = np.corrcoef(x, y)[0, 1]
            return correlation ** 2 if not np.isnan(correlation) else 0
        
        trend_r2 = returns.rolling(window=period).apply(rolling_trend_r2, raw=False)
        return trend_r2
    
    def detect_market_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main function to detect market regime
        Returns DataFrame with regime classifications
        """
        # Calculate regime indicators
        df['adx'] = self.calculate_adx(df['High'], df['Low'], df['Close'])
        df['bb_squeeze'] = self.calculate_bollinger_squeeze(df['Close'])
        df['atr_percentile'] = self.calculate_atr_percentile(df['High'], df['Low'], df['Close'])
        
        # Calculate EMAs for whipsaw detection
        df['ema_12'] = df['Close'].ewm(span=12).mean()
        df['whipsaw_count'] = self.detect_whipsaw(df['Close'], df['ema_12'])
        
        # Trend consistency
        df['trend_consistency'] = self.calculate_trend_consistency(df['Close'])
        
        # Price momentum
        df['momentum_20'] = df['Close'].pct_change(20) * 100
        
        # Classify regimes
        df['market_regime'] = self.classify_regime(df)
        df['trade_favorable'] = self.is_trade_favorable(df)
        
        return df
    
    def classify_regime(self, df: pd.DataFrame) -> pd.Series:
        """
        Classify market regime based on indicators
        """
        regimes = []
        
        for i in range(len(df)):
            adx = df['adx'].iloc[i] if not pd.isna(df['adx'].iloc[i]) else 0
            bb_squeeze = df['bb_squeeze'].iloc[i] if not pd.isna(df['bb_squeeze'].iloc[i]) else 0.05
            atr_percentile = df['atr_percentile'].iloc[i] if not pd.isna(df['atr_percentile'].iloc[i]) else 0.5
            whipsaw = df['whipsaw_count'].iloc[i] if not pd.isna(df['whipsaw_count'].iloc[i]) else 0
            momentum = df['momentum_20'].iloc[i] if not pd.isna(df['momentum_20'].iloc[i]) else 0
            trend_consistency = df['trend_consistency'].iloc[i] if not pd.isna(df['trend_consistency'].iloc[i]) else 0
            
            # High volatility regime
            if atr_percentile > self.atr_percentile_high:
                regime = MarketRegime.HIGH_VOLATILITY.value
                
            # Low volatility / ranging regime  
            elif bb_squeeze < self.bb_squeeze_threshold or atr_percentile < self.atr_percentile_low:
                regime = MarketRegime.LOW_VOLATILITY.value
                
            # Whipsaw regime (frequent reversals)
            elif whipsaw >= self.whipsaw_threshold:
                regime = MarketRegime.WHIPSAW.value
                
            # Strong trending regimes
            elif adx > self.adx_strong_threshold and trend_consistency > 0.3:
                if momentum > 5:
                    regime = MarketRegime.TRENDING_BULL.value
                elif momentum < -5:
                    regime = MarketRegime.TRENDING_BEAR.value
                else:
                    regime = MarketRegime.RANGING.value
                    
            # Weak trend / ranging
            elif adx < self.adx_trend_threshold:
                regime = MarketRegime.RANGING.value
                
            # Breakout conditions
            elif (atr_percentile > 0.7 and bb_squeeze > 0.08 and 
                  trend_consistency > 0.4 and abs(momentum) > 3):
                regime = MarketRegime.BREAKOUT.value
                
            # Default to ranging
            else:
                regime = MarketRegime.RANGING.value
                
            regimes.append(regime)
        
        return pd.Series(regimes, index=df.index)
    
    def is_trade_favorable(self, df: pd.DataFrame) -> pd.Series:
        """
        Determine if conditions are favorable for trend following
        """
        favorable_regimes = {
            MarketRegime.TRENDING_BULL.value,
            MarketRegime.TRENDING_BEAR.value,
            MarketRegime.BREAKOUT.value
        }
        
        unfavorable_regimes = {
            MarketRegime.RANGING.value,
            MarketRegime.HIGH_VOLATILITY.value,
            MarketRegime.LOW_VOLATILITY.value,
            MarketRegime.WHIPSAW.value
        }
        
        trade_favorable = []
        
        for i in range(len(df)):
            regime = df['market_regime'].iloc[i]
            adx = df['adx'].iloc[i] if not pd.isna(df['adx'].iloc[i]) else 0
            trend_consistency = df['trend_consistency'].iloc[i] if not pd.isna(df['trend_consistency'].iloc[i]) else 0
            
            # Base decision on regime
            if regime in favorable_regimes:
                favorable = True
            elif regime in unfavorable_regimes:
                favorable = False
            else:
                favorable = False
            
            # Additional filters
            if favorable:
                # Require minimum trend strength
                if adx < 20:
                    favorable = False
                # Require trend consistency
                if trend_consistency < 0.2:
                    favorable = False
            
            trade_favorable.append(favorable)
        
        return pd.Series(trade_favorable, index=df.index)
    
    def get_regime_stats(self, df: pd.DataFrame) -> Dict:
        """
        Get statistics about regime distribution
        """
        if 'market_regime' not in df.columns:
            df = self.detect_market_regime(df)
        
        regime_counts = df['market_regime'].value_counts()
        total_periods = len(df)
        
        stats = {}
        for regime, count in regime_counts.items():
            percentage = (count / total_periods) * 100
            stats[regime] = {
                'count': count,
                'percentage': percentage
            }
        
        # Trading favorability
        favorable_periods = df['trade_favorable'].sum()
        stats['trading_favorable'] = {
            'count': favorable_periods,
            'percentage': (favorable_periods / total_periods) * 100
        }
        
        return stats

# Example usage functions
def analyze_symbol_regimes(df: pd.DataFrame, symbol: str) -> None:
    """
    Analyze and print regime statistics for a symbol
    """
    detector = MarketRegimeDetector()
    df_with_regimes = detector.detect_market_regime(df.copy())
    stats = detector.get_regime_stats(df_with_regimes)
    
    print(f"\n📊 {symbol} REGIME ANALYSIS")
    print("-" * 50)
    for regime, data in stats.items():
        if regime != 'trading_favorable':
            print(f"{regime.replace('_', ' ').title()}: {data['count']} periods ({data['percentage']:.1f}%)")
    
    print(f"\n🎯 Trading Favorable: {stats['trading_favorable']['count']} periods ({stats['trading_favorable']['percentage']:.1f}%)")
    
    return df_with_regimes

def create_regime_filter(df: pd.DataFrame) -> pd.Series:
    """
    Create a boolean filter for favorable trading conditions
    """
    detector = MarketRegimeDetector()
    df_with_regimes = detector.detect_market_regime(df.copy())
    
    return df_with_regimes['trade_favorable']