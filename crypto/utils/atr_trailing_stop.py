#!/usr/bin/env python3
"""
ATR Trailing Stop Loss Implementation
Dynamic stop-loss that trails price using Average True Range
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple

class ATRTrailingStop:
    """
    ATR-based Trailing Stop Loss System
    Dynamically adjusts stop-loss based on market volatility
    """
    
    def __init__(self, 
                 atr_period: int = 14,
                 atr_multiplier: float = 2.0,
                 initial_stop_multiplier: float = 2.5):
        """
        Initialize ATR Trailing Stop
        
        Args:
            atr_period: Period for ATR calculation
            atr_multiplier: Multiplier for trailing distance
            initial_stop_multiplier: Multiplier for initial stop (usually higher)
        """
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.initial_stop_multiplier = initial_stop_multiplier
        
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Average True Range
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Series with ATR values
        """
        # True Range components
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift(1))
        low_close = np.abs(df['Low'] - df['Close'].shift(1))
        
        # True Range is the maximum of the three
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        
        # ATR is the moving average of True Range
        atr = true_range.rolling(window=self.atr_period).mean()
        
        return atr.fillna(true_range)
    
    def initialize_stop(self, 
                       entry_price: float,
                       entry_direction: int,
                       current_atr: float) -> float:
        """
        Initialize stop-loss level for new position
        
        Args:
            entry_price: Entry price of position
            entry_direction: 1 for long, -1 for short
            current_atr: Current ATR value
            
        Returns:
            Initial stop-loss price
        """
        stop_distance = current_atr * self.initial_stop_multiplier
        
        if entry_direction > 0:  # Long position
            return entry_price - stop_distance
        else:  # Short position
            return entry_price + stop_distance
    
    def update_trailing_stop(self,
                           current_price: float,
                           current_atr: float,
                           position_direction: int,
                           current_stop: float) -> float:
        """
        Update trailing stop-loss based on current price and ATR
        
        Args:
            current_price: Current market price
            current_atr: Current ATR value
            position_direction: 1 for long, -1 for short
            current_stop: Current stop-loss level
            
        Returns:
            Updated stop-loss price
        """
        trail_distance = current_atr * self.atr_multiplier
        
        if position_direction > 0:  # Long position
            # New stop is price minus trail distance
            new_stop = current_price - trail_distance
            # Only move stop up (more favorable), never down
            return max(new_stop, current_stop)
        else:  # Short position  
            # New stop is price plus trail distance
            new_stop = current_price + trail_distance
            # Only move stop down (more favorable), never up
            return min(new_stop, current_stop)
    
    def check_stop_hit(self,
                      current_price: float,
                      stop_price: float,
                      position_direction: int) -> bool:
        """
        Check if stop-loss has been hit
        
        Args:
            current_price: Current market price
            stop_price: Stop-loss price
            position_direction: 1 for long, -1 for short
            
        Returns:
            True if stop has been hit
        """
        if position_direction > 0:  # Long position
            return current_price <= stop_price
        else:  # Short position
            return current_price >= stop_price
    
    def calculate_trailing_stops_series(self, 
                                       df: pd.DataFrame,
                                       entry_signals: pd.Series,
                                       exit_signals: pd.Series) -> pd.DataFrame:
        """
        Calculate trailing stops for entire price series with entry/exit signals
        
        Args:
            df: DataFrame with OHLC data
            entry_signals: Series with 1 for long entry, -1 for short entry, 0 for no signal
            exit_signals: Series with 1 where position should be exited
            
        Returns:
            DataFrame with trailing stop information
        """
        # Calculate ATR
        atr = self.calculate_atr(df)
        
        # Initialize result DataFrame
        result = pd.DataFrame(index=df.index)
        result['ATR'] = atr
        result['Price'] = df['Close']
        result['Entry_Signal'] = entry_signals
        result['Exit_Signal'] = exit_signals
        result['Position'] = 0  # 0: no position, 1: long, -1: short
        result['Stop_Loss'] = np.nan
        result['Stop_Hit'] = False
        result['Trail_Distance'] = atr * self.atr_multiplier
        
        # Track position state
        current_position = 0
        current_stop = np.nan
        entry_price = np.nan
        
        for i in range(len(df)):
            current_price = df['Close'].iloc[i]
            current_atr_val = atr.iloc[i]
            entry_signal = entry_signals.iloc[i]
            exit_signal = exit_signals.iloc[i]
            
            # Check for new entry
            if entry_signal != 0 and current_position == 0:
                current_position = entry_signal
                entry_price = current_price
                current_stop = self.initialize_stop(entry_price, current_position, current_atr_val)
                
            # Update trailing stop if in position
            elif current_position != 0:
                # Update trailing stop
                if not np.isnan(current_stop):
                    current_stop = self.update_trailing_stop(
                        current_price, current_atr_val, current_position, current_stop
                    )
                
                # Check if stop hit
                stop_hit = self.check_stop_hit(current_price, current_stop, current_position)
                
                # Exit on stop hit or exit signal
                if stop_hit or exit_signal:
                    result.loc[result.index[i], 'Stop_Hit'] = stop_hit
                    current_position = 0
                    current_stop = np.nan
                    entry_price = np.nan
            
            # Record current state
            result.loc[result.index[i], 'Position'] = current_position
            result.loc[result.index[i], 'Stop_Loss'] = current_stop
        
        # Calculate additional metrics
        result['Stop_Distance_Pct'] = np.where(
            result['Position'] != 0,
            abs(result['Stop_Loss'] - result['Price']) / result['Price'] * 100,
            np.nan
        )
        
        return result
    
    def get_stop_statistics(self, trailing_stops_df: pd.DataFrame) -> dict:
        """
        Calculate statistics for trailing stop performance
        
        Args:
            trailing_stops_df: DataFrame from calculate_trailing_stops_series
            
        Returns:
            Dictionary with stop statistics
        """
        # Filter periods with positions
        in_position = trailing_stops_df[trailing_stops_df['Position'] != 0].copy()
        
        if len(in_position) == 0:
            return {'no_positions': True}
        
        # Count stops hit
        stops_hit = (trailing_stops_df['Stop_Hit'] == True).sum()
        
        # Position statistics
        long_periods = (in_position['Position'] == 1).sum()
        short_periods = (in_position['Position'] == -1).sum()
        
        # Stop distance statistics
        avg_stop_distance = in_position['Stop_Distance_Pct'].mean()
        max_stop_distance = in_position['Stop_Distance_Pct'].max()
        min_stop_distance = in_position['Stop_Distance_Pct'].min()
        
        # ATR statistics during positions
        avg_atr_in_position = in_position['ATR'].mean()
        avg_trail_distance = in_position['Trail_Distance'].mean()
        
        return {
            'total_position_periods': len(in_position),
            'long_periods': long_periods,
            'short_periods': short_periods,
            'stops_hit': stops_hit,
            'stop_hit_rate': stops_hit / len(in_position) * 100 if len(in_position) > 0 else 0,
            'avg_stop_distance_pct': avg_stop_distance,
            'max_stop_distance_pct': max_stop_distance,
            'min_stop_distance_pct': min_stop_distance,
            'avg_atr_in_position': avg_atr_in_position,
            'avg_trail_distance': avg_trail_distance,
            'atr_multiplier': self.atr_multiplier,
            'initial_multiplier': self.initial_stop_multiplier
        }

def test_atr_trailing_stop():
    """Test the ATR Trailing Stop implementation"""
    print("🧪 Testing ATR Trailing Stop System")
    print("=" * 40)
    
    # Create sample data with trend
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    
    # Generate realistic trending price data
    base_price = 50000
    trend = np.linspace(0, 2000, 100)  # Upward trend
    noise = np.random.randn(100) * 200
    close_prices = base_price + trend + noise
    
    high_prices = close_prices + np.random.uniform(50, 150, 100)
    low_prices = close_prices - np.random.uniform(50, 150, 100)
    open_prices = close_prices + np.random.randn(100) * 50
    
    df = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': np.random.uniform(1000, 5000, 100)
    }, index=dates)
    
    # Create entry/exit signals (buy at start, hold, then exit)
    entry_signals = pd.Series(np.zeros(100), index=dates)
    exit_signals = pd.Series(np.zeros(100), index=dates)
    
    entry_signals.iloc[10] = 1  # Long entry
    exit_signals.iloc[80] = 1   # Exit
    
    # Initialize ATR trailing stop
    atr_stop = ATRTrailingStop(atr_period=14, atr_multiplier=2.0)
    
    # Calculate trailing stops
    result = atr_stop.calculate_trailing_stops_series(df, entry_signals, exit_signals)
    
    # Get statistics
    stats = atr_stop.get_stop_statistics(result)
    
    # Display results
    print(f"📊 ATR Trailing Stop Analysis:")
    print(f"   Data points: {len(result)}")
    print(f"   ATR Period: {atr_stop.atr_period}")
    print(f"   ATR Multiplier: {atr_stop.atr_multiplier}")
    print(f"   Initial Stop Multiplier: {atr_stop.initial_stop_multiplier}")
    
    print(f"\n📈 Position Statistics:")
    if not stats.get('no_positions', False):
        print(f"   Total position periods: {stats['total_position_periods']}")
        print(f"   Long periods: {stats['long_periods']}")
        print(f"   Short periods: {stats['short_periods']}")
        print(f"   Stops hit: {stats['stops_hit']}")
        print(f"   Stop hit rate: {stats['stop_hit_rate']:.1f}%")
        
        print(f"\n💰 Stop Distance Analysis:")
        print(f"   Average stop distance: {stats['avg_stop_distance_pct']:.2f}%")
        print(f"   Maximum stop distance: {stats['max_stop_distance_pct']:.2f}%")
        print(f"   Minimum stop distance: {stats['min_stop_distance_pct']:.2f}%")
        
        print(f"\n🎯 ATR Analysis:")
        print(f"   Average ATR in position: ${stats['avg_atr_in_position']:.2f}")
        print(f"   Average trail distance: ${stats['avg_trail_distance']:.2f}")
    else:
        print("   No positions found")
    
    # Show sample of trailing stop evolution
    position_periods = result[result['Position'] != 0]
    if len(position_periods) > 0:
        print(f"\n📋 Trailing Stop Evolution (first 10 position periods):")
        sample = position_periods.head(10)
        for idx, row in sample.iterrows():
            print(f"   {idx.strftime('%m-%d %H:%M')}: Price ${row['Price']:>7.0f}, "
                  f"Stop ${row['Stop_Loss']:>7.0f}, Distance {row['Stop_Distance_Pct']:>5.2f}%")
    
    return result, stats

if __name__ == "__main__":
    test_atr_trailing_stop()