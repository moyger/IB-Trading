"""
FTMO-Arthur Hill Hybrid Trend Composite
Combines the successful FTMO weighted scoring with Arthur Hill's proven indicators
Optimized for 1H crypto trading with high win rates
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class HybridTrendSignal:
    """Hybrid trend signal combining FTMO and Arthur Hill methodologies"""
    score: float
    direction: str  # 'LONG', 'SHORT', or 'NEUTRAL'
    strength: str  # 'STRONG', 'MEDIUM', 'WEAK'
    confidence: float
    components: Dict[str, float]
    
    # FTMO-style detailed breakdown
    ema_score: float
    rsi_score: float
    macd_score: float
    volume_score: float
    momentum_score: float
    
    # Arthur Hill components (for validation)
    ah_ma_trend: int
    ah_cci: int
    ah_bollinger: int
    ah_keltner: int
    ah_stoch: int

class FTMOArthurHillHybrid:
    """
    Hybrid system combining:
    1. FTMO's successful weighted multi-indicator scoring
    2. Arthur Hill's proven 5-indicator validation
    3. Crypto-optimized parameters for 1H trading
    """
    
    def __init__(self, timeframe_hours: int = 1):
        """
        Initialize hybrid system
        
        Args:
            timeframe_hours: Timeframe in hours (1 for 1H, 4 for 4H, etc.)
        """
        self.timeframe_hours = timeframe_hours
        
        # FTMO-style parameters (optimized for crypto 1H)
        if timeframe_hours == 1:
            # 1H optimized settings - faster than original but not too fast
            self.ema_periods = [8, 21, 50]    # Faster than 12,26,50
            self.rsi_period = 14
            self.macd_fast = 8                # Faster MACD
            self.macd_slow = 21
            self.macd_signal = 5
            self.volume_period = 20
            self.momentum_short = 5
            self.momentum_long = 10
        elif timeframe_hours == 4:
            # 4H settings (closer to original FTMO)
            self.ema_periods = [12, 26, 50]
            self.rsi_period = 14
            self.macd_fast = 12
            self.macd_slow = 26
            self.macd_signal = 9
            self.volume_period = 20
            self.momentum_short = 5
            self.momentum_long = 10
        
        # Arthur Hill validation parameters (shorter for crypto)
        self.ah_base_period = 50  # Much shorter than 125
        self.ah_roc_period = 3
        self.ah_stoch_smooth = 3
        
        # Scoring thresholds
        self.min_ftmo_score = 3.0      # Minimum FTMO score to trade
        self.min_ah_agreement = 2      # Minimum Arthur Hill agreement (out of 5)
        
        # FTMO component weights
        self.weights = {
            'ema': 0.40,      # 40% - trend alignment 
            'rsi': 0.20,      # 20% - momentum
            'macd': 0.20,     # 20% - trend change
            'volume': 0.10,   # 10% - confirmation
            'momentum': 0.10  # 10% - short-term momentum
        }
    
    def calculate_ftmo_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate FTMO-style indicators"""
        
        # EMAs
        for period in self.ema_periods:
            df[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_fast = df['Close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Volume indicators
        df['volume_ma'] = df['Volume'].rolling(window=self.volume_period).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_ma']
        
        # Momentum
        df['momentum_short'] = df['Close'].pct_change(self.momentum_short) * 100
        df['momentum_long'] = df['Close'].pct_change(self.momentum_long) * 100
        
        return df
    
    def calculate_arthur_hill_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Arthur Hill validation indicators"""
        
        # Moving Average Trend (SMA + ROC)
        sma = df['Close'].rolling(window=self.ah_base_period).mean()
        roc = sma.pct_change(periods=self.ah_roc_period) * 100
        df['ah_ma_trend'] = np.where(roc > 0, 1, -1)
        
        # CCI
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        sma_tp = tp.rolling(window=self.ah_base_period).mean()
        mad = tp.rolling(window=self.ah_base_period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )
        cci = (tp - sma_tp) / (0.015 * mad)
        df['ah_cci'] = np.where(cci > 100, 1, np.where(cci < -100, -1, np.nan))
        df['ah_cci'] = df['ah_cci'].ffill().fillna(-1).astype(int)
        
        # Bollinger Bands
        bb_sma = df['Close'].rolling(window=self.ah_base_period).mean()
        bb_std = df['Close'].rolling(window=self.ah_base_period).std()
        upper_band = bb_sma + bb_std
        lower_band = bb_sma - bb_std
        df['ah_bollinger'] = np.where(df['Close'] > upper_band, 1,
                                     np.where(df['Close'] < lower_band, -1, np.nan))
        df['ah_bollinger'] = df['ah_bollinger'].ffill().fillna(-1).astype(int)
        
        # Keltner Channels
        kc_ema = df['Close'].ewm(span=self.ah_base_period).mean()
        tr1 = df['High'] - df['Low']
        tr2 = abs(df['High'] - df['Close'].shift())
        tr3 = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.ah_base_period).mean()
        upper_kc = kc_ema + (atr * 2)
        lower_kc = kc_ema - (atr * 2)
        df['ah_keltner'] = np.where(df['Close'] > upper_kc, 1,
                                   np.where(df['Close'] < lower_kc, -1, np.nan))
        df['ah_keltner'] = df['ah_keltner'].ffill().fillna(-1).astype(int)
        
        # Stochastic
        lowest_low = df['Low'].rolling(window=self.ah_base_period).min()
        highest_high = df['High'].rolling(window=self.ah_base_period).max()
        k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
        stoch = k_percent.rolling(window=self.ah_stoch_smooth).mean()
        df['ah_stoch'] = np.where(stoch > 60, 1, np.where(stoch < 40, -1, np.nan))
        df['ah_stoch'] = df['ah_stoch'].ffill().fillna(-1).astype(int)
        
        return df
    
    def score_ftmo_ema_alignment(self, df: pd.DataFrame, idx: int) -> Tuple[float, Dict]:
        """FTMO-style EMA alignment scoring (40% weight)"""
        components = {}
        score = 0.0
        
        close = df['Close'].iloc[idx]
        ema_fast = df[f'ema_{self.ema_periods[0]}'].iloc[idx]
        ema_medium = df[f'ema_{self.ema_periods[1]}'].iloc[idx]
        ema_slow = df[f'ema_{self.ema_periods[2]}'].iloc[idx]
        
        # EMA order scoring (stronger scoring than original)
        if ema_fast > ema_medium > ema_slow:
            score += 3.0  # Perfect bullish alignment
            components['ema_alignment'] = 3.0
        elif ema_fast > ema_medium:
            score += 1.5  # Partial bullish
            components['ema_alignment'] = 1.5
        elif ema_fast < ema_medium < ema_slow:
            score -= 3.0  # Perfect bearish alignment
            components['ema_alignment'] = -3.0
        elif ema_fast < ema_medium:
            score -= 1.5  # Partial bearish
            components['ema_alignment'] = -1.5
        
        # Price vs EMA
        if close > ema_fast:
            score += 1.0
            components['price_vs_ema'] = 1.0
        else:
            score -= 1.0
            components['price_vs_ema'] = -1.0
        
        # EMA slope (momentum)
        ema_fast_prev = df[f'ema_{self.ema_periods[0]}'].iloc[idx-1] if idx > 0 else ema_fast
        if ema_fast > ema_fast_prev:
            score += 1.0
            components['ema_slope'] = 1.0
        else:
            score -= 1.0
            components['ema_slope'] = -1.0
        
        return score, components
    
    def score_ftmo_rsi_momentum(self, df: pd.DataFrame, idx: int) -> Tuple[float, Dict]:
        """FTMO-style RSI momentum scoring (20% weight)"""
        components = {}
        score = 0.0
        
        rsi = df['rsi'].iloc[idx]
        rsi_prev = df['rsi'].iloc[idx-1] if idx > 0 else rsi
        
        # RSI level scoring (crypto-optimized thresholds)
        if rsi > 65:  # Strong bullish
            score += 2.0
        elif rsi > 55:  # Moderate bullish
            score += 1.0
        elif rsi < 35:  # Strong bearish  
            score -= 2.0
        elif rsi < 45:  # Moderate bearish
            score -= 1.0
        
        components['rsi_level'] = score
        
        # RSI momentum
        rsi_change = rsi - rsi_prev
        if abs(rsi_change) > 2:
            momentum_score = 1.0 if rsi_change > 0 else -1.0
            score += momentum_score
            components['rsi_momentum'] = momentum_score
        
        return score, components
    
    def score_ftmo_macd_signals(self, df: pd.DataFrame, idx: int) -> Tuple[float, Dict]:
        """FTMO-style MACD scoring (20% weight)"""
        components = {}
        score = 0.0
        
        macd = df['macd'].iloc[idx]
        signal = df['macd_signal'].iloc[idx]
        histogram = df['macd_histogram'].iloc[idx]
        hist_prev = df['macd_histogram'].iloc[idx-1] if idx > 0 else histogram
        
        # MACD vs Signal
        if macd > signal:
            score += 2.0
            components['macd_cross'] = 2.0
        else:
            score -= 2.0
            components['macd_cross'] = -2.0
        
        # Histogram momentum (strengthening/weakening)
        if histogram > hist_prev:
            score += 1.0
            components['macd_momentum'] = 1.0
        else:
            score -= 1.0
            components['macd_momentum'] = -1.0
        
        # MACD zero line
        if macd > 0:
            score += 0.5
            components['macd_zero'] = 0.5
        else:
            score -= 0.5
            components['macd_zero'] = -0.5
        
        return score, components
    
    def score_ftmo_volume_confirmation(self, df: pd.DataFrame, idx: int) -> Tuple[float, Dict]:
        """FTMO-style volume confirmation (10% weight)"""
        components = {}
        score = 0.0
        
        volume_ratio = df['volume_ratio'].iloc[idx]
        
        # Volume level scoring
        if volume_ratio > 1.5:  # Very high volume
            score += 2.0
        elif volume_ratio > 1.2:  # High volume
            score += 1.0
        elif volume_ratio < 0.7:  # Low volume (penalty)
            score -= 1.0
        
        components['volume_level'] = score
        return score, components
    
    def score_ftmo_momentum_filter(self, df: pd.DataFrame, idx: int) -> Tuple[float, Dict]:
        """FTMO-style momentum filter (10% weight)"""
        components = {}
        score = 0.0
        
        momentum_short = df['momentum_short'].iloc[idx]
        momentum_long = df['momentum_long'].iloc[idx]
        
        # Short-term momentum
        if abs(momentum_short) > 2.0:
            score += 1.0 if momentum_short > 0 else -1.0
            components['momentum_short'] = score
        
        # Long-term momentum alignment
        if abs(momentum_long) > 3.0:
            momentum_score = 1.0 if momentum_long > 0 else -1.0
            score += momentum_score
            components['momentum_long'] = momentum_score
        
        return score, components
    
    def calculate_composite(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate hybrid composite signal"""
        
        # Calculate all indicators
        df = self.calculate_ftmo_indicators(df)
        df = self.calculate_arthur_hill_indicators(df)
        
        # Initialize result columns
        df['ftmo_score'] = 0.0
        df['ftmo_direction'] = 'NEUTRAL'
        df['ah_score'] = 0
        df['ah_agreement'] = 0
        df['hybrid_score'] = 0.0
        df['hybrid_direction'] = 'NEUTRAL'
        df['hybrid_confidence'] = 0.0
        
        # Calculate for each row (skip initial bars for indicator warm-up)
        min_periods = max(self.ah_base_period, max(self.ema_periods)) + 10
        
        for i in range(min_periods, len(df)):
            # FTMO scoring
            ema_score, ema_comp = self.score_ftmo_ema_alignment(df, i)
            rsi_score, rsi_comp = self.score_ftmo_rsi_momentum(df, i)
            macd_score, macd_comp = self.score_ftmo_macd_signals(df, i)
            vol_score, vol_comp = self.score_ftmo_volume_confirmation(df, i)
            mom_score, mom_comp = self.score_ftmo_momentum_filter(df, i)
            
            # Weighted FTMO composite
            ftmo_total = (
                ema_score * self.weights['ema'] +
                rsi_score * self.weights['rsi'] + 
                macd_score * self.weights['macd'] +
                vol_score * self.weights['volume'] +
                mom_score * self.weights['momentum']
            )
            
            df.loc[df.index[i], 'ftmo_score'] = ftmo_total
            
            # Arthur Hill validation
            ah_components = [
                df['ah_ma_trend'].iloc[i],
                df['ah_cci'].iloc[i], 
                df['ah_bollinger'].iloc[i],
                df['ah_keltner'].iloc[i],
                df['ah_stoch'].iloc[i]
            ]
            
            ah_total = sum(ah_components)
            ah_agreement = sum(1 for x in ah_components if x == (1 if ah_total > 0 else -1))
            
            df.loc[df.index[i], 'ah_score'] = ah_total
            df.loc[df.index[i], 'ah_agreement'] = ah_agreement
            
            # Hybrid decision
            # Require both FTMO signal AND Arthur Hill agreement
            if abs(ftmo_total) >= self.min_ftmo_score and ah_agreement >= self.min_ah_agreement:
                if ftmo_total > 0 and ah_total > 0:
                    df.loc[df.index[i], 'hybrid_direction'] = 'LONG'
                    df.loc[df.index[i], 'hybrid_score'] = ftmo_total
                    df.loc[df.index[i], 'hybrid_confidence'] = min(ftmo_total / 10.0, 1.0) * (ah_agreement / 5.0)
                elif ftmo_total < 0 and ah_total < 0:
                    df.loc[df.index[i], 'hybrid_direction'] = 'SHORT'
                    df.loc[df.index[i], 'hybrid_score'] = ftmo_total
                    df.loc[df.index[i], 'hybrid_confidence'] = min(abs(ftmo_total) / 10.0, 1.0) * (ah_agreement / 5.0)
            
            # FTMO direction (for comparison)
            if ftmo_total >= self.min_ftmo_score:
                df.loc[df.index[i], 'ftmo_direction'] = 'LONG'
            elif ftmo_total <= -self.min_ftmo_score:
                df.loc[df.index[i], 'ftmo_direction'] = 'SHORT'
        
        return df
    
    def get_current_signal(self, df: pd.DataFrame) -> Optional[HybridTrendSignal]:
        """Get current hybrid signal"""
        if len(df) < 100:
            return None
        
        # Calculate if not already done
        if 'hybrid_direction' not in df.columns:
            df = self.calculate_composite(df)
        
        latest = df.iloc[-1]
        
        if latest['hybrid_direction'] == 'NEUTRAL':
            return None
        
        return HybridTrendSignal(
            score=latest['hybrid_score'],
            direction=latest['hybrid_direction'],
            strength='STRONG' if abs(latest['hybrid_score']) >= 6 else 'MEDIUM',
            confidence=latest['hybrid_confidence'],
            components={
                'ftmo_score': latest['ftmo_score'],
                'ah_score': latest['ah_score'],
                'ah_agreement': latest['ah_agreement']
            },
            ema_score=latest['ftmo_score'],  # Simplified for now
            rsi_score=0,  # Would need to store component scores
            macd_score=0,
            volume_score=0,
            momentum_score=0,
            ah_ma_trend=latest['ah_ma_trend'],
            ah_cci=latest['ah_cci'],
            ah_bollinger=latest['ah_bollinger'],
            ah_keltner=latest['ah_keltner'],
            ah_stoch=latest['ah_stoch']
        )

# Factory function
def create_hybrid_composite(timeframe_hours: int = 1) -> FTMOArthurHillHybrid:
    """Create hybrid composite for given timeframe"""
    return FTMOArthurHillHybrid(timeframe_hours=timeframe_hours)