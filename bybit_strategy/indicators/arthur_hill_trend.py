"""
Arthur Hill's Trend Composite Implementation
Based on StockCharts TIP (Trend Investor Pro) methodology
Adapted for 4H crypto timeframe
"""

import pandas as pd
import numpy as np
from typing import Tuple

class ArthurHillTrendComposite:
    """
    Arthur Hill's 5-Indicator Trend Composite
    Exactly as specified in StockCharts TIP documentation
    """
    
    def __init__(self, timeframe_multiplier: int = 1):
        """
        Initialize with timeframe multiplier for 4H adaptation
        timeframe_multiplier: 1 for daily, adjust for other timeframes
        """
        
        # Base period (125 for daily, adapt for 4H)
        base_period = int(125 / (6 * timeframe_multiplier))  # 125 daily ≈ 21 for 4H
        base_period = max(base_period, 20)  # Minimum 20 periods
        
        # Arthur Hill's 5 indicators with adapted periods
        self.ma_period = base_period          # 125-day SMA → 21 for 4H
        self.roc_period = max(5 // timeframe_multiplier, 2)  # 5-day ROC → 2 for 4H
        self.cci_period = base_period         # 125-period CCI
        self.bb_period = base_period          # 125-day Bollinger
        self.bb_std = 1.0                     # 1 standard deviation
        self.kc_period = base_period          # 125-day Keltner
        self.kc_atr_mult = 2.0               # 2 ATR
        self.stoch_period = base_period       # 125-day Stochastic
        self.stoch_smooth = max(5 // timeframe_multiplier, 2)  # 5-day smoothing
        
        print(f"📊 Arthur Hill Trend Composite Parameters:")
        print(f"   Base Period: {base_period}")
        print(f"   MA/CCI/BB/KC Period: {self.ma_period}")
        print(f"   ROC Period: {self.roc_period}")
        print(f"   Stoch Smoothing: {self.stoch_smooth}")
    
    def calculate_tip_moving_average_trend(self, close: pd.Series) -> pd.Series:
        """
        TIP Moving Average Trend: 125-day SMA with 5-period ROC
        Signal: +1 when ROC > 0, -1 when ROC < 0
        """
        sma = close.rolling(window=self.ma_period).mean()
        roc = ((sma / sma.shift(self.roc_period)) - 1) * 100
        
        signal = pd.Series(0, index=close.index)
        signal[roc > 0] = 1
        signal[roc < 0] = -1
        
        return signal
    
    def calculate_tip_cci_close(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        TIP CCI Close: 125-period Commodity Channel Index
        Signal: +1 when CCI > +100, -1 when CCI < -100
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=self.cci_period).mean()
        
        # Calculate mean deviation
        mad = typical_price.rolling(window=self.cci_period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
        )
        
        # CCI calculation
        cci = (typical_price - sma_tp) / (0.015 * mad)
        
        signal = pd.Series(0, index=close.index)
        signal[cci > 100] = 1
        signal[cci < -100] = -1
        
        return signal
    
    def calculate_bollinger_bands_signal(self, close: pd.Series) -> pd.Series:
        """
        Bollinger Bands: 125-day, 1 standard deviation
        Signal: +1 when close above upper band, -1 when close below lower band
        """
        sma = close.rolling(window=self.bb_period).mean()
        std = close.rolling(window=self.bb_period).std()
        
        upper_band = sma + (std * self.bb_std)
        lower_band = sma - (std * self.bb_std)
        
        signal = pd.Series(0, index=close.index)
        signal[close > upper_band] = 1
        signal[close < lower_band] = -1
        
        return signal
    
    def calculate_keltner_channels_signal(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        Keltner Channels: 125-day, 2 ATR
        Signal: +1 when close above upper channel, -1 when close below lower channel
        """
        sma = close.rolling(window=self.kc_period).mean()
        
        # True Range for ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.kc_period).mean()
        
        upper_channel = sma + (atr * self.kc_atr_mult)
        lower_channel = sma - (atr * self.kc_atr_mult)
        
        signal = pd.Series(0, index=close.index)
        signal[close > upper_channel] = 1
        signal[close < lower_channel] = -1
        
        return signal
    
    def calculate_tip_stoch_close(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        TIP StochClose: 125-day stochastic with 5-day smoothing
        Signal: +1 when smoothed stoch > 60, -1 when smoothed stoch < 40
        """
        # Calculate %K over the period
        highest_high = high.rolling(window=self.stoch_period).max()
        lowest_low = low.rolling(window=self.stoch_period).min()
        
        k_percent = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Smooth %K
        k_smooth = k_percent.rolling(window=self.stoch_smooth).mean()
        
        signal = pd.Series(0, index=close.index)
        signal[k_smooth > 60] = 1
        signal[k_smooth < 40] = -1
        
        return signal
    
    def calculate_arthur_hill_composite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Arthur Hill's 5-Indicator Trend Composite
        Returns DataFrame with individual signals and composite score
        """
        high = df['High']
        low = df['Low'] 
        close = df['Close']
        
        print("📊 Calculating Arthur Hill Trend Composite...")
        
        # Calculate all 5 indicators
        df['tip_ma_trend'] = self.calculate_tip_moving_average_trend(close)
        df['tip_cci_signal'] = self.calculate_tip_cci_close(high, low, close)
        df['bb_signal'] = self.calculate_bollinger_bands_signal(close)
        df['kc_signal'] = self.calculate_keltner_channels_signal(high, low, close)
        df['tip_stoch_signal'] = self.calculate_tip_stoch_close(high, low, close)
        
        # Arthur Hill's Composite Score (-5 to +5)
        df['arthur_hill_composite'] = (
            df['tip_ma_trend'] + 
            df['tip_cci_signal'] + 
            df['bb_signal'] + 
            df['kc_signal'] + 
            df['tip_stoch_signal']
        )
        
        # Generate trading signals
        df['ah_trend_direction'] = 'NEUTRAL'
        df['ah_trend_direction'][df['arthur_hill_composite'] >= 3] = 'LONG'   # 3+ indicators bullish
        df['ah_trend_direction'][df['arthur_hill_composite'] <= -3] = 'SHORT'  # 3+ indicators bearish
        
        # Signal strength
        df['ah_signal_strength'] = abs(df['arthur_hill_composite'])
        
        # Calculate ATR for stops
        tr1 = df['High'] - df['Low']
        tr2 = abs(df['High'] - df['Close'].shift())
        tr3 = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        print("✅ Arthur Hill Trend Composite calculated")
        print(f"📊 Signal distribution:")
        print(df['ah_trend_direction'].value_counts())
        
        return df
    
    def get_signal_summary(self, df: pd.DataFrame) -> dict:
        """Get summary of signals generated"""
        
        if 'arthur_hill_composite' not in df.columns:
            return {}
        
        total_periods = len(df)
        long_signals = (df['ah_trend_direction'] == 'LONG').sum()
        short_signals = (df['ah_trend_direction'] == 'SHORT').sum()
        neutral_signals = (df['ah_trend_direction'] == 'NEUTRAL').sum()
        
        # Composite score distribution
        score_dist = df['arthur_hill_composite'].value_counts().sort_index()
        
        return {
            'total_periods': total_periods,
            'long_signals': long_signals,
            'short_signals': short_signals, 
            'neutral_signals': neutral_signals,
            'long_percentage': (long_signals / total_periods) * 100,
            'short_percentage': (short_signals / total_periods) * 100,
            'neutral_percentage': (neutral_signals / total_periods) * 100,
            'score_distribution': score_dist.to_dict(),
            'max_score': df['arthur_hill_composite'].max(),
            'min_score': df['arthur_hill_composite'].min(),
            'avg_signal_strength': df['ah_signal_strength'].mean()
        }