#!/usr/bin/env python3
"""
Arthur Hill Trend Composite Strategy with ATR Trailing Stops
1-Hour Timeframe BTCUSDT Strategy

Strategy Components:
1. Arthur Hill's Trend Composite (5 indicators: MA, CCI, BB, Keltner, Stoch)
2. ATR Trailing Stop Loss System
3. Volume and volatility filters
4. Risk management with position sizing

Entry Conditions:
- Trend Composite >= +3 (Strong Bullish) for long
- Trend Composite <= -3 (Strong Bearish) for short
- Volume confirmation
- Trend quality filters

Exit Conditions:
- ATR Trailing Stop hit
- Trend Composite reversal
- Risk management stops
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'indicators'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_fetcher import BTCDataFetcher
from arthur_hill_trend_composite import ArthurHillTrendComposite
from atr_trailing_stop import ATRTrailingStop
from typing import Optional, Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class ArthurHillTrendStrategy:
    """
    Arthur Hill Trend Composite Strategy with ATR Trailing Stops
    1-Hour BTCUSDT Trading Strategy
    """
    
    def __init__(self, 
                 account_size: float = 10000,
                 risk_profile: str = 'moderate'):
        """
        Initialize Arthur Hill Trend Strategy
        
        Args:
            account_size: Trading capital
            risk_profile: 'conservative', 'moderate', 'aggressive'
        """
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.risk_profile = risk_profile
        
        # Initialize components
        self.data_fetcher = BTCDataFetcher()
        
        # Strategy parameters based on risk profile
        self._init_strategy_parameters()
        
        # Initialize indicators
        self.trend_indicator = ArthurHillTrendComposite(
            ma_period=self.ma_period,
            cci_period=self.cci_period,
            bb_period=self.bb_period,
            keltner_period=self.keltner_period
        )
        
        self.trailing_stop = ATRTrailingStop(
            atr_period=self.atr_period,
            atr_multiplier=self.atr_multiplier,
            initial_stop_multiplier=self.initial_stop_multiplier
        )
        
        # Trading state
        self.trades = []
        self.current_position = 0  # 0: no position, 1: long, -1: short
        self.current_entry_price = 0
        self.current_stop_loss = 0
        self.position_size = 0
        
        # Performance tracking
        self.equity_curve = []
        self.daily_pnl = []
        self.trend_composite_history = []
        self.stop_history = []
        
        # Risk monitoring
        self.max_balance = account_size
        self.max_drawdown = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        print(f"🎯 ARTHUR HILL TREND COMPOSITE STRATEGY ({risk_profile.upper()})")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"📊 Trend Entry Threshold: ±{self.trend_entry_threshold}")
        print(f"🛡️ ATR Trailing Stop: {self.atr_multiplier}x ATR")
        print(f"⏰ Timeframe: 1-Hour")
        
    def _init_strategy_parameters(self):
        """Initialize strategy parameters based on risk profile"""
        
        # Risk profile configurations
        configs = {
            'conservative': {
                'trend_entry_threshold': 4,      # Require very strong signals
                'trend_exit_threshold': 1,       # Exit on weak reversal
                'position_size_pct': 0.15,       # 15% position size
                'max_position_size_pct': 0.25,   # Max 25% per trade
                'volume_threshold_pct': 1.5,     # Require 150% avg volume
                'atr_multiplier': 2.5,           # Conservative trailing stop
                'initial_stop_multiplier': 3.0,  # Wider initial stop
                'ma_period': 50,                 # Longer MA for smoother signals
                'max_daily_loss_pct': 3.0
            },
            'moderate': {
                'trend_entry_threshold': 3,      # Strong signals
                'trend_exit_threshold': 0,       # Exit on neutral
                'position_size_pct': 0.20,       # 20% position size
                'max_position_size_pct': 0.35,   # Max 35% per trade
                'volume_threshold_pct': 1.2,     # Require 120% avg volume
                'atr_multiplier': 2.0,           # Moderate trailing stop
                'initial_stop_multiplier': 2.5,  # Moderate initial stop
                'ma_period': 40,                 # Balanced MA period
                'max_daily_loss_pct': 4.0
            },
            'aggressive': {
                'trend_entry_threshold': 2,      # Moderate signals
                'trend_exit_threshold': -1,      # Exit on opposite signal
                'position_size_pct': 0.25,       # 25% position size
                'max_position_size_pct': 0.50,   # Max 50% per trade
                'volume_threshold_pct': 1.1,     # Require 110% avg volume
                'atr_multiplier': 1.5,           # Tight trailing stop
                'initial_stop_multiplier': 2.0,  # Tighter initial stop
                'ma_period': 30,                 # Shorter MA for faster signals
                'max_daily_loss_pct': 5.0
            }
        }
        
        config = configs[self.risk_profile]
        
        # Set parameters
        self.trend_entry_threshold = config['trend_entry_threshold']
        self.trend_exit_threshold = config['trend_exit_threshold']
        self.position_size_pct = config['position_size_pct']
        self.max_position_size_pct = config['max_position_size_pct']
        self.volume_threshold_pct = config['volume_threshold_pct']
        self.atr_multiplier = config['atr_multiplier']
        self.initial_stop_multiplier = config['initial_stop_multiplier']
        self.ma_period = config['ma_period']
        self.max_daily_loss_pct = config['max_daily_loss_pct']
        
        # Fixed indicator periods (optimized for 1h timeframe)
        self.cci_period = 20
        self.bb_period = 20
        self.keltner_period = 20
        self.atr_period = 14
        self.volume_sma_period = 20
        
        # Risk limits
        self.max_daily_loss = self.account_size * self.max_daily_loss_pct / 100
        self.max_position_size = self.account_size * self.max_position_size_pct / 100
        
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators for the strategy"""
        
        # Calculate Trend Composite
        trend_data = self.trend_indicator.calculate_trend_composite(df)
        
        # Add trend data to main dataframe
        for col in trend_data.columns:
            df[col] = trend_data[col]
        
        # Calculate ATR (needed for position sizing and stops)
        atr = self.trailing_stop.calculate_atr(df)
        df['ATR'] = atr
        
        # Calculate volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=self.volume_sma_period).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Calculate volatility metrics
        df['Price_Change_Pct'] = df['Close'].pct_change() * 100
        df['Volatility'] = df['Price_Change_Pct'].rolling(window=20).std()
        
        return df
        
    def should_enter_long(self, df: pd.DataFrame, idx: int) -> bool:
        """Check if conditions are met for long entry"""
        if idx < max(self.ma_period, self.volume_sma_period):
            return False
            
        current_data = df.iloc[idx]
        
        # Primary signal: Trend Composite >= threshold
        if current_data['Trend_Composite'] < self.trend_entry_threshold:
            return False
        
        # Volume confirmation
        if current_data['Volume_Ratio'] < self.volume_threshold_pct:
            return False
        
        # Trend quality check
        trend_quality = self.trend_indicator.get_trend_quality(df, idx, lookback=10)
        if trend_quality['consistency'] < 0.6:  # Require 60% consistency
            return False
        
        # Don't enter if volatility is too extreme
        if current_data['Volatility'] > 5.0:  # > 5% volatility
            return False
            
        return True
    
    def should_enter_short(self, df: pd.DataFrame, idx: int) -> bool:
        """Check if conditions are met for short entry"""
        if idx < max(self.ma_period, self.volume_sma_period):
            return False
            
        current_data = df.iloc[idx]
        
        # Primary signal: Trend Composite <= -threshold
        if current_data['Trend_Composite'] > -self.trend_entry_threshold:
            return False
        
        # Volume confirmation
        if current_data['Volume_Ratio'] < self.volume_threshold_pct:
            return False
        
        # Trend quality check
        trend_quality = self.trend_indicator.get_trend_quality(df, idx, lookback=10)
        if trend_quality['consistency'] < 0.6:  # Require 60% consistency
            return False
        
        # Don't enter if volatility is too extreme
        if current_data['Volatility'] > 5.0:  # > 5% volatility
            return False
            
        return True
    
    def should_exit_position(self, df: pd.DataFrame, idx: int) -> Tuple[bool, str]:
        """Check if current position should be exited"""
        if self.current_position == 0:
            return False, ""
        
        current_data = df.iloc[idx]
        current_price = current_data['Close']
        
        # Check ATR trailing stop
        stop_hit = self.trailing_stop.check_stop_hit(
            current_price, self.current_stop_loss, self.current_position
        )
        if stop_hit:
            return True, "ATR_Stop"
        
        # Check trend reversal
        trend_score = current_data['Trend_Composite']
        
        if self.current_position > 0:  # Long position
            if trend_score <= self.trend_exit_threshold:
                return True, "Trend_Reversal"
        else:  # Short position
            if trend_score >= -self.trend_exit_threshold:
                return True, "Trend_Reversal"
        
        # Emergency exit on extreme adverse movement (5% against position)
        if self.current_position > 0 and current_price < self.current_entry_price * 0.95:
            return True, "Emergency_Stop"
        elif self.current_position < 0 and current_price > self.current_entry_price * 1.05:
            return True, "Emergency_Stop"
        
        return False, ""
    
    def calculate_position_size(self, current_price: float, atr: float) -> float:
        """Calculate position size based on risk and ATR"""
        
        # Base position size as percentage of account
        base_position_value = self.current_balance * self.position_size_pct
        
        # Risk-based sizing: don't risk more than 2% of account on initial stop
        initial_stop_distance = atr * self.initial_stop_multiplier
        risk_amount = self.current_balance * 0.02  # 2% risk
        risk_based_size = risk_amount / initial_stop_distance
        risk_based_value = risk_based_size * current_price
        
        # Use the larger of the two approaches for meaningful position sizes
        position_value = max(base_position_value, risk_based_value)
        
        # Ensure we don't exceed max position size
        position_value = min(position_value, self.max_position_size)
        
        # Ensure minimum meaningful position (at least $50)
        position_value = max(position_value, 50.0)
        
        # Convert to number of units
        position_size = position_value / current_price
        
        return position_size
    
    def enter_position(self, df: pd.DataFrame, idx: int, direction: int):
        """Enter a new position"""
        current_data = df.iloc[idx]
        entry_price = current_data['Close']
        current_atr = current_data['ATR']
        
        # Calculate position size
        position_size = self.calculate_position_size(entry_price, current_atr)
        
        if position_size <= 0:
            return
        
        # Set position
        self.current_position = direction
        self.current_entry_price = entry_price
        self.position_size = position_size
        
        # Initialize ATR trailing stop
        self.current_stop_loss = self.trailing_stop.initialize_stop(
            entry_price, direction, current_atr
        )
        
        # Record trade entry
        trade_entry = {
            'entry_time': df.index[idx],
            'entry_price': entry_price,
            'direction': 'long' if direction > 0 else 'short',
            'position_size': position_size,
            'position_value': position_size * entry_price,
            'trend_composite': current_data['Trend_Composite'],
            'atr': current_atr,
            'initial_stop': self.current_stop_loss,
            'volume_ratio': current_data['Volume_Ratio']
        }
        
        self.trades.append(trade_entry)
        
    def exit_position(self, df: pd.DataFrame, idx: int, exit_reason: str):
        """Exit current position"""
        if self.current_position == 0 or not self.trades:
            return
            
        current_data = df.iloc[idx]
        exit_price = current_data['Close']
        
        # Calculate P&L
        if self.current_position > 0:  # Long position
            pnl = (exit_price - self.current_entry_price) * self.position_size
        else:  # Short position
            pnl = (self.current_entry_price - exit_price) * self.position_size
        
        # Update balance
        self.current_balance += pnl
        self.max_balance = max(self.max_balance, self.current_balance)
        
        # Update trade record
        current_trade = self.trades[-1]
        current_trade['exit_time'] = df.index[idx]
        current_trade['exit_price'] = exit_price
        current_trade['exit_reason'] = exit_reason
        current_trade['pnl'] = pnl
        current_trade['return_pct'] = (pnl / current_trade['position_value']) * 100
        current_trade['bars_held'] = idx - df.index.get_loc(current_trade['entry_time'])
        
        # Track consecutive wins/losses
        if pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Reset position
        self.current_position = 0
        self.current_entry_price = 0
        self.current_stop_loss = 0
        self.position_size = 0
    
    def update_trailing_stop(self, df: pd.DataFrame, idx: int):
        """Update ATR trailing stop for current position"""
        if self.current_position == 0:
            return
        
        current_data = df.iloc[idx]
        current_price = current_data['Close']
        current_atr = current_data['ATR']
        
        # Update trailing stop
        self.current_stop_loss = self.trailing_stop.update_trailing_stop(
            current_price, current_atr, self.current_position, self.current_stop_loss
        )
        
        # Record stop level
        self.stop_history.append({
            'time': df.index[idx],
            'price': current_price,
            'stop': self.current_stop_loss,
            'distance_pct': abs(self.current_stop_loss - current_price) / current_price * 100
        })
    
    def run_backtest(self, 
                    start_date: str = "2024-01-01", 
                    end_date: str = "2024-06-01") -> Optional[pd.DataFrame]:
        """Run Arthur Hill Trend Strategy backtest"""
        
        print(f"\n🎯 ARTHUR HILL TREND COMPOSITE BACKTEST")
        print("=" * 50)
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"🎪 Strategy: Trend Composite + ATR Trailing Stops")
        
        # Fetch data
        df = self.data_fetcher.fetch_btc_data(start_date, end_date, "1h")
        if df is None or df.empty:
            print("❌ Failed to fetch data")
            return None
        
        print(f"✅ Data loaded: {len(df)} periods")
        
        # Calculate all indicators
        print("🔧 Calculating indicators...")
        df = self.calculate_all_indicators(df)
        
        # Reset state
        self._reset_state()
        
        # Run simulation
        print("📈 Running Arthur Hill strategy simulation...")
        
        for i in range(max(self.ma_period, self.volume_sma_period), len(df)):
            current_data = df.iloc[i]
            
            # Update equity curve
            self.equity_curve.append(self.current_balance)
            
            # Update trailing stop if in position
            if self.current_position != 0:
                self.update_trailing_stop(df, i)
                
                # Check for exit
                should_exit, exit_reason = self.should_exit_position(df, i)
                if should_exit:
                    self.exit_position(df, i, exit_reason)
            
            # Check for new entries (only if not in position)
            if self.current_position == 0:
                if self.should_enter_long(df, i):
                    self.enter_position(df, i, 1)  # Long
                elif self.should_enter_short(df, i):
                    self.enter_position(df, i, -1)  # Short
            
            # Record trend composite history
            self.trend_composite_history.append({
                'time': df.index[i],
                'trend_composite': current_data['Trend_Composite'],
                'trend_strength': current_data['Trend_Strength']
            })
            
            # Check daily loss limit
            if self._check_daily_loss_limit():
                print("⚠️ Daily loss limit reached, stopping trading")
                break
        
        # Close any open position
        if self.current_position != 0:
            self.exit_position(df, len(df)-1, "End_of_Period")
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
        
        # Print results
        self._print_results()
        
        return df
    
    def _reset_state(self):
        """Reset all state variables for new backtest"""
        self.current_balance = self.initial_balance
        self.trades = []
        self.current_position = 0
        self.current_entry_price = 0
        self.current_stop_loss = 0
        self.position_size = 0
        self.equity_curve = []
        self.daily_pnl = []
        self.trend_composite_history = []
        self.stop_history = []
        self.max_balance = self.initial_balance
        self.max_drawdown = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
    
    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached"""
        daily_loss = self.initial_balance - self.current_balance
        return daily_loss >= self.max_daily_loss
    
    def _calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return
        
        # Filter completed trades
        completed_trades = [t for t in self.trades if 'pnl' in t]
        if not completed_trades:
            return
        
        # Basic metrics
        total_return = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        total_pnl = sum([t['pnl'] for t in completed_trades])
        
        # Trade statistics
        win_trades = [t for t in completed_trades if t['pnl'] > 0]
        loss_trades = [t for t in completed_trades if t['pnl'] <= 0]
        
        self.win_rate = len(win_trades) / len(completed_trades) * 100
        self.total_return = total_return
        self.total_trades = len(completed_trades)
        
        # P&L statistics
        if win_trades:
            self.avg_win = np.mean([t['pnl'] for t in win_trades])
            self.largest_win = max([t['pnl'] for t in win_trades])
        else:
            self.avg_win = 0
            self.largest_win = 0
            
        if loss_trades:
            self.avg_loss = np.mean([t['pnl'] for t in loss_trades])
            self.largest_loss = min([t['pnl'] for t in loss_trades])
        else:
            self.avg_loss = 0
            self.largest_loss = 0
        
        # Profit factor
        gross_profit = sum([t['pnl'] for t in win_trades]) if win_trades else 0
        gross_loss = abs(sum([t['pnl'] for t in loss_trades])) if loss_trades else 1
        self.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Drawdown calculation
        equity_series = pd.Series(self.equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        self.max_drawdown = abs(drawdown.min())
    
    def _print_results(self):
        """Print comprehensive backtest results"""
        print(f"\n🏆 ARTHUR HILL TREND STRATEGY RESULTS")
        print("=" * 50)
        print(f"Initial Balance:        ${self.initial_balance:,.2f}")
        print(f"Final Balance:          ${self.current_balance:,.2f}")
        print(f"Total Return:           {self.total_return:+.2f}%")
        print(f"Max Drawdown:           {self.max_drawdown:.2f}%")
        
        print(f"\n📊 TRADING PERFORMANCE:")
        print(f"Total Trades:           {self.total_trades}")
        print(f"Win Rate:               {self.win_rate:.1f}%")
        print(f"Profit Factor:          {self.profit_factor:.2f}")
        
        if hasattr(self, 'avg_win') and self.avg_win > 0:
            print(f"Average Win:            ${self.avg_win:,.2f}")
            print(f"Largest Win:            ${self.largest_win:,.2f}")
        
        if hasattr(self, 'avg_loss') and self.avg_loss < 0:
            print(f"Average Loss:           ${self.avg_loss:,.2f}")
            print(f"Largest Loss:           ${self.largest_loss:,.2f}")
        
        # Strategy-specific metrics
        if self.trades:
            # Trend composite analysis
            trend_scores = [t.get('trend_composite', 0) for t in self.trades]
            avg_entry_strength = np.mean(trend_scores) if trend_scores else 0
            
            # Exit reason analysis
            exit_reasons = {}
            for trade in self.trades:
                if 'exit_reason' in trade:
                    reason = trade['exit_reason']
                    exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
            
            print(f"\n🎯 STRATEGY ANALYSIS:")
            print(f"Average Entry Strength:  {avg_entry_strength:.1f}")
            print(f"Entry Threshold:         ±{self.trend_entry_threshold}")
            print(f"ATR Multiplier:          {self.atr_multiplier}x")
            
            print(f"\n🚪 EXIT ANALYSIS:")
            for reason, count in exit_reasons.items():
                pct = count / len(self.trades) * 100
                print(f"{reason.replace('_', ' '):<20}: {count:>3} ({pct:>5.1f}%)")
        
        # Risk analysis
        print(f"\n🛡️ RISK ANALYSIS:")
        print(f"Max Daily Loss Limit:   ${self.max_daily_loss:,.2f} ({self.max_daily_loss_pct}%)")
        print(f"Max Position Size:      ${self.max_position_size:,.2f} ({self.max_position_size_pct}%)")
        print(f"Consecutive Wins:       {self.consecutive_wins}")
        print(f"Consecutive Losses:     {self.consecutive_losses}")

def main():
    """Test Arthur Hill Trend Strategy"""
    print("🧪 Testing Arthur Hill Trend Composite Strategy")
    print("=" * 55)
    
    # Test different risk profiles
    profiles = ['conservative', 'moderate', 'aggressive']
    
    results = {}
    
    for profile in profiles:
        print(f"\n🎯 Testing {profile.upper()} Profile:")
        
        strategy = ArthurHillTrendStrategy(
            account_size=10000, 
            risk_profile=profile
        )
        
        # Run backtest
        result = strategy.run_backtest("2024-01-01", "2024-04-01")
        
        if result is not None:
            results[profile] = {
                'total_return': getattr(strategy, 'total_return', 0),
                'win_rate': getattr(strategy, 'win_rate', 0),
                'total_trades': getattr(strategy, 'total_trades', 0),
                'max_drawdown': getattr(strategy, 'max_drawdown', 0),
                'profit_factor': getattr(strategy, 'profit_factor', 0)
            }
    
    # Compare results
    if results:
        print(f"\n📊 PROFILE COMPARISON:")
        print("=" * 80)
        print(f"{'Profile':<12} {'Return':<8} {'Trades':<7} {'Win Rate':<9} {'PF':<5} {'Drawdown'}")
        print("-" * 80)
        
        for profile, metrics in results.items():
            print(f"{profile.title():<12} "
                  f"{metrics['total_return']:>+6.1f}% "
                  f"{metrics['total_trades']:>6} "
                  f"{metrics['win_rate']:>7.1f}% "
                  f"{metrics['profit_factor']:>4.1f} "
                  f"{metrics['max_drawdown']:>7.1f}%")
    
    print(f"\n🎉 Arthur Hill Trend Strategy Testing Complete!")
    return results

if __name__ == "__main__":
    main()