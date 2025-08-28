"""
Bitcoin FTMO Strategy

Advanced Bitcoin trading strategy with FTMO compliance.
Adapted from proven XAUUSD FTMO strategy for crypto markets.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from ..core.universal_strategy import UniversalStrategy, StrategyConfig, AssetType, RiskProfile


class BitcoinFTMOStrategy(UniversalStrategy):
    """
    FTMO-compliant Bitcoin trading strategy.
    
    Features:
    - Multi-confluence analysis
    - Strict risk management
    - Volatility-adaptive position sizing
    - Monthly performance tracking
    """
    
    def __init__(self, config: StrategyConfig):
        """Initialize Bitcoin FTMO strategy"""
        super().__init__(config)
        
        # Strategy parameters
        self.ema_periods = config.params.get('ema_periods', [8, 21, 50, 100, 200])
        self.rsi_periods = config.params.get('rsi_periods', [14, 21])
        self.macd_config = config.params.get('macd_config', [12, 26, 9])
        self.adx_period = config.params.get('adx_period', 14)
        self.bb_period = config.params.get('bb_period', 20)
        self.bb_std = config.params.get('bb_std', 2)
        self.volume_period = config.params.get('volume_period', 20)
        
        # Confluence thresholds
        self.min_confluence = config.params.get('min_confluence', 4)
        self.strong_confluence = config.params.get('strong_confluence', 6)
        
        # Risk management (FTMO compliant)
        self.volatility_multiplier = config.params.get('volatility_multiplier', 10)
        self.buffer_factor = config.params.get('buffer_factor', 0.8)  # Use 80% of allowed risk
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        indicators = pd.DataFrame(index=data.index)
        
        # EMAs
        for period in self.ema_periods:
            indicators[f'EMA_{period}'] = data['Close'].ewm(span=period).mean()
        
        # RSI indicators
        for period in self.rsi_periods:
            indicators[f'RSI_{period}'] = self._calculate_rsi(data['Close'], period)
        
        # MACD
        macd_line, macd_signal, macd_histogram = self._calculate_macd(
            data['Close'], *self.macd_config
        )
        indicators['MACD'] = macd_line
        indicators['MACD_Signal'] = macd_signal
        indicators['MACD_Histogram'] = macd_histogram
        
        # ADX (Average Directional Index)
        indicators['ADX'] = self._calculate_adx(data, self.adx_period)
        
        # Bollinger Bands
        bb_middle, bb_upper, bb_lower = self._calculate_bollinger_bands(
            data['Close'], self.bb_period, self.bb_std
        )
        indicators['BB_Middle'] = bb_middle
        indicators['BB_Upper'] = bb_upper
        indicators['BB_Lower'] = bb_lower
        
        # Volume analysis
        indicators['Volume_MA'] = data['Volume'].rolling(self.volume_period).mean()
        indicators['Volume_Ratio'] = data['Volume'] / indicators['Volume_MA']
        
        # ATR for position sizing
        indicators['ATR'] = self._calculate_atr(data)
        
        return indicators
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals with confluence analysis"""
        signals = pd.DataFrame(index=data.index)
        signals['entries'] = False
        signals['exits'] = False
        signals['size'] = 0.0
        
        # Check minimum data requirement
        min_data_needed = max(self.ema_periods + [self.bb_period, self.volume_period])
        if len(data) < min_data_needed:
            return signals
        
        # Calculate confluence scores
        long_confluence = self._calculate_long_confluence(data)
        short_confluence = self._calculate_short_confluence(data)
        
        # Entry signals (require minimum confluence)
        long_entries = long_confluence >= self.min_confluence
        short_entries = short_confluence >= self.min_confluence
        
        # Exit conditions
        exits = self._calculate_exit_conditions(data)
        
        # Position sizing based on confluence strength and volatility
        position_sizes = self._calculate_adaptive_position_size(data, long_confluence, short_confluence)
        
        # Apply signals
        signals.loc[long_entries, 'entries'] = True
        signals.loc[short_entries, 'entries'] = True  # Would need short support in VectorBT
        signals.loc[exits, 'exits'] = True
        
        # Position sizes (for long entries only in this implementation)
        signals.loc[long_entries, 'size'] = position_sizes[long_entries]
        
        return signals
    
    def _calculate_long_confluence(self, data: pd.DataFrame) -> pd.Series:
        """Calculate confluence score for long signals"""
        confluence = pd.Series(0, index=data.index)
        
        # EMA alignment (bullish when shorter EMAs > longer EMAs)
        if all(f'EMA_{p}' in data.columns for p in self.ema_periods[:4]):
            ema_bullish = (
                (data['EMA_8'] > data['EMA_21']) &
                (data['EMA_21'] > data['EMA_50']) &
                (data['EMA_50'] > data['EMA_100'])
            )
            confluence += ema_bullish.astype(int) * 2  # Strong signal
        
        # RSI conditions (not oversold, but not overbought)
        if 'RSI_14' in data.columns:
            rsi_favorable = (data['RSI_14'] > 40) & (data['RSI_14'] < 70)
            confluence += rsi_favorable.astype(int)
        
        # MACD bullish
        if 'MACD' in data.columns and 'MACD_Signal' in data.columns:
            macd_bullish = data['MACD'] > data['MACD_Signal']
            confluence += macd_bullish.astype(int)
        
        # ADX trend strength
        if 'ADX' in data.columns:
            strong_trend = data['ADX'] > 25
            confluence += strong_trend.astype(int)
        
        # Price above EMA_21
        if 'EMA_21' in data.columns:
            price_above_ema = data['Close'] > data['EMA_21']
            confluence += price_above_ema.astype(int)
        
        # Volume confirmation
        if 'Volume_Ratio' in data.columns:
            volume_support = data['Volume_Ratio'] > 1.2  # Above average volume
            confluence += volume_support.astype(int)
        
        # Bollinger Band position (not extreme)
        if all(col in data.columns for col in ['BB_Upper', 'BB_Lower']):
            bb_position = (data['Close'] - data['BB_Lower']) / (data['BB_Upper'] - data['BB_Lower'])
            bb_favorable = (bb_position > 0.2) & (bb_position < 0.8)
            confluence += bb_favorable.astype(int)
        
        return confluence
    
    def _calculate_short_confluence(self, data: pd.DataFrame) -> pd.Series:
        """Calculate confluence score for short signals"""
        # Mirror of long confluence with opposite conditions
        confluence = pd.Series(0, index=data.index)
        
        # EMA alignment (bearish when shorter EMAs < longer EMAs)
        if all(f'EMA_{p}' in data.columns for p in self.ema_periods[:4]):
            ema_bearish = (
                (data['EMA_8'] < data['EMA_21']) &
                (data['EMA_21'] < data['EMA_50']) &
                (data['EMA_50'] < data['EMA_100'])
            )
            confluence += ema_bearish.astype(int) * 2
        
        # RSI conditions (not oversold, but potentially overbought)
        if 'RSI_14' in data.columns:
            rsi_favorable = (data['RSI_14'] > 30) & (data['RSI_14'] < 60)
            confluence += rsi_favorable.astype(int)
        
        # MACD bearish
        if 'MACD' in data.columns and 'MACD_Signal' in data.columns:
            macd_bearish = data['MACD'] < data['MACD_Signal']
            confluence += macd_bearish.astype(int)
        
        # Other conditions...
        return confluence
    
    def _calculate_exit_conditions(self, data: pd.DataFrame) -> pd.Series:
        """Calculate exit conditions"""
        exits = pd.Series(False, index=data.index)
        
        # MA cross exit
        if 'MA_Fast' in data.columns and 'MA_Slow' in data.columns:
            ma_exit = (data['MA_Fast'] < data['MA_Slow']) & (data['MA_Fast'].shift(1) >= data['MA_Slow'].shift(1))
            exits |= ma_exit
        
        # RSI extreme exit
        if 'RSI_14' in data.columns:
            rsi_exit = data['RSI_14'] < self.rsi_oversold
            exits |= rsi_exit
        
        return exits
    
    def _calculate_adaptive_position_size(self, data: pd.DataFrame, 
                                        long_confluence: pd.Series,
                                        short_confluence: pd.Series) -> pd.Series:
        """Calculate position size based on confluence and volatility"""
        base_size = self.config.risk_per_trade
        position_sizes = pd.Series(base_size, index=data.index)
        
        # Confluence adjustment (higher confluence = larger position)
        max_confluence = max(self.strong_confluence, self.min_confluence)
        confluence_factor = np.maximum(long_confluence, short_confluence) / max_confluence
        confluence_factor = np.clip(confluence_factor, 0.5, 1.5)
        
        position_sizes *= confluence_factor
        
        # Volatility adjustment
        if 'ATR' in data.columns:
            volatility = data['ATR'] / data['Close']
            volatility_factor = 1.0 / (1.0 + volatility * self.volatility_multiplier)
            position_sizes *= volatility_factor
        
        # Apply FTMO buffer
        position_sizes *= self.buffer_factor
        
        # Clip to maximum position size
        position_sizes = position_sizes.clip(0, self.config.max_position_size)
        
        return position_sizes
    
    def _calculate_macd(self, close: pd.Series, fast: int = 12, 
                       slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD indicator"""
        ema_fast = close.ewm(span=fast).mean()
        ema_slow = close.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        
        return macd_line, macd_signal, macd_histogram
    
    def _calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # True Range
        tr = pd.concat([
            high - low,
            abs(high - close.shift(1)),
            abs(low - close.shift(1))
        ], axis=1).max(axis=1)
        
        # Directional Movement
        dm_plus = np.where((high.diff() > low.diff().abs()) & (high.diff() > 0), high.diff(), 0)
        dm_minus = np.where((low.diff().abs() > high.diff()) & (low.diff() < 0), low.diff().abs(), 0)
        
        # Smooth the values
        tr_smooth = pd.Series(tr).rolling(period).mean()
        dm_plus_smooth = pd.Series(dm_plus).rolling(period).mean()
        dm_minus_smooth = pd.Series(dm_minus).rolling(period).mean()
        
        # Calculate DI+ and DI-
        di_plus = 100 * dm_plus_smooth / tr_smooth
        di_minus = 100 * dm_minus_smooth / tr_smooth
        
        # Calculate DX and ADX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(period).mean()
        
        return adx
    
    def _calculate_bollinger_bands(self, close: pd.Series, period: int = 20, 
                                  std_dev: float = 2) -> tuple:
        """Calculate Bollinger Bands"""
        middle = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return middle, upper, lower


def create_bitcoin_ftmo_strategy(risk_profile: str = 'conservative',
                                ftmo_phase: str = 'challenge') -> BitcoinFTMOStrategy:
    """
    Factory function for Bitcoin FTMO strategy.
    
    Args:
        risk_profile: Risk profile level
        ftmo_phase: FTMO challenge phase
        
    Returns:
        Configured BitcoinFTMOStrategy
    """
    from ..core.universal_strategy import RiskProfile
    
    risk_map = {
        'conservative': RiskProfile.CONSERVATIVE,
        'moderate': RiskProfile.MODERATE, 
        'aggressive': RiskProfile.AGGRESSIVE
    }
    
    config = StrategyConfig(
        name=f"Bitcoin_FTMO_{ftmo_phase}",
        asset_type=AssetType.CRYPTO,
        risk_profile=risk_map.get(risk_profile, RiskProfile.CONSERVATIVE),
        ftmo_compliant=True,
        params={
            'ema_periods': [8, 21, 50, 100, 200],
            'rsi_periods': [14, 21],
            'macd_config': [12, 26, 9],
            'adx_period': 14,
            'bb_period': 20,
            'bb_std': 2,
            'volume_period': 20,
            'min_confluence': 4,
            'strong_confluence': 6,
            'volatility_multiplier': 10,
            'buffer_factor': 0.8,
            'ftmo_phase': ftmo_phase
        }
    )
    
    return BitcoinFTMOStrategy(config)