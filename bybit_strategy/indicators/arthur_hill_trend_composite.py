"""
Arthur Hill's Trend Composite Indicator - Correct Implementation
Based on official StockCharts documentation: TIP Trend Composite

Five Binary Indicators:
1. TIP Moving Average Trend (SMA + ROC)
2. TIP CCI Close  
3. Bollinger Bands
4. Keltner Channels
5. TIP StochClose

Each indicator provides +1 (bullish) or -1 (bearish) signal
Total Score: +5 to -5 (always odd number)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ArthurHillSignal:
    """Arthur Hill Trend Composite signal data structure"""
    score: int  # -5 to +5 (always odd)
    direction: str  # 'LONG', 'SHORT', or 'NEUTRAL'
    components: Dict[str, int]  # Each component: +1 or -1
    confidence: float  # Abs(score) / 5

class ArthurHillTrendComposite:
    """
    Authentic Arthur Hill Trend Composite Implementation
    Based on TIP Trend Composite from StockCharts
    """
    
    def __init__(self, base_period: int = 125, crypto_hourly: bool = True, fast_mode: bool = False):
        """
        Initialize Arthur Hill Trend Composite
        
        Args:
            base_period: Base period (125 days default, adjusted for timeframe)
            crypto_hourly: If True, adjust periods for 1H crypto timeframe
            fast_mode: If True, use even shorter periods for more frequent signals
        """
        if crypto_hourly:
            if fast_mode:
                # Fast mode for more frequent 1H signals (~1-2 days lookback)
                self.ma_period = 50     # ~2 days at 1H
                self.cci_period = 50    # ~2 days 
                self.bb_period = 50     # ~2 days
                self.kc_period = 50     # ~2 days
                self.stoch_period = 50  # ~2 days
                self.roc_period = 3     # Faster ROC
                self.stoch_smooth = 3   # Faster smoothing
            else:
                # Standard 1H crypto periods - shorter than original but not too fast
                self.ma_period = 100    # ~4 days at 1H
                self.cci_period = 100   # ~4 days 
                self.bb_period = 100    # ~4 days
                self.kc_period = 100    # ~4 days
                self.stoch_period = 100 # ~4 days
                self.roc_period = 5     # Keep ROC short
                self.stoch_smooth = 5
        else:
            # Original daily periods
            self.ma_period = base_period
            self.cci_period = base_period
            self.bb_period = base_period
            self.kc_period = base_period
            self.stoch_period = base_period
            self.roc_period = 5
            self.stoch_smooth = 5
        
        # Signal thresholds (from StockCharts documentation)
        self.cci_bull_threshold = 100
        self.cci_bear_threshold = -100
        self.stoch_bull_threshold = 60
        self.stoch_bear_threshold = 40
        self.bb_std_dev = 1.0
        self.kc_atr_multiplier = 2.0
    
    def calculate_tip_moving_average_trend(self, close: pd.Series) -> pd.Series:
        """
        Calculate TIP Moving Average Trend
        Signal: ROC of SMA cross above/below zero
        +1 = ROC > 0, -1 = ROC <= 0
        """
        sma = close.rolling(window=self.ma_period).mean()
        roc = sma.pct_change(periods=self.roc_period) * 100
        
        # Binary signal
        signal = np.where(roc > 0, 1, -1)
        return pd.Series(signal, index=close.index, name='ma_trend_signal')
    
    def calculate_tip_cci_close(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        Calculate TIP CCI Close
        Signal: CCI above +100 (bullish) or below -100 (bearish)
        Between -100 and +100 = neutral (use last signal)
        """
        # Calculate Typical Price
        tp = (high + low + close) / 3
        
        # Calculate CCI
        sma_tp = tp.rolling(window=self.cci_period).mean()
        mad = tp.rolling(window=self.cci_period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - sma_tp) / (0.015 * mad)
        
        # Binary signal with neutral zone
        signal = np.where(cci > self.cci_bull_threshold, 1,
                         np.where(cci < self.cci_bear_threshold, -1, np.nan))
        
        # Forward fill to maintain last signal in neutral zone
        signal = pd.Series(signal, index=close.index).ffill().fillna(-1)
        
        return signal.astype(int)
    
    def calculate_bollinger_bands_signal(self, close: pd.Series) -> pd.Series:
        """
        Calculate Bollinger Bands Signal  
        Signal: Close above upper band (+1) or below lower band (-1)
        Between bands = neutral (use last signal)
        """
        sma = close.rolling(window=self.bb_period).mean()
        std = close.rolling(window=self.bb_period).std()
        
        upper_band = sma + (std * self.bb_std_dev)
        lower_band = sma - (std * self.bb_std_dev)
        
        # Binary signal
        signal = np.where(close > upper_band, 1,
                         np.where(close < lower_band, -1, np.nan))
        
        # Forward fill to maintain last signal
        signal = pd.Series(signal, index=close.index).fillna(method='ffill').fillna(-1)
        
        return signal.astype(int)
    
    def calculate_keltner_channels_signal(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        Calculate Keltner Channels Signal
        Signal: Close above upper channel (+1) or below lower channel (-1)
        Between channels = neutral (use last signal)
        """
        # EMA of close
        ema = close.ewm(span=self.kc_period).mean()
        
        # Calculate ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.kc_period).mean()
        
        # Keltner Channels
        upper_channel = ema + (atr * self.kc_atr_multiplier)
        lower_channel = ema - (atr * self.kc_atr_multiplier)
        
        # Binary signal
        signal = np.where(close > upper_channel, 1,
                         np.where(close < lower_channel, -1, np.nan))
        
        # Forward fill to maintain last signal
        signal = pd.Series(signal, index=close.index).fillna(method='ffill').fillna(-1)
        
        return signal.astype(int)
    
    def calculate_tip_stoch_close(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        Calculate TIP StochClose
        Signal: Stochastic above 60 (+1) or below 40 (-1)
        Between 40-60 = neutral (use last signal)
        """
        # Calculate %K
        lowest_low = low.rolling(window=self.stoch_period).min()
        highest_high = high.rolling(window=self.stoch_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        
        # Smooth with SMA
        stoch_smooth = k_percent.rolling(window=self.stoch_smooth).mean()
        
        # Binary signal
        signal = np.where(stoch_smooth > self.stoch_bull_threshold, 1,
                         np.where(stoch_smooth < self.stoch_bear_threshold, -1, np.nan))
        
        # Forward fill to maintain last signal
        signal = pd.Series(signal, index=close.index).fillna(method='ffill').fillna(-1)
        
        return signal.astype(int)
    
    def calculate_composite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Arthur Hill Trend Composite
        Returns DataFrame with all component signals and composite score
        """
        # Ensure we have required columns
        required_cols = ['High', 'Low', 'Close']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in DataFrame")
        
        # Calculate all component signals
        df['ah_ma_trend'] = self.calculate_tip_moving_average_trend(df['Close'])
        df['ah_cci_signal'] = self.calculate_tip_cci_close(df['High'], df['Low'], df['Close'])
        df['ah_bb_signal'] = self.calculate_bollinger_bands_signal(df['Close'])
        df['ah_kc_signal'] = self.calculate_keltner_channels_signal(df['High'], df['Low'], df['Close'])
        df['ah_stoch_signal'] = self.calculate_tip_stoch_close(df['High'], df['Low'], df['Close'])
        
        # Calculate composite score (-5 to +5)
        df['ah_composite_score'] = (
            df['ah_ma_trend'] + 
            df['ah_cci_signal'] + 
            df['ah_bb_signal'] + 
            df['ah_kc_signal'] + 
            df['ah_stoch_signal']
        )
        
        # Determine trend direction
        df['ah_trend_direction'] = np.where(
            df['ah_composite_score'] > 0, 'LONG',
            np.where(df['ah_composite_score'] < 0, 'SHORT', 'NEUTRAL')
        )
        
        # Calculate confidence (0 to 1)
        df['ah_confidence'] = abs(df['ah_composite_score']) / 5.0
        
        # Classify strength based on score magnitude
        df['ah_trend_strength'] = np.where(
            abs(df['ah_composite_score']) >= 4, 'STRONG',
            np.where(abs(df['ah_composite_score']) >= 2, 'MEDIUM', 'WEAK')
        )
        
        return df
    
    def get_current_signal(self, df: pd.DataFrame, min_score: int = 2) -> Optional[ArthurHillSignal]:
        """
        Get current Arthur Hill signal from DataFrame
        
        Args:
            df: DataFrame with calculated composite
            min_score: Minimum absolute score to generate signal (default 2)
        
        Returns:
            ArthurHillSignal or None
        """
        if len(df) < max(self.ma_period, self.cci_period, self.bb_period, 
                        self.kc_period, self.stoch_period):
            return None
        
        # Calculate composite if not already done
        if 'ah_composite_score' not in df.columns:
            df = self.calculate_composite(df)
        
        # Get latest values
        latest = df.iloc[-1]
        score = int(latest['ah_composite_score'])
        
        # Check minimum score threshold
        if abs(score) < min_score:
            return None
        
        # Build component breakdown
        components = {
            'ma_trend': int(latest['ah_ma_trend']),
            'cci': int(latest['ah_cci_signal']),
            'bollinger': int(latest['ah_bb_signal']),
            'keltner': int(latest['ah_kc_signal']),
            'stochastic': int(latest['ah_stoch_signal'])
        }
        
        # Determine direction
        if score > 0:
            direction = 'LONG'
        elif score < 0:
            direction = 'SHORT'
        else:
            direction = 'NEUTRAL'
        
        # Calculate confidence
        confidence = abs(score) / 5.0
        
        return ArthurHillSignal(
            score=score,
            direction=direction,
            components=components,
            confidence=confidence
        )
    
    def get_signal_description(self, signal: ArthurHillSignal) -> str:
        """Get human-readable signal description"""
        if signal is None:
            return "No signal"
        
        bull_count = sum(1 for v in signal.components.values() if v > 0)
        bear_count = sum(1 for v in signal.components.values() if v < 0)
        
        desc = f"Score: {signal.score:+d} ({bull_count} bull, {bear_count} bear)\n"
        desc += f"Direction: {signal.direction}\n"
        desc += f"Confidence: {signal.confidence:.1%}\n"
        desc += "Components:\n"
        
        for name, value in signal.components.items():
            status = "BULL" if value > 0 else "BEAR"
            desc += f"  {name}: {status} ({value:+d})\n"
        
        return desc

# Utility functions
def create_arthur_hill_composite(base_period: int = 125, crypto_hourly: bool = True) -> ArthurHillTrendComposite:
    """Factory function to create Arthur Hill Trend Composite"""
    return ArthurHillTrendComposite(base_period=base_period, crypto_hourly=crypto_hourly)

def backtest_arthur_hill_signals(df: pd.DataFrame, 
                                initial_capital: float = 10000,
                                risk_per_trade: float = 0.02,
                                min_score: int = 2) -> dict:
    """
    Simple backtest for Arthur Hill signals
    Uses basic position sizing and ATR stops
    """
    from ..utils.atr_trailing_stop import ATRTrailingStop
    
    # Initialize
    composite = ArthurHillTrendComposite()
    atr_stop = ATRTrailingStop()
    
    # Calculate signals
    df_signals = composite.calculate_composite(df.copy())
    
    # Simple backtest logic
    capital = initial_capital
    position = None
    trades = []
    
    for i in range(len(df_signals)):
        current = df_signals.iloc[i]
        
        # Check for entry signal
        if position is None and abs(current['ah_composite_score']) >= min_score:
            # Enter position
            direction = current['ah_trend_direction']
            entry_price = current['Close']
            
            # Calculate position size (simple risk-based)
            risk_amount = capital * risk_per_trade
            # Assume 2% stop loss for position sizing
            position_size = risk_amount / (entry_price * 0.02)
            
            position = {
                'direction': direction,
                'entry_price': entry_price,
                'entry_index': i,
                'size': position_size,
                'entry_score': current['ah_composite_score']
            }
        
        # Check for exit signal (score flips or weakens significantly)
        elif position is not None:
            current_score = current['ah_composite_score']
            entry_score = position['entry_score']
            
            # Exit conditions:
            # 1. Score flips sign
            # 2. Score weakens significantly (drops below threshold)
            # 3. End of data
            should_exit = False
            exit_reason = 'hold'
            
            if (entry_score > 0 and current_score <= 0) or (entry_score < 0 and current_score >= 0):
                should_exit = True
                exit_reason = 'signal_flip'
            elif abs(current_score) < min_score:
                should_exit = True
                exit_reason = 'signal_weak'
            elif i == len(df_signals) - 1:
                should_exit = True
                exit_reason = 'end_of_data'
            
            if should_exit:
                # Calculate P&L
                exit_price = current['Close']
                
                if position['direction'] == 'LONG':
                    pnl = (exit_price - position['entry_price']) * position['size']
                else:
                    pnl = (position['entry_price'] - exit_price) * position['size']
                
                capital += pnl
                
                # Record trade
                trades.append({
                    'entry_time': df_signals.index[position['entry_index']],
                    'exit_time': df_signals.index[i],
                    'direction': position['direction'],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'size': position['size'],
                    'pnl': pnl,
                    'pnl_pct': (pnl / (position['entry_price'] * position['size'])) * 100,
                    'exit_reason': exit_reason,
                    'entry_score': position['entry_score'],
                    'exit_score': current_score
                })
                
                position = None
    
    # Calculate results
    if trades:
        total_pnl = sum(t['pnl'] for t in trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        
        results = {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return': total_pnl,
            'total_return_pct': (total_pnl / initial_capital) * 100,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'win_rate': len(winning_trades) / len(trades),
            'avg_trade': total_pnl / len(trades),
            'trades': trades
        }
    else:
        results = {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return': 0,
            'total_return_pct': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'win_rate': 0,
            'avg_trade': 0,
            'trades': []
        }
    
    return results