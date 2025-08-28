"""
BTCUSDT Enhanced Strategy Adapter

Adapts the existing crypto/strategies/btcusdt_enhanced_strategy.py 
to work with the new Universal Backtesting Framework.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

# Add the crypto strategies path
crypto_path = Path(__file__).parent.parent.parent / "crypto" / "strategies"
sys.path.append(str(crypto_path))

from ..core.universal_strategy import UniversalStrategy, StrategyConfig, AssetType


class BTCUSDTEnhancedAdapter(UniversalStrategy):
    """
    Adapter for the existing BTCUSDT Enhanced Multi-Confluence Strategy.
    
    Integrates the proven confluence-based approach with the new framework
    while maintaining the original strategy logic.
    """
    
    def __init__(self, config: StrategyConfig):
        """Initialize the enhanced BTCUSDT strategy adapter"""
        super().__init__(config)
        
        # Original strategy parameters
        self.ema_periods = config.params.get('ema_periods', [8, 21, 50, 100, 200])
        self.rsi_periods = config.params.get('rsi_periods', [14, 21])
        self.macd_config = config.params.get('macd_config', [8, 21, 7])
        self.adx_period = config.params.get('adx_period', 14)
        self.bb_period = config.params.get('bb_period', 20)
        self.bb_std = config.params.get('bb_std', 2.0)
        self.volume_period = config.params.get('volume_period', 20)
        
        # Confluence thresholds
        self.min_confluence = config.params.get('min_confluence', 4)
        self.strong_confluence = config.params.get('strong_confluence', 6)
        
        # Risk profile specific settings
        if config.risk_profile.value == 'conservative':
            self.min_confluence = 5
            self.confluence_threshold = 0.8
        elif config.risk_profile.value == 'moderate':
            self.min_confluence = 4
            self.confluence_threshold = 0.7
        else:  # aggressive
            self.min_confluence = 3
            self.confluence_threshold = 0.6
        
        # Performance tracking
        self.trades_skipped_filters = {
            'no_trend': 0,
            'low_volume': 0,
            'low_volatility': 0,
            'weak_confluence': 0
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators for confluence analysis"""
        if len(data) < 100:
            return pd.DataFrame(index=data.index)
        
        indicators = pd.DataFrame(index=data.index)
        
        # Moving Averages (Multiple timeframes)
        for period in self.ema_periods:
            indicators[f'ema_{period}'] = data['Close'].ewm(span=period).mean()
        
        indicators['sma_20'] = data['Close'].rolling(window=20).mean()
        indicators['sma_50'] = data['Close'].rolling(window=50).mean()
        
        # RSI (Multiple periods for confluence)
        for period in self.rsi_periods:
            indicators[f'rsi_{period}'] = self._calculate_rsi(data['Close'], period)
        
        # MACD (Optimized for crypto)
        ema_fast, ema_slow, signal_period = self.macd_config
        indicators['ema_macd_fast'] = data['Close'].ewm(span=ema_fast).mean()
        indicators['ema_macd_slow'] = data['Close'].ewm(span=ema_slow).mean()
        indicators['macd'] = indicators['ema_macd_fast'] - indicators['ema_macd_slow']
        indicators['macd_signal'] = indicators['macd'].ewm(span=signal_period).mean()
        indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
        
        # ADX for trend strength
        indicators = pd.concat([indicators, self._calculate_adx(data)], axis=1)
        
        # Bollinger Bands
        indicators = pd.concat([indicators, self._calculate_bollinger_bands(data)], axis=1)
        
        # Volume indicators
        indicators['volume_sma'] = data['Volume'].rolling(window=self.volume_period).mean()
        indicators['volume_ratio'] = data['Volume'] / indicators['volume_sma']
        
        # ATR and volatility
        indicators['atr'] = self._calculate_atr(data)
        indicators['volatility_ratio'] = indicators['atr'] / indicators['atr'].rolling(window=24).mean()
        
        # Price patterns
        indicators = pd.concat([indicators, self._calculate_price_patterns(data)], axis=1)
        
        return indicators.fillna(0)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals with confluence analysis"""
        signals = pd.DataFrame(index=data.index)
        signals['entries'] = False
        signals['exits'] = False
        signals['size'] = 0.0
        
        if len(data) < max(self.ema_periods):
            return signals
        
        # Calculate confluence scores for each bar
        for i in range(max(self.ema_periods), len(data)):
            confluence_score, confluence_details = self._calculate_confluence_score(data, i)
            
            # Entry conditions
            if confluence_score >= self.min_confluence:
                can_enter, multiplier, reason = self._check_entry_conditions(data, i, confluence_details)
                
                if can_enter:
                    signal_direction = confluence_details.get('signal_direction', 'LONG')
                    
                    # Calculate position size based on confluence strength
                    position_size = self._calculate_confluence_position_size(
                        confluence_score, confluence_details, multiplier
                    )
                    
                    # Only long positions for now (VectorBT limitation in current setup)
                    if signal_direction == 'LONG' and position_size > 0:
                        signals.loc[data.index[i], 'entries'] = True
                        signals.loc[data.index[i], 'size'] = position_size
            
            # Exit conditions (simplified for VectorBT)
            if i > 0 and self._should_exit(data, i):
                signals.loc[data.index[i], 'exits'] = True
        
        return signals
    
    def _calculate_confluence_score(self, data: pd.DataFrame, idx: int) -> Tuple[int, Dict]:
        """Calculate multi-indicator confluence score (0-7 scale)"""
        if idx < 100:
            return 0, {}
        
        score = 0
        details = {}
        current_data = data.iloc[idx]
        
        # 1. Trend Alignment Score (0-2 points)
        trend_score = 0
        close = current_data['Close']
        ema8 = current_data.get('ema_8', close)
        ema21 = current_data.get('ema_21', close)
        ema50 = current_data.get('ema_50', close)
        ema100 = current_data.get('ema_100', close)
        
        # Perfect trend alignment
        if close > ema8 > ema21 > ema50 > ema100:
            trend_score = 2
            details['trend'] = 'Strong Bullish Alignment'
        elif close < ema8 < ema21 < ema50 < ema100:
            trend_score = -2
            details['trend'] = 'Strong Bearish Alignment'
        elif close > ema8 > ema21 > ema50:
            trend_score = 1
            details['trend'] = 'Moderate Bullish'
        elif close < ema8 < ema21 < ema50:
            trend_score = -1
            details['trend'] = 'Moderate Bearish'
        else:
            trend_score = 0
            details['trend'] = 'Mixed/Sideways'
        
        score += abs(trend_score)
        details['trend_score'] = trend_score
        
        # 2. Momentum Confluence (0-2 points)
        momentum_score = 0
        rsi14 = current_data.get('rsi_14', 50)
        rsi21 = current_data.get('rsi_21', 50)
        macd = current_data.get('macd', 0)
        macd_signal = current_data.get('macd_signal', 0)
        macd_hist = current_data.get('macd_histogram', 0)
        
        # RSI momentum
        rsi_bullish = 30 < rsi14 < 80 and 30 < rsi21 < 80 and rsi14 > rsi21
        rsi_bearish = 20 < rsi14 < 70 and 20 < rsi21 < 70 and rsi14 < rsi21
        
        # MACD momentum
        macd_bullish = macd > macd_signal and macd_hist > 0
        macd_bearish = macd < macd_signal and macd_hist < 0
        
        if (rsi_bullish and macd_bullish and trend_score > 0):
            momentum_score = 2
            details['momentum'] = 'Strong Bullish Momentum'
        elif (rsi_bearish and macd_bearish and trend_score < 0):
            momentum_score = -2
            details['momentum'] = 'Strong Bearish Momentum'
        elif (rsi_bullish or macd_bullish) and trend_score > 0:
            momentum_score = 1
            details['momentum'] = 'Moderate Bullish'
        elif (rsi_bearish or macd_bearish) and trend_score < 0:
            momentum_score = -1
            details['momentum'] = 'Moderate Bearish'
        else:
            momentum_score = 0
            details['momentum'] = 'Neutral'
        
        score += abs(momentum_score)
        details['momentum_score'] = momentum_score
        
        # 3. Market Regime Filter (0-1 points)
        regime_score = 0
        adx = current_data.get('adx', 0)
        
        if adx >= 25:
            regime_score = 1
            details['regime'] = f'Strong Trend (ADX: {adx:.1f})'
        elif adx >= 20:
            regime_score = 1
            details['regime'] = f'Moderate Trend (ADX: {adx:.1f})'
        else:
            regime_score = 0
            details['regime'] = f'No Trend (ADX: {adx:.1f})'
        
        score += regime_score
        details['regime_score'] = regime_score
        
        # 4. Volume & Volatility Confirmation (0-1 points)
        volume_vol_score = 0
        volume_ratio = current_data.get('volume_ratio', 1.0)
        volatility_ratio = current_data.get('volatility_ratio', 1.0)
        
        if volume_ratio >= 1.2 and volatility_ratio >= 1.1:
            volume_vol_score = 1
            details['volume_volatility'] = 'Strong Confirmation'
        elif volume_ratio >= 0.8 and volatility_ratio >= 0.8:
            volume_vol_score = 0.5
            details['volume_volatility'] = 'Moderate Confirmation'
        else:
            volume_vol_score = 0
            details['volume_volatility'] = 'Weak Confirmation'
        
        score += volume_vol_score
        details['volume_vol_score'] = volume_vol_score
        
        # 5. Pattern Recognition Bonus (0-1 points)
        pattern_score = 0
        bb_position = current_data.get('bb_position', 0.5)
        
        if trend_score > 0 and bb_position < 0.2:
            pattern_score = 1
            details['pattern'] = 'BB Lower Band Bounce'
        elif trend_score < 0 and bb_position > 0.8:
            pattern_score = 1
            details['pattern'] = 'BB Upper Band Rejection'
        elif current_data.get('breakout_up', False) and trend_score > 0:
            pattern_score = 1
            details['pattern'] = 'Bullish Breakout'
        elif current_data.get('breakout_down', False) and trend_score < 0:
            pattern_score = 1
            details['pattern'] = 'Bearish Breakdown'
        else:
            pattern_score = 0
            details['pattern'] = 'No Clear Pattern'
        
        score += pattern_score
        details['pattern_score'] = pattern_score
        
        # Final score adjustment
        direction_consistent = (trend_score > 0 and momentum_score > 0) or (trend_score < 0 and momentum_score < 0)
        if direction_consistent:
            final_score = min(7, int(score))
        else:
            final_score = max(0, int(score) - 1)
            details['direction_penalty'] = True
        
        details['final_score'] = final_score
        details['signal_direction'] = 'LONG' if (trend_score + momentum_score) > 0 else 'SHORT'
        
        return final_score, details
    
    def _check_entry_conditions(self, data: pd.DataFrame, idx: int, confluence_details: Dict) -> Tuple[bool, float, str]:
        """Check entry conditions with additional filters"""
        current_data = data.iloc[idx]
        
        # Volume check
        volume_ratio = current_data.get('volume_ratio', 0.0)
        if volume_ratio < 0.6:
            self.trades_skipped_filters['low_volume'] += 1
            return False, 0, "Insufficient volume"
        
        # Volatility check
        volatility_ratio = current_data.get('volatility_ratio', 0.0)
        if volatility_ratio < 0.5:
            self.trades_skipped_filters['low_volatility'] += 1
            return False, 0, "Low volatility environment"
        
        # Calculate position size multiplier based on confluence strength
        confluence_score = confluence_details['final_score']
        multiplier = min(confluence_score / 7.0, 1.0)
        
        # Bonus for perfect alignment
        if confluence_score >= 6:
            multiplier *= 1.2
        elif confluence_score >= 5:
            multiplier *= 1.1
        
        return True, multiplier, f"Confluence approved ({confluence_score}/7)"
    
    def _calculate_confluence_position_size(self, confluence_score: int, 
                                          confluence_details: Dict, multiplier: float) -> float:
        """Calculate position size based on confluence strength"""
        # Base position size from configuration
        base_size = self.config.risk_per_trade
        
        # Scale by confluence score
        confluence_factor = min(confluence_score / 7.0, 1.0)
        
        # Apply multiplier
        final_size = base_size * confluence_factor * multiplier
        
        # Apply maximum position size limit
        final_size = min(final_size, self.config.max_position_size)
        
        return final_size
    
    def _should_exit(self, data: pd.DataFrame, idx: int) -> bool:
        """Simple exit conditions (improved for VectorBT)"""
        if idx < 20:
            return False
        
        current_data = data.iloc[idx]
        prev_data = data.iloc[idx-1]
        
        # Simple EMA crossover exit
        ema8 = current_data.get('ema_8', 0)
        ema21 = current_data.get('ema_21', 0)
        prev_ema8 = prev_data.get('ema_8', 0)
        prev_ema21 = prev_data.get('ema_21', 0)
        
        # Exit when fast EMA crosses below slow EMA
        if ema8 < ema21 and prev_ema8 >= prev_ema21:
            return True
        
        # RSI extreme exit
        rsi = current_data.get('rsi_14', 50)
        if rsi < 25:  # Oversold exit
            return True
        
        return False
    
    # Helper methods from original strategy
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI with improved accuracy"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ADX with DI+ and DI- components"""
        adx_data = pd.DataFrame(index=data.index)
        
        # Calculate directional movement
        adx_data['dm_plus'] = np.where(
            (data['High'] - data['High'].shift(1)) > (data['Low'].shift(1) - data['Low']),
            np.maximum(data['High'] - data['High'].shift(1), 0), 0
        )
        adx_data['dm_minus'] = np.where(
            (data['Low'].shift(1) - data['Low']) > (data['High'] - data['High'].shift(1)),
            np.maximum(data['Low'].shift(1) - data['Low'], 0), 0
        )
        
        # Calculate True Range
        adx_data['high_low'] = data['High'] - data['Low']
        adx_data['high_close'] = abs(data['High'] - data['Close'].shift(1))
        adx_data['low_close'] = abs(data['Low'] - data['Close'].shift(1))
        adx_data['true_range'] = adx_data[['high_low', 'high_close', 'low_close']].max(axis=1)
        
        # Smooth the values
        adx_data['atr'] = adx_data['true_range'].rolling(window=period).mean()
        adx_data['di_plus'] = 100 * (adx_data['dm_plus'].rolling(window=period).mean() / adx_data['atr'])
        adx_data['di_minus'] = 100 * (adx_data['dm_minus'].rolling(window=period).mean() / adx_data['atr'])
        
        # Calculate DX and ADX
        adx_data['dx'] = 100 * abs(adx_data['di_plus'] - adx_data['di_minus']) / (adx_data['di_plus'] + adx_data['di_minus'])
        adx_data['adx'] = adx_data['dx'].rolling(window=period).mean()
        
        return adx_data[['adx', 'di_plus', 'di_minus']].fillna(0)
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift(1))
        low_close = abs(data['Low'] - data['Close'].shift(1))
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def _calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        bb_data = pd.DataFrame(index=data.index)
        bb_data['bb_middle'] = data['Close'].rolling(window=period).mean()
        bb_std = data['Close'].rolling(window=period).std()
        bb_data['bb_upper'] = bb_data['bb_middle'] + (bb_std * std_dev)
        bb_data['bb_lower'] = bb_data['bb_middle'] - (bb_std * std_dev)
        bb_data['bb_width'] = (bb_data['bb_upper'] - bb_data['bb_lower']) / bb_data['bb_middle']
        bb_data['bb_position'] = (data['Close'] - bb_data['bb_lower']) / (bb_data['bb_upper'] - bb_data['bb_lower'])
        
        return bb_data[['bb_middle', 'bb_upper', 'bb_lower', 'bb_width', 'bb_position']].fillna(0.5)
    
    def _calculate_price_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate price pattern indicators"""
        patterns = pd.DataFrame(index=data.index)
        
        # Higher highs and lower lows
        patterns['higher_high'] = (data['High'] > data['High'].shift(1)) & (data['High'].shift(1) > data['High'].shift(2))
        patterns['lower_low'] = (data['Low'] < data['Low'].shift(1)) & (data['Low'].shift(1) < data['Low'].shift(2))
        
        # Price breakouts
        patterns['breakout_up'] = data['Close'] > data['High'].rolling(window=20).max().shift(1)
        patterns['breakout_down'] = data['Close'] < data['Low'].rolling(window=20).min().shift(1)
        
        return patterns.fillna(False)


def create_btcusdt_enhanced_strategy(risk_profile: str = 'moderate',
                                   confluence_threshold: int = 4) -> BTCUSDTEnhancedAdapter:
    """
    Factory function for BTCUSDT Enhanced Strategy.
    
    Args:
        risk_profile: Risk profile level
        confluence_threshold: Minimum confluence score for entries
        
    Returns:
        Configured BTCUSDTEnhancedAdapter
    """
    from ..core.universal_strategy import RiskProfile
    
    risk_map = {
        'conservative': RiskProfile.CONSERVATIVE,
        'moderate': RiskProfile.MODERATE,
        'aggressive': RiskProfile.AGGRESSIVE
    }
    
    config = StrategyConfig(
        name=f"BTCUSDT_Enhanced_{risk_profile}",
        asset_type=AssetType.CRYPTO,
        risk_profile=risk_map.get(risk_profile, RiskProfile.MODERATE),
        params={
            'ema_periods': [8, 21, 50, 100, 200],
            'rsi_periods': [14, 21],
            'macd_config': [8, 21, 7],
            'adx_period': 14,
            'bb_period': 20,
            'bb_std': 2.0,
            'volume_period': 20,
            'min_confluence': confluence_threshold,
            'strong_confluence': 6
        }
    )
    
    return BTCUSDTEnhancedAdapter(config)