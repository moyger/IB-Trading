#!/usr/bin/env python3
"""
Arthur Hill's Trend Composite Indicator
Based on TIP (Trend Investor Pro) methodology from StockCharts

Components:
1. TIP Moving Average Trend
2. TIP CCI Close  
3. Bollinger Bands
4. Keltner Channels
5. TIP StochClose

Range: -5 to +5 (odd numbers only)
Each component contributes +1 (bullish) or -1 (bearish)
"""

import pandas as pd
import numpy as np
from typing import Tuple

class ArthurHillTrendComposite:
    """
    Arthur Hill's Trend Composite Indicator Implementation
    Combines 5 technical indicators for robust trend detection
    """
    
    def __init__(self, 
                 ma_period: int = 50,
                 cci_period: int = 20,
                 bb_period: int = 20,
                 bb_std: float = 2.0,
                 keltner_period: int = 20,
                 keltner_multiplier: float = 2.0,
                 stoch_k_period: int = 14,
                 stoch_d_period: int = 3):
        """
        Initialize Arthur Hill Trend Composite
        
        Args:
            ma_period: Moving average period for trend component
            cci_period: CCI calculation period
            bb_period: Bollinger Bands period
            bb_std: Bollinger Bands standard deviation multiplier
            keltner_period: Keltner Channels period
            keltner_multiplier: Keltner Channels ATR multiplier
            stoch_k_period: Stochastic %K period
            stoch_d_period: Stochastic %D period
        """
        self.ma_period = ma_period
        self.cci_period = cci_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.keltner_period = keltner_period
        self.keltner_multiplier = keltner_multiplier
        self.stoch_k_period = stoch_k_period
        self.stoch_d_period = stoch_d_period
        
    def calculate_component_1_ma_trend(self, df: pd.DataFrame) -> pd.Series:
        """
        Component 1: TIP Moving Average Trend
        Compares price to moving average
        """
        ma = df['Close'].rolling(window=self.ma_period).mean()
        
        # Simple trend: price above MA = +1, below = -1
        trend_signal = np.where(df['Close'] > ma, 1, -1)
        
        return pd.Series(trend_signal, index=df.index, name='MA_Trend')
    
    def calculate_component_2_cci_close(self, df: pd.DataFrame) -> pd.Series:
        """
        Component 2: TIP CCI Close
        Commodity Channel Index based trend signal
        """
        # Calculate CCI
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        ma_tp = typical_price.rolling(window=self.cci_period).mean()
        mean_deviation = typical_price.rolling(window=self.cci_period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )
        cci = (typical_price - ma_tp) / (0.015 * mean_deviation)
        
        # TIP CCI Close signal: CCI > 0 = +1, CCI < 0 = -1
        cci_signal = np.where(cci > 0, 1, -1)
        
        return pd.Series(cci_signal, index=df.index, name='CCI_Close')
    
    def calculate_component_3_bollinger_bands(self, df: pd.DataFrame) -> pd.Series:
        """
        Component 3: Bollinger Bands
        Position relative to bands determines signal
        """
        # Calculate Bollinger Bands
        ma = df['Close'].rolling(window=self.bb_period).mean()
        std = df['Close'].rolling(window=self.bb_period).std()
        upper_band = ma + (std * self.bb_std)
        lower_band = ma - (std * self.bb_std)
        
        # Signal logic: Price above middle = +1, below = -1
        # This captures the trend component of Bollinger Bands
        bb_signal = np.where(df['Close'] > ma, 1, -1)
        
        return pd.Series(bb_signal, index=df.index, name='BB_Trend')
    
    def calculate_component_4_keltner_channels(self, df: pd.DataFrame) -> pd.Series:
        """
        Component 4: Keltner Channels  
        Position relative to channels determines signal
        """
        # Calculate ATR for Keltner Channels
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=self.keltner_period).mean()
        
        # Keltner Channels
        ma = df['Close'].rolling(window=self.keltner_period).mean()
        upper_channel = ma + (atr * self.keltner_multiplier)
        lower_channel = ma - (atr * self.keltner_multiplier)
        
        # Signal logic: Price above middle = +1, below = -1
        keltner_signal = np.where(df['Close'] > ma, 1, -1)
        
        return pd.Series(keltner_signal, index=df.index, name='Keltner_Trend')
    
    def calculate_component_5_stoch_close(self, df: pd.DataFrame) -> pd.Series:
        """
        Component 5: TIP StochClose
        Stochastic oscillator trend signal
        """
        # Calculate Stochastic
        lowest_low = df['Low'].rolling(window=self.stoch_k_period).min()
        highest_high = df['High'].rolling(window=self.stoch_k_period).max()
        
        k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=self.stoch_d_period).mean()
        
        # TIP StochClose signal: %D > 50 = +1, %D < 50 = -1
        # This captures the trend component of stochastic
        stoch_signal = np.where(d_percent > 50, 1, -1)
        
        return pd.Series(stoch_signal, index=df.index, name='Stoch_Close')
    
    def calculate_trend_composite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Arthur Hill's Trend Composite
        
        Returns:
            DataFrame with individual components and composite score
        """
        # Calculate all 5 components
        component_1 = self.calculate_component_1_ma_trend(df)
        component_2 = self.calculate_component_2_cci_close(df)
        component_3 = self.calculate_component_3_bollinger_bands(df)
        component_4 = self.calculate_component_4_keltner_channels(df)
        component_5 = self.calculate_component_5_stoch_close(df)
        
        # Create results DataFrame
        result_df = pd.DataFrame(index=df.index)
        result_df['MA_Trend'] = component_1
        result_df['CCI_Close'] = component_2
        result_df['BB_Trend'] = component_3
        result_df['Keltner_Trend'] = component_4
        result_df['Stoch_Close'] = component_5
        
        # Calculate Trend Composite Score (-5 to +5)
        result_df['Trend_Composite'] = (component_1 + component_2 + component_3 + 
                                       component_4 + component_5)
        
        # Add trend strength classification
        result_df['Trend_Strength'] = result_df['Trend_Composite'].apply(self._classify_trend_strength)
        
        return result_df
    
    def _classify_trend_strength(self, score: int) -> str:
        """Classify trend strength based on composite score"""
        if score >= 4:
            return 'Very Strong Bullish'
        elif score >= 2:
            return 'Strong Bullish'
        elif score == 0:
            return 'Neutral'
        elif score >= -2:
            return 'Weak Bearish'
        elif score >= -4:
            return 'Strong Bearish'
        else:
            return 'Very Strong Bearish'
    
    def get_signal(self, trend_composite_score: int) -> Tuple[str, int]:
        """
        Get trading signal from trend composite score
        
        Args:
            trend_composite_score: Score from -5 to +5
            
        Returns:
            Tuple of (signal_name, signal_direction)
            signal_direction: 1 for long, -1 for short, 0 for neutral
        """
        if trend_composite_score >= 3:
            return 'Strong Bullish', 1
        elif trend_composite_score >= 1:
            return 'Bullish', 1
        elif trend_composite_score <= -3:
            return 'Strong Bearish', -1
        elif trend_composite_score <= -1:
            return 'Bearish', -1
        else:
            return 'Neutral', 0
    
    def get_trend_quality(self, df_with_composite: pd.DataFrame, current_idx: int, lookback: int = 10) -> dict:
        """
        Assess trend quality and consistency
        
        Args:
            df_with_composite: DataFrame with trend composite calculated
            current_idx: Current index position
            lookback: Periods to look back for consistency analysis
            
        Returns:
            Dictionary with trend quality metrics
        """
        if current_idx < lookback:
            return {'consistency': 0, 'direction_changes': 0, 'avg_strength': 0}
        
        # Get recent trend composite scores
        recent_scores = df_with_composite['Trend_Composite'].iloc[current_idx-lookback:current_idx]
        
        # Calculate consistency (how often trend stays in same direction)
        positive_periods = (recent_scores > 0).sum()
        negative_periods = (recent_scores < 0).sum()
        neutral_periods = (recent_scores == 0).sum()
        
        # Consistency is the proportion of the dominant trend
        consistency = max(positive_periods, negative_periods, neutral_periods) / lookback
        
        # Count direction changes
        direction_changes = 0
        prev_direction = 1 if recent_scores.iloc[0] > 0 else (-1 if recent_scores.iloc[0] < 0 else 0)
        
        for score in recent_scores.iloc[1:]:
            current_direction = 1 if score > 0 else (-1 if score < 0 else 0)
            if current_direction != prev_direction and prev_direction != 0 and current_direction != 0:
                direction_changes += 1
            prev_direction = current_direction
        
        # Average strength
        avg_strength = abs(recent_scores).mean()
        
        return {
            'consistency': consistency,
            'direction_changes': direction_changes,
            'avg_strength': avg_strength,
            'trend_periods': {
                'bullish': positive_periods,
                'bearish': negative_periods,
                'neutral': neutral_periods
            }
        }

def test_trend_composite():
    """Test the Arthur Hill Trend Composite indicator"""
    print("🧪 Testing Arthur Hill Trend Composite Indicator")
    print("=" * 50)
    
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='H')
    
    # Generate realistic OHLCV data with trend
    close_prices = 50000 + np.cumsum(np.random.randn(200) * 100)
    high_prices = close_prices + np.random.uniform(50, 200, 200)
    low_prices = close_prices - np.random.uniform(50, 200, 200)
    open_prices = close_prices + np.random.randn(200) * 50
    volumes = np.random.uniform(1000, 10000, 200)
    
    df = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    }, index=dates)
    
    # Initialize indicator
    indicator = ArthurHillTrendComposite()
    
    # Calculate trend composite
    result = indicator.calculate_trend_composite(df)
    
    # Show results
    print(f"📊 Trend Composite Analysis:")
    print(f"   Data points: {len(result)}")
    print(f"   Period: {result.index[0]} to {result.index[-1]}")
    
    # Show component statistics
    print(f"\n📈 Component Statistics:")
    for col in ['MA_Trend', 'CCI_Close', 'BB_Trend', 'Keltner_Trend', 'Stoch_Close']:
        bullish_count = (result[col] == 1).sum()
        bearish_count = (result[col] == -1).sum()
        print(f"   {col:15}: {bullish_count:3} bullish, {bearish_count:3} bearish")
    
    # Show composite score distribution
    print(f"\n🎯 Trend Composite Score Distribution:")
    score_counts = result['Trend_Composite'].value_counts().sort_index()
    for score, count in score_counts.items():
        strength = indicator._classify_trend_strength(score)
        print(f"   {score:2}: {count:3} periods ({strength})")
    
    # Show recent signals
    print(f"\n📋 Recent Signals (last 10 periods):")
    for i in range(max(0, len(result)-10), len(result)):
        score = result['Trend_Composite'].iloc[i]
        signal_name, signal_direction = indicator.get_signal(score)
        print(f"   {result.index[i].strftime('%m-%d %H:%M')}: Score {score:2} = {signal_name}")
    
    # Test trend quality analysis
    print(f"\n🔍 Trend Quality Analysis (last 10 periods):")
    quality = indicator.get_trend_quality(result, len(result)-1, lookback=10)
    print(f"   Consistency: {quality['consistency']:.2f}")
    print(f"   Direction Changes: {quality['direction_changes']}")
    print(f"   Average Strength: {quality['avg_strength']:.2f}")
    print(f"   Bullish Periods: {quality['trend_periods']['bullish']}")
    print(f"   Bearish Periods: {quality['trend_periods']['bearish']}")
    print(f"   Neutral Periods: {quality['trend_periods']['neutral']}")
    
    return result

if __name__ == "__main__":
    test_trend_composite()