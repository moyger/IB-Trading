"""
ATR Trailing Stop Implementation
Professional trailing stop methodology using Average True Range
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional

class ATRTrailingStop:
    """
    ATR-based Trailing Stop Loss System
    Professional implementation for trend following
    """
    
    def __init__(self, atr_period: int = 14, atr_multiplier: float = 3.0):
        """
        Initialize ATR Trailing Stop
        
        Args:
            atr_period: Period for ATR calculation (default 14)
            atr_multiplier: ATR multiplier for stop distance (default 3.0)
        """
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        Calculate Average True Range
        
        Returns:
            pd.Series: ATR values
        """
        # True Range calculation
        tr1 = high - low  # Current high - current low
        tr2 = abs(high - close.shift())  # Current high - previous close
        tr3 = abs(low - close.shift())   # Current low - previous close
        
        # True Range is the maximum of the three
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR is the moving average of True Range
        atr = tr.rolling(window=self.atr_period).mean()
        
        return atr
    
    def calculate_trailing_stops(self, df: pd.DataFrame, direction: str) -> pd.DataFrame:
        """
        Calculate ATR trailing stops for given direction
        
        Args:
            df: DataFrame with OHLC data
            direction: 'LONG' or 'SHORT'
            
        Returns:
            DataFrame with trailing stop columns added
        """
        # Calculate ATR
        df['atr'] = self.calculate_atr(df['High'], df['Low'], df['Close'])
        
        if direction == 'LONG':
            # Long trailing stop: Close - (ATR * multiplier)
            df['trailing_stop_raw'] = df['Close'] - (df['atr'] * self.atr_multiplier)
            
            # Trailing stop can only move up, never down
            df['trailing_stop'] = df['trailing_stop_raw'].copy()
            for i in range(1, len(df)):
                if df['trailing_stop_raw'].iloc[i] > df['trailing_stop'].iloc[i-1]:
                    df['trailing_stop'].iloc[i] = df['trailing_stop_raw'].iloc[i]
                else:
                    df['trailing_stop'].iloc[i] = df['trailing_stop'].iloc[i-1]
                    
        else:  # SHORT
            # Short trailing stop: Close + (ATR * multiplier)
            df['trailing_stop_raw'] = df['Close'] + (df['atr'] * self.atr_multiplier)
            
            # Trailing stop can only move down, never up
            df['trailing_stop'] = df['trailing_stop_raw'].copy()
            for i in range(1, len(df)):
                if df['trailing_stop_raw'].iloc[i] < df['trailing_stop'].iloc[i-1]:
                    df['trailing_stop'].iloc[i] = df['trailing_stop_raw'].iloc[i]
                else:
                    df['trailing_stop'].iloc[i] = df['trailing_stop'].iloc[i-1]
        
        # Determine exit signals
        if direction == 'LONG':
            df['stop_hit'] = df['Low'] <= df['trailing_stop']
        else:  # SHORT
            df['stop_hit'] = df['High'] >= df['trailing_stop']
        
        return df
    
    def find_exit_point(self, df: pd.DataFrame, entry_idx: int, direction: str) -> Tuple[Optional[int], Optional[float], str]:
        """
        Find exit point using ATR trailing stop
        
        Args:
            df: DataFrame with OHLC and trailing stop data
            entry_idx: Index of entry point
            direction: 'LONG' or 'SHORT'
            
        Returns:
            Tuple of (exit_index, exit_price, exit_reason)
        """
        if entry_idx >= len(df) - 1:
            return None, None, 'no_data'
        
        # Slice data from entry point forward
        df_trade = df.iloc[entry_idx:].copy()
        
        # Recalculate trailing stops from entry
        df_trade = self.calculate_trailing_stops(df_trade, direction)
        
        # Find first stop hit
        stop_hits = df_trade[df_trade['stop_hit'] == True]
        
        if len(stop_hits) > 0:
            # First stop hit after entry
            exit_idx = stop_hits.index[0]
            
            if direction == 'LONG':
                # Exit at the trailing stop level or low, whichever is higher
                exit_price = max(df_trade.loc[exit_idx, 'trailing_stop'], 
                               df_trade.loc[exit_idx, 'Low'])
            else:  # SHORT
                # Exit at the trailing stop level or high, whichever is lower
                exit_price = min(df_trade.loc[exit_idx, 'trailing_stop'],
                               df_trade.loc[exit_idx, 'High'])
            
            return exit_idx, exit_price, 'trailing_stop'
        
        # No stop hit - exit at end of data
        return df.index[-1], df['Close'].iloc[-1], 'end_of_data'
    
    def backtest_with_trailing_stops(self, df: pd.DataFrame, signals_df: pd.DataFrame, 
                                    initial_capital: float = 10000, 
                                    position_size_pct: float = 1.0) -> dict:
        """
        Backtest strategy using ATR trailing stops
        
        Args:
            df: OHLC DataFrame
            signals_df: DataFrame with entry signals
            initial_capital: Starting capital
            position_size_pct: Position size as % of capital
            
        Returns:
            Dictionary with backtest results
        """
        capital = initial_capital
        trades = []
        current_position = None
        
        for idx, signal in signals_df.iterrows():
            if current_position is not None:
                continue  # Already in position
                
            if signal['ah_trend_direction'] in ['LONG', 'SHORT']:
                # Enter position
                entry_price = df.loc[idx, 'Close']
                direction = signal['ah_trend_direction']
                
                # Calculate position size
                risk_amount = capital * (position_size_pct / 100)
                position_size = risk_amount / entry_price
                
                # Find exit using ATR trailing stop
                exit_idx, exit_price, exit_reason = self.find_exit_point(df, idx, direction)
                
                if exit_idx is not None:
                    # Calculate P&L
                    if direction == 'LONG':
                        pnl = (exit_price - entry_price) * position_size
                    else:  # SHORT
                        pnl = (entry_price - exit_price) * position_size
                    
                    capital += pnl
                    
                    # Store trade
                    trade = {
                        'entry_date': idx,
                        'exit_date': exit_idx,
                        'direction': direction,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'position_size': position_size,
                        'pnl': pnl,
                        'pnl_pct': (pnl / risk_amount) * 100,
                        'exit_reason': exit_reason,
                        'capital_after': capital
                    }
                    trades.append(trade)
        
        # Calculate performance metrics
        if trades:
            total_pnl = sum(t['pnl'] for t in trades)
            winning_trades = [t for t in trades if t['pnl'] > 0]
            losing_trades = [t for t in trades if t['pnl'] <= 0]
            
            results = {
                'initial_capital': initial_capital,
                'final_capital': capital,
                'total_return': total_pnl,
                'total_return_pct': (total_pnl / initial_capital) * 100,
                'total_trades': len(trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': len(winning_trades) / len(trades) if trades else 0,
                'avg_win': np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0,
                'avg_loss': np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0,
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
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'trades': []
            }
        
        return results

# Utility functions
def create_atr_stop_strategy(df: pd.DataFrame, atr_period: int = 14, 
                           atr_multiplier: float = 3.0) -> ATRTrailingStop:
    """
    Factory function to create ATR trailing stop strategy
    """
    return ATRTrailingStop(atr_period=atr_period, atr_multiplier=atr_multiplier)

def optimize_atr_parameters(df: pd.DataFrame, signals_df: pd.DataFrame, 
                          atr_periods: list = None, atr_multipliers: list = None) -> dict:
    """
    Optimize ATR parameters using grid search
    """
    if atr_periods is None:
        atr_periods = [10, 14, 20]
    if atr_multipliers is None:
        atr_multipliers = [2.0, 2.5, 3.0, 3.5, 4.0]
    
    best_result = None
    best_params = None
    best_return = -float('inf')
    
    results = {}
    
    for period in atr_periods:
        for multiplier in atr_multipliers:
            atr_stop = ATRTrailingStop(atr_period=period, atr_multiplier=multiplier)
            result = atr_stop.backtest_with_trailing_stops(df, signals_df)
            
            key = f"ATR_{period}_{multiplier}"
            results[key] = result
            
            if result['total_return_pct'] > best_return:
                best_return = result['total_return_pct']
                best_result = result
                best_params = {'atr_period': period, 'atr_multiplier': multiplier}
    
    return {
        'best_params': best_params,
        'best_result': best_result,
        'all_results': results
    }