"""
Simple Moving Average Strategy

Basic strategy implementation demonstrating the Universal Framework.
Perfect for learning and as a starting template.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from ..core.universal_strategy import UniversalStrategy, StrategyConfig, AssetType


class SimpleMAStrategy(UniversalStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    Strategy Logic:
    - Long signal when fast MA crosses above slow MA
    - Exit when fast MA crosses below slow MA
    - Includes RSI filter to avoid overbought/oversold conditions
    """
    
    def __init__(self, config: StrategyConfig):
        """Initialize strategy with configuration"""
        super().__init__(config)
        
        # Default parameters
        self.fast_period = config.params.get('fast_period', 20)
        self.slow_period = config.params.get('slow_period', 50)
        self.rsi_period = config.params.get('rsi_period', 14)
        self.rsi_overbought = config.params.get('rsi_overbought', 70)
        self.rsi_oversold = config.params.get('rsi_oversold', 30)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            DataFrame with calculated indicators
        """
        indicators = pd.DataFrame(index=data.index)
        
        # Moving Averages
        indicators['MA_Fast'] = data['Close'].rolling(window=self.fast_period).mean()
        indicators['MA_Slow'] = data['Close'].rolling(window=self.slow_period).mean()
        
        # RSI calculation
        indicators['RSI'] = self._calculate_rsi(data['Close'], self.rsi_period)
        
        # ATR for position sizing
        indicators['ATR'] = self._calculate_atr(data)
        
        return indicators
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.
        
        Args:
            data: Combined OHLCV and indicators DataFrame
            
        Returns:
            DataFrame with 'entries', 'exits', and 'size' columns
        """
        signals = pd.DataFrame(index=data.index)
        
        # Initialize signals
        signals['entries'] = False
        signals['exits'] = False
        signals['size'] = 0.0
        
        # Check if we have enough data
        if len(data) < max(self.fast_period, self.slow_period):
            return signals
        
        # MA crossover signals
        ma_fast = data['MA_Fast']
        ma_slow = data['MA_Slow']
        rsi = data['RSI']
        
        # Entry conditions: Fast MA crosses above Slow MA and RSI not overbought
        ma_cross_up = (ma_fast > ma_slow) & (ma_fast.shift(1) <= ma_slow.shift(1))
        rsi_filter = rsi < self.rsi_overbought
        
        entries = ma_cross_up & rsi_filter
        
        # Exit conditions: Fast MA crosses below Slow MA or RSI oversold
        ma_cross_down = (ma_fast < ma_slow) & (ma_fast.shift(1) >= ma_slow.shift(1))
        rsi_exit = rsi < self.rsi_oversold
        
        exits = ma_cross_down | rsi_exit
        
        # Calculate position sizes based on signal strength
        signal_strength = self._calculate_signal_strength(data)
        
        # Apply signals
        signals.loc[entries, 'entries'] = True
        signals.loc[exits, 'exits'] = True
        signals.loc[entries, 'size'] = signal_strength[entries] * self.config.risk_per_trade
        
        return signals
    
    def _calculate_rsi(self, close_prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data['High']
        low = data['Low']
        close = data['Close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def _calculate_signal_strength(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate signal strength (0-1) based on multiple factors.
        
        Returns:
            Series with signal strength values
        """
        signal_strength = pd.Series(0.5, index=data.index)  # Base strength
        
        if 'RSI' in data.columns:
            # Stronger signals when RSI is in favorable range
            rsi = data['RSI']
            
            # For long signals, prefer RSI between 40-60 (not oversold, not overbought)
            rsi_strength = np.where(
                (rsi >= 40) & (rsi <= 60), 1.0,
                np.where((rsi >= 30) & (rsi <= 70), 0.8, 0.5)
            )
            
            signal_strength *= rsi_strength
        
        if 'MA_Fast' in data.columns and 'MA_Slow' in data.columns:
            # Stronger signals when MAs are clearly separated
            ma_separation = abs(data['MA_Fast'] - data['MA_Slow']) / data['Close']
            ma_strength = np.clip(ma_separation * 20, 0.5, 1.0)  # Scale factor
            signal_strength *= ma_strength
        
        return signal_strength.fillna(0.5)


def create_simple_ma_strategy(asset_type: AssetType = AssetType.CRYPTO,
                             fast_period: int = 20,
                             slow_period: int = 50,
                             risk_profile: str = 'moderate') -> SimpleMAStrategy:
    """
    Factory function to create SimpleMAStrategy with common configurations.
    
    Args:
        asset_type: Type of asset to trade
        fast_period: Fast moving average period
        slow_period: Slow moving average period
        risk_profile: Risk profile (conservative/moderate/aggressive)
        
    Returns:
        Configured SimpleMAStrategy instance
    """
    from ..core.universal_strategy import RiskProfile
    
    # Map string to enum
    risk_map = {
        'conservative': RiskProfile.CONSERVATIVE,
        'moderate': RiskProfile.MODERATE,
        'aggressive': RiskProfile.AGGRESSIVE
    }
    
    config = StrategyConfig(
        name=f"SimpleMA_{fast_period}_{slow_period}",
        asset_type=asset_type,
        risk_profile=risk_map.get(risk_profile, RiskProfile.MODERATE),
        params={
            'fast_period': fast_period,
            'slow_period': slow_period,
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30
        }
    )
    
    return SimpleMAStrategy(config)