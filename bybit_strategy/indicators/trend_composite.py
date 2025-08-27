"""
Trend Composite Indicator Module
Replicates the successful FTMO strategy with crypto optimizations
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TrendSignal:
    """Trend signal data structure"""
    score: float
    direction: str  # 'LONG', 'SHORT', or 'NEUTRAL'
    strength: str  # 'STRONG', 'MEDIUM', 'WEAK'
    components: Dict[str, float]
    confidence: float

class TrendComposite:
    """
    4H Trend Composite Calculator
    Based on FTMO strategy with 68.4% win rate, optimized for 4H timeframe
    """
    
    def __init__(self, config=None):
        """Initialize trend composite calculator"""
        if config:
            self.config = config
            # Use config settings if provided
            self.ema_periods = [config.indicators.ema_fast, config.indicators.ema_medium, config.indicators.ema_slow]
            self.rsi_period = config.indicators.rsi_period
            self.macd_fast = config.indicators.macd_fast
            self.macd_slow = config.indicators.macd_slow
            self.macd_signal = config.indicators.macd_signal
            self.min_strength = config.trading.min_trend_strength
        else:
            # 4H timeframe optimized settings (standard FTMO)
            self.ema_periods = [12, 26, 50]
            self.rsi_period = 14
            self.macd_fast = 12
            self.macd_slow = 26
            self.macd_signal = 9
            self.min_strength = 3.0
    
    def calculate_ema(self, data: pd.Series, periods: list) -> pd.DataFrame:
        """Calculate multiple EMAs"""
        ema_df = pd.DataFrame(index=data.index)
        for period in periods:
            ema_df[f'ema_{period}'] = data.ewm(span=period, adjust=False).mean()
        return ema_df
    
    def calculate_rsi(self, data: pd.Series, period: int = 10) -> pd.Series:
        """Calculate RSI indicator"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.Series, 
                      fast: int = 8, slow: int = 21, signal: int = 5) -> pd.DataFrame:
        """Calculate MACD indicator"""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })
    
    def calculate_bollinger_bands(self, data: pd.Series, 
                                  period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        return pd.DataFrame({
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev),
            'squeeze': (2 * std * std_dev) / sma  # Volatility metric
        })
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                     period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_volume_profile(self, volume: pd.Series, period: int = 20) -> pd.DataFrame:
        """Calculate volume profile indicators"""
        volume_ma = volume.rolling(window=period).mean()
        volume_std = volume.rolling(window=period).std()
        
        return pd.DataFrame({
            'volume_ma': volume_ma,
            'volume_ratio': volume / volume_ma,
            'volume_zscore': (volume - volume_ma) / volume_std
        })
    
    def calculate_momentum(self, data: pd.Series, 
                          short: int = 5, long: int = 10) -> pd.DataFrame:
        """Calculate momentum indicators"""
        return pd.DataFrame({
            'momentum_short': data.pct_change(short) * 100,
            'momentum_long': data.pct_change(long) * 100,
            'roc': (data / data.shift(long) - 1) * 100  # Rate of Change
        })
    
    def score_ema_alignment(self, df: pd.DataFrame, current_idx: int) -> Tuple[float, Dict]:
        """
        Score EMA alignment (40% weight in composite)
        Based on FTMO's successful approach
        """
        components = {}
        score = 0.0
        
        # Get current values with dynamic EMA periods
        close = df['Close'].iloc[current_idx]
        ema_fast = df[f'ema_{self.ema_periods[0]}'].iloc[current_idx]
        ema_medium = df[f'ema_{self.ema_periods[1]}'].iloc[current_idx]
        ema_slow = df[f'ema_{self.ema_periods[2]}'].iloc[current_idx]
        
        # EMA alignment scoring (0-5 scale)
        if ema_fast > ema_medium:
            score += 2.0
            components['ema_fast_medium'] = 2.0
        else:
            components['ema_fast_medium'] = -2.0
            score -= 2.0
        
        if ema_medium > ema_slow:
            score += 2.0
            components['ema_medium_slow'] = 2.0
        else:
            components['ema_medium_slow'] = -2.0
            score -= 2.0
        
        if close > ema_fast:
            score += 1.0
            components['price_ema_fast'] = 1.0
        else:
            components['price_ema_fast'] = -1.0
            score -= 1.0
        
        components['ema_total'] = score
        return score * 0.8, components  # 40% weight (0.8 * 5 = 4.0 max)
    
    def score_rsi_momentum(self, df: pd.DataFrame, current_idx: int) -> Tuple[float, Dict]:
        """
        Score RSI momentum (20% weight in composite)
        Crypto-optimized thresholds
        """
        components = {}
        score = 0.0
        
        rsi = df['rsi'].iloc[current_idx]
        rsi_prev = df['rsi'].iloc[current_idx - 1] if current_idx > 0 else rsi
        
        # RSI level scoring
        if rsi > 60:
            score += 2.0
            components['rsi_level'] = 2.0
        elif rsi > 50:
            score += 1.0
            components['rsi_level'] = 1.0
        elif rsi < 40:
            score -= 2.0
            components['rsi_level'] = -2.0
        elif rsi < 50:
            score -= 1.0
            components['rsi_level'] = -1.0
        
        # RSI momentum
        rsi_change = rsi - rsi_prev
        if abs(rsi_change) > 2:
            momentum_score = 1.0 if rsi_change > 0 else -1.0
            score += momentum_score
            components['rsi_momentum'] = momentum_score
        
        components['rsi_total'] = score
        return score * 0.4, components  # 20% weight
    
    def score_macd_signal(self, df: pd.DataFrame, current_idx: int) -> Tuple[float, Dict]:
        """
        Score MACD signal (20% weight in composite)
        """
        components = {}
        score = 0.0
        
        macd = df['macd'].iloc[current_idx]
        signal = df['macd_signal'].iloc[current_idx]
        histogram = df['macd_histogram'].iloc[current_idx]
        histogram_prev = df['macd_histogram'].iloc[current_idx - 1] if current_idx > 0 else histogram
        
        # MACD vs Signal
        if macd > signal:
            score += 2.0
            components['macd_signal'] = 2.0
        else:
            score -= 2.0
            components['macd_signal'] = -2.0
        
        # Histogram momentum
        if histogram > histogram_prev:
            score += 1.0
            components['macd_momentum'] = 1.0
        else:
            score -= 1.0
            components['macd_momentum'] = -1.0
        
        components['macd_total'] = score
        return score * 0.4, components  # 20% weight
    
    def score_volume_confirmation(self, df: pd.DataFrame, current_idx: int) -> Tuple[float, Dict]:
        """
        Score volume confirmation (10% weight)
        Important for crypto markets
        """
        components = {}
        score = 0.0
        
        volume_ratio = df['volume_ratio'].iloc[current_idx]
        
        if volume_ratio > 1.2:
            score += 2.0
            components['volume_level'] = 2.0
        elif volume_ratio > 1.0:
            score += 1.0
            components['volume_level'] = 1.0
        elif volume_ratio < 0.8:
            score -= 1.0
            components['volume_level'] = -1.0
        
        components['volume_total'] = score
        return score * 0.2, components  # 10% weight
    
    def score_momentum_filter(self, df: pd.DataFrame, current_idx: int) -> Tuple[float, Dict]:
        """
        Score price momentum (10% weight)
        Additional filter for strong moves
        """
        components = {}
        score = 0.0
        
        momentum_5 = df['momentum_5'].iloc[current_idx]
        momentum_10 = df['momentum_10'].iloc[current_idx]
        
        # Short-term momentum
        if abs(momentum_5) > 2.0:
            score += 1.5 if momentum_5 > 0 else -1.5
            components['momentum_5'] = score
        
        # Medium-term momentum
        if abs(momentum_10) > 3.0:
            score += 1.5 if momentum_10 > 0 else -1.5
            components['momentum_10'] = 1.5 if momentum_10 > 0 else -1.5
        
        components['momentum_total'] = score
        return score * 0.2, components  # 10% weight
    
    def apply_volatility_filter(self, score: float, df: pd.DataFrame, 
                               current_idx: int) -> float:
        """
        Apply volatility-based score adjustment
        Reduces signals in extreme volatility
        """
        bb_squeeze = df['bb_squeeze'].iloc[current_idx]
        squeeze_percentile = df['bb_squeeze'].rolling(50).rank().iloc[current_idx] / 50
        
        if squeeze_percentile > 0.9:  # Extreme volatility
            return score * 0.5
        elif squeeze_percentile > 0.8:  # High volatility
            return score * 0.7
        elif squeeze_percentile < 0.2:  # Low volatility
            return score * 1.2
        
        return score
    
    def calculate_composite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate full trend composite score
        Main entry point for strategy
        """
        # Calculate all indicators with dynamic periods
        ema_names = [f'ema_{period}' for period in self.ema_periods]
        ema_df = self.calculate_ema(df['Close'], self.ema_periods)
        for name, col in zip(ema_names, ema_df.columns):
            df[name] = ema_df[col]
        
        df['rsi'] = self.calculate_rsi(df['Close'], self.rsi_period)
        
        macd_df = self.calculate_macd(df['Close'], self.macd_fast, self.macd_slow, self.macd_signal)
        df['macd'] = macd_df['macd']
        df['macd_signal'] = macd_df['signal']
        df['macd_histogram'] = macd_df['histogram']
        
        bb_df = self.calculate_bollinger_bands(df['Close'])
        df['bb_upper'] = bb_df['upper']
        df['bb_middle'] = bb_df['middle']
        df['bb_lower'] = bb_df['lower']
        df['bb_squeeze'] = bb_df['squeeze']
        
        volume_df = self.calculate_volume_profile(df['Volume'])
        df['volume_ma'] = volume_df['volume_ma']
        df['volume_ratio'] = volume_df['volume_ratio']
        
        momentum_df = self.calculate_momentum(df['Close'])
        df['momentum_5'] = momentum_df['momentum_short']
        df['momentum_10'] = momentum_df['momentum_long']
        
        # Calculate ATR for position sizing
        df['atr'] = self.calculate_atr(df['High'], df['Low'], df['Close'])
        
        # Initialize composite columns
        df['trend_score'] = 0.0
        df['trend_direction'] = 'NEUTRAL'
        df['trend_strength'] = 'WEAK'
        df['confidence'] = 0.0
        
        # Calculate composite for each row (skip initial rows for indicator warm-up)
        min_periods = 50
        for i in range(min_periods, len(df)):
            # Score each component
            ema_score, ema_components = self.score_ema_alignment(df, i)
            rsi_score, rsi_components = self.score_rsi_momentum(df, i)
            macd_score, macd_components = self.score_macd_signal(df, i)
            volume_score, volume_components = self.score_volume_confirmation(df, i)
            momentum_score, momentum_components = self.score_momentum_filter(df, i)
            
            # Calculate total score
            total_score = ema_score + rsi_score + macd_score + volume_score + momentum_score
            
            # Apply volatility filter
            filtered_score = self.apply_volatility_filter(total_score, df, i)
            
            # Store results
            df.loc[df.index[i], 'trend_score'] = filtered_score
            
            # Determine direction and strength
            if filtered_score >= self.min_strength:
                df.loc[df.index[i], 'trend_direction'] = 'LONG'
                df.loc[df.index[i], 'confidence'] = min(filtered_score / 6.0, 1.0)
            elif filtered_score <= -self.min_strength:
                df.loc[df.index[i], 'trend_direction'] = 'SHORT'
                df.loc[df.index[i], 'confidence'] = min(abs(filtered_score) / 6.0, 1.0)
            else:
                df.loc[df.index[i], 'trend_direction'] = 'NEUTRAL'
                df.loc[df.index[i], 'confidence'] = 0.0
            
            # Classify strength
            abs_score = abs(filtered_score)
            if abs_score >= 5.0:
                df.loc[df.index[i], 'trend_strength'] = 'STRONG'
            elif abs_score >= 3.5:
                df.loc[df.index[i], 'trend_strength'] = 'MEDIUM'
            else:
                df.loc[df.index[i], 'trend_strength'] = 'WEAK'
        
        return df
    
    def get_current_signal(self, df: pd.DataFrame) -> Optional[TrendSignal]:
        """
        Get current trading signal from dataframe
        Returns None if no valid signal
        """
        if len(df) < 50:
            return None
        
        # Calculate composite if not already done
        if 'trend_score' not in df.columns:
            df = self.calculate_composite(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Build signal if valid
        if latest['trend_direction'] != 'NEUTRAL':
            components = {
                'ema': latest.get('ema_8', 0),
                'rsi': latest.get('rsi', 50),
                'macd': latest.get('macd', 0),
                'volume': latest.get('volume_ratio', 1),
                'momentum': latest.get('momentum_5', 0),
                'atr': latest.get('atr', 0)
            }
            
            return TrendSignal(
                score=latest['trend_score'],
                direction=latest['trend_direction'],
                strength=latest['trend_strength'],
                components=components,
                confidence=latest['confidence']
            )
        
        return None