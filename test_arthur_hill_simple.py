"""
Arthur Hill Trend Strategy - Simplified 24 Month Backtest
Adapts the Arthur Hill Trend Composite strategy for 24-month testing
Period: August 2023 to July 2025 (24 months)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class ArthurHillTrendSimplified:
    """
    Simplified Arthur Hill Trend Strategy for 24-month backtesting
    Uses Trend Composite scoring with ATR trailing stops
    """
    
    def __init__(self, account_size=100000, risk_profile='moderate'):
        """Initialize Arthur Hill Trend Strategy"""
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.risk_profile = risk_profile
        
        # Strategy parameters based on risk profile
        self._init_strategy_parameters()
        
        # Trading state
        self.trades = []
        self.current_position = 0  # 0: no position, 1: long, -1: short
        self.current_entry_price = 0
        self.current_stop_loss = 0
        self.position_size = 0
        
        # Performance tracking
        self.equity_curve = []
        self.monthly_summaries = []
        self.current_month = None
        self.monthly_starting_balance = account_size
        self.monthly_trades = 0
        
        print(f"🎯 ARTHUR HILL TREND STRATEGY - {risk_profile.upper()}")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"📊 Trend Threshold: ±{self.trend_entry_threshold}")
        print(f"🛡️ ATR Multiplier: {self.atr_multiplier}x")
    
    def _init_strategy_parameters(self):
        """Initialize strategy parameters based on risk profile"""
        
        configs = {
            'conservative': {
                'trend_entry_threshold': 4,      # Very strong signals only
                'trend_exit_threshold': 1,       # Exit on weak reversal
                'position_size_pct': 0.15,       # 15% position size
                'volume_threshold': 1.5,         # 150% avg volume required
                'atr_multiplier': 2.5,           # Conservative trailing stop
                'max_daily_loss_pct': 3.0,       # 3% daily loss limit
                'ma_period': 50
            },
            'moderate': {
                'trend_entry_threshold': 3,      # Strong signals
                'trend_exit_threshold': 0,       # Exit on neutral
                'position_size_pct': 0.20,       # 20% position size
                'volume_threshold': 1.2,         # 120% avg volume required
                'atr_multiplier': 2.0,           # Moderate trailing stop
                'max_daily_loss_pct': 4.0,       # 4% daily loss limit
                'ma_period': 40
            },
            'aggressive': {
                'trend_entry_threshold': 2,      # Moderate signals
                'trend_exit_threshold': -1,      # Exit on opposite signal
                'position_size_pct': 0.25,       # 25% position size
                'volume_threshold': 1.1,         # 110% avg volume required
                'atr_multiplier': 1.5,           # Tight trailing stop
                'max_daily_loss_pct': 5.0,       # 5% daily loss limit
                'ma_period': 30
            }
        }
        
        config = configs[self.risk_profile]
        
        # Set parameters
        for key, value in config.items():
            setattr(self, key, value)
    
    def fetch_bitcoin_data(self, start_date, end_date):
        """Fetch Bitcoin data from Yahoo Finance"""
        print(f"📊 Fetching BTC-USD data from {start_date} to {end_date}")
        
        try:
            ticker = yf.Ticker("BTC-USD")
            df = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if df.empty:
                print("❌ No data available from Yahoo Finance")
                return None
            
            print(f"✅ Downloaded {len(df)} daily periods")
            print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"   Price range: ${df['Close'].min():,.0f} - ${df['Close'].max():,.0f}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def calculate_arthur_hill_indicators(self, df):
        """
        Calculate Arthur Hill Trend Composite indicators
        Composite of 5 indicators: MA, CCI, Bollinger Bands, Keltner Channels, Stochastic
        """
        print("🔧 Calculating Arthur Hill Trend Composite indicators...")
        
        # 1. Moving Average Component (+/-1 point)
        df['MA'] = df['Close'].rolling(window=self.ma_period).mean()
        df['MA_Signal'] = 0
        df.loc[df['Close'] > df['MA'], 'MA_Signal'] = 1
        df.loc[df['Close'] < df['MA'], 'MA_Signal'] = -1
        
        # 2. CCI Component (+/-1 point)
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=False)
        df['CCI'] = (tp - sma_tp) / (0.015 * mad)
        df['CCI_Signal'] = 0
        df.loc[df['CCI'] > 100, 'CCI_Signal'] = 1
        df.loc[df['CCI'] < -100, 'CCI_Signal'] = -1
        
        # 3. Bollinger Bands Component (+/-1 point)
        bb_period = 20
        df['BB_Middle'] = df['Close'].rolling(window=bb_period).mean()
        bb_std = df['Close'].rolling(window=bb_period).std()
        df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
        df['BB_Signal'] = 0
        df.loc[df['Close'] > df['BB_Middle'], 'BB_Signal'] = 1
        df.loc[df['Close'] < df['BB_Middle'], 'BB_Signal'] = -1
        
        # 4. Keltner Channels Component (+/-1 point)
        kc_period = 20
        df['KC_Middle'] = df['Close'].ewm(span=kc_period).mean()
        
        # Calculate ATR for Keltner Channels
        df['H-L'] = df['High'] - df['Low']
        df['H-C'] = abs(df['High'] - df['Close'].shift(1))
        df['L-C'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()
        
        df['KC_Upper'] = df['KC_Middle'] + (2 * df['ATR'])
        df['KC_Lower'] = df['KC_Middle'] - (2 * df['ATR'])
        df['KC_Signal'] = 0
        df.loc[df['Close'] > df['KC_Middle'], 'KC_Signal'] = 1
        df.loc[df['Close'] < df['KC_Middle'], 'KC_Signal'] = -1
        
        # 5. Stochastic Component (+/-1 point)
        stoch_period = 14
        df['Lowest_Low'] = df['Low'].rolling(window=stoch_period).min()
        df['Highest_High'] = df['High'].rolling(window=stoch_period).max()
        df['%K'] = 100 * ((df['Close'] - df['Lowest_Low']) / (df['Highest_High'] - df['Lowest_Low']))
        df['%D'] = df['%K'].rolling(window=3).mean()
        df['Stoch_Signal'] = 0
        df.loc[df['%K'] > 50, 'Stoch_Signal'] = 1
        df.loc[df['%K'] < 50, 'Stoch_Signal'] = -1
        
        # Calculate Trend Composite (-5 to +5)
        df['Trend_Composite'] = (df['MA_Signal'] + df['CCI_Signal'] + 
                                df['BB_Signal'] + df['KC_Signal'] + df['Stoch_Signal'])
        
        # Calculate volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Calculate trend strength (absolute value)
        df['Trend_Strength'] = abs(df['Trend_Composite'])
        
        print(f"✅ Calculated Arthur Hill indicators")
        print(f"   Trend Composite range: {df['Trend_Composite'].min()} to {df['Trend_Composite'].max()}")
        
        return df
    
    def should_enter_long(self, current_data):
        """Check if conditions are met for long entry"""
        return (current_data['Trend_Composite'] >= self.trend_entry_threshold and
                current_data['Volume_Ratio'] >= self.volume_threshold)
    
    def should_enter_short(self, current_data):
        """Check if conditions are met for short entry"""
        return (current_data['Trend_Composite'] <= -self.trend_entry_threshold and
                current_data['Volume_Ratio'] >= self.volume_threshold)
    
    def should_exit_position(self, current_data):
        """Check if current position should be exited"""
        if self.current_position == 0:
            return False, ""
        
        current_price = current_data['Close']
        
        # Check ATR trailing stop
        if self.current_position > 0:  # Long position
            if current_price <= self.current_stop_loss:
                return True, "ATR_Stop"
            # Check trend reversal
            if current_data['Trend_Composite'] <= self.trend_exit_threshold:
                return True, "Trend_Reversal"
        else:  # Short position
            if current_price >= self.current_stop_loss:
                return True, "ATR_Stop"
            # Check trend reversal
            if current_data['Trend_Composite'] >= -self.trend_exit_threshold:
                return True, "Trend_Reversal"
        
        return False, ""
    
    def calculate_position_size(self, current_price, atr):
        """Calculate position size based on risk and ATR"""
        # Base position size as percentage of account
        base_position_value = self.current_balance * self.position_size_pct
        
        # Risk-based sizing: don't risk more than 2% of account
        risk_amount = self.current_balance * 0.02
        initial_stop_distance = atr * 2.5  # Initial stop distance
        risk_based_size = risk_amount / initial_stop_distance
        risk_based_value = risk_based_size * current_price
        
        # Use the smaller of the two for safer sizing
        position_value = min(base_position_value, risk_based_value)
        
        # Ensure minimum meaningful position
        position_value = max(position_value, 100.0)
        
        return position_value / current_price
    
    def enter_position(self, current_data, direction, timestamp):
        """Enter a new position"""
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
        if direction > 0:  # Long
            self.current_stop_loss = entry_price - (current_atr * 2.5)
        else:  # Short
            self.current_stop_loss = entry_price + (current_atr * 2.5)
        
        # Record trade entry
        trade_entry = {
            'entry_time': timestamp,
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
    
    def exit_position(self, current_data, exit_reason, timestamp):
        """Exit current position"""
        if self.current_position == 0 or not self.trades:
            return
        
        exit_price = current_data['Close']
        
        # Calculate P&L
        if self.current_position > 0:  # Long position
            pnl = (exit_price - self.current_entry_price) * self.position_size
        else:  # Short position
            pnl = (self.current_entry_price - exit_price) * self.position_size
        
        # Update balance
        self.current_balance += pnl
        
        # Update trade record
        current_trade = self.trades[-1]
        current_trade['exit_time'] = timestamp
        current_trade['exit_price'] = exit_price
        current_trade['exit_reason'] = exit_reason
        current_trade['pnl'] = pnl
        current_trade['return_pct'] = (pnl / current_trade['position_value']) * 100
        
        # Update monthly trades counter
        self.monthly_trades += 1
        
        # Reset position
        self.current_position = 0
        self.current_entry_price = 0
        self.current_stop_loss = 0
        self.position_size = 0
        
        # Print trade result
        result = "WIN" if pnl > 0 else "LOSS"
        emoji = "✅" if pnl > 0 else "❌"
        print(f"{emoji} {result}: ${pnl:+,.0f} ({current_trade['return_pct']:+.1f}%) - {exit_reason}")
    
    def update_trailing_stop(self, current_data):
        """Update ATR trailing stop for current position"""
        if self.current_position == 0:
            return
        
        current_price = current_data['Close']
        current_atr = current_data['ATR']
        
        if self.current_position > 0:  # Long position
            new_stop = current_price - (current_atr * self.atr_multiplier)
            self.current_stop_loss = max(self.current_stop_loss, new_stop)
        else:  # Short position
            new_stop = current_price + (current_atr * self.atr_multiplier)
            self.current_stop_loss = min(self.current_stop_loss, new_stop)
    
    def _complete_monthly_summary(self, current_date):
        """Complete monthly summary and add to tracking"""
        if self.current_month is None:
            return
        
        # Calculate monthly P&L
        monthly_ending_balance = self.current_balance
        monthly_pnl_amount = monthly_ending_balance - self.monthly_starting_balance
        monthly_pnl_percentage = (monthly_pnl_amount / self.monthly_starting_balance) * 100
        
        # Create monthly summary
        monthly_summary = {
            'month': self.current_month,
            'starting_balance': round(self.monthly_starting_balance, 2),
            'ending_balance': round(monthly_ending_balance, 2),
            'pnl': round(monthly_pnl_amount, 2),
            'pnl_pct': round(monthly_pnl_percentage, 2),
            'trades': self.monthly_trades
        }
        
        self.monthly_summaries.append(monthly_summary)
        
        # Reset for next month
        self.monthly_starting_balance = monthly_ending_balance
        self.monthly_trades = 0
    
    def run_backtest(self, start_date="2023-08-01", end_date="2025-07-31"):
        """Run Arthur Hill Trend Strategy backtest"""
        
        print(f"\\n🚀 ARTHUR HILL TREND STRATEGY - 24 MONTH BACKTEST")
        print("=" * 70)
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"🎯 Strategy: Arthur Hill Trend Composite + ATR Trailing Stops")
        
        # Fetch data
        df = self.fetch_bitcoin_data(start_date, end_date)
        if df is None or df.empty:
            print("❌ Failed to fetch data")
            return None
        
        # Calculate all indicators
        df = self.calculate_arthur_hill_indicators(df)
        
        # Reset state
        self.current_balance = self.initial_balance
        self.trades = []
        self.current_position = 0
        self.monthly_summaries = []
        self.current_month = None
        self.monthly_starting_balance = self.initial_balance
        self.monthly_trades = 0
        
        print("📈 Running Arthur Hill strategy simulation...")
        
        for i in range(50, len(df)):  # Start after indicator warm-up
            current_data = df.iloc[i]
            timestamp = df.index[i]
            
            # Update monthly tracking
            current_month_key = f"{timestamp.year}-{timestamp.month:02d}"
            if current_month_key != self.current_month:
                # Complete previous month
                if self.current_month is not None:
                    self._complete_monthly_summary(timestamp)
                
                # Start new month
                self.current_month = current_month_key
                self.monthly_starting_balance = self.current_balance
                self.monthly_trades = 0
            
            # Update trailing stop if in position
            if self.current_position != 0:
                self.update_trailing_stop(current_data)
                
                # Check for exit
                should_exit, exit_reason = self.should_exit_position(current_data)
                if should_exit:
                    self.exit_position(current_data, exit_reason, timestamp)
            
            # Check for new entries (only if not in position)
            if self.current_position == 0:
                if self.should_enter_long(current_data):
                    self.enter_position(current_data, 1, timestamp)  # Long
                    print(f"📈 LONG: ${current_data['Close']:,.0f} | Trend: {current_data['Trend_Composite']:+.0f} | Vol: {current_data['Volume_Ratio']:.1f}x")
                elif self.should_enter_short(current_data):
                    self.enter_position(current_data, -1, timestamp)  # Short
                    print(f"📉 SHORT: ${current_data['Close']:,.0f} | Trend: {current_data['Trend_Composite']:+.0f} | Vol: {current_data['Volume_Ratio']:.1f}x")
            
            # Update equity curve
            self.equity_curve.append(self.current_balance)
        
        # Complete final month
        if self.current_month is not None:
            self._complete_monthly_summary(df.index[-1])
        
        # Close any open position
        if self.current_position != 0:
            self.exit_position(df.iloc[-1], "End_of_Period", df.index[-1])
        
        return df
    
    def print_results(self):
        """Print comprehensive backtest results"""
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        print(f"\\n🏆 ARTHUR HILL TREND STRATEGY RESULTS")
        print("=" * 60)
        print(f"💰 Financial Performance:")
        print(f"   Initial Balance:     ${self.initial_balance:,.2f}")
        print(f"   Final Balance:       ${self.current_balance:,.2f}")
        print(f"   Total Return:        {profit_pct:+.2f}%")
        
        # Calculate max drawdown
        if self.equity_curve:
            equity_series = pd.Series(self.equity_curve)
            running_max = equity_series.expanding().max()
            drawdown = (equity_series - running_max) / running_max * 100
            max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0
            print(f"   Max Drawdown:        {max_drawdown:.2f}%")
        
        # Trade statistics
        completed_trades = [t for t in self.trades if 'pnl' in t]
        total_trades = len(completed_trades)
        
        print(f"\\n📊 Trading Performance:")
        print(f"   Total Trades:        {total_trades}")
        
        if total_trades > 0:
            win_trades = [t for t in completed_trades if t['pnl'] > 0]
            win_rate = len(win_trades) / total_trades * 100
            print(f"   Win Rate:            {win_rate:.1f}%")
            
            # Profit factor
            gross_profit = sum(t['pnl'] for t in win_trades)
            gross_loss = abs(sum(t['pnl'] for t in completed_trades if t['pnl'] < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            print(f"   Profit Factor:       {profit_factor:.2f}")
            
            # Average trade
            avg_trade = sum(t['pnl'] for t in completed_trades) / total_trades
            print(f"   Average Trade:       ${avg_trade:+,.0f}")
            
            if win_trades:
                avg_win = sum(t['pnl'] for t in win_trades) / len(win_trades)
                print(f"   Average Win:         ${avg_win:+,.0f}")
            
            loss_trades = [t for t in completed_trades if t['pnl'] < 0]
            if loss_trades:
                avg_loss = sum(t['pnl'] for t in loss_trades) / len(loss_trades)
                print(f"   Average Loss:        ${avg_loss:+,.0f}")
        
        # Strategy specifics
        print(f"\\n🎯 Strategy Settings:")
        print(f"   Risk Profile:        {self.risk_profile.title()}")
        print(f"   Trend Threshold:     ±{self.trend_entry_threshold}")
        print(f"   Position Size:       {self.position_size_pct*100:.1f}%")
        print(f"   ATR Multiplier:      {self.atr_multiplier}x")
        print(f"   Volume Threshold:    {self.volume_threshold}x")


def run_arthur_hill_comprehensive_test():
    """Run comprehensive Arthur Hill strategy test across risk profiles"""
    
    print("🎯 ARTHUR HILL TREND STRATEGY - Comprehensive 24 Month Test")
    print("📊 Testing across all risk profiles with real Bitcoin data")
    print("=" * 80)
    
    risk_profiles = ['conservative', 'moderate', 'aggressive']
    results = {}
    
    for risk_profile in risk_profiles:
        print(f"\\n📊 Testing {risk_profile.upper()} profile...")
        print("-" * 60)
        
        try:
            strategy = ArthurHillTrendSimplified(
                account_size=100000,
                risk_profile=risk_profile
            )
            
            # Run backtest
            df = strategy.run_backtest()
            
            if df is not None:
                strategy.print_results()
                results[risk_profile] = strategy
            else:
                print(f"❌ Backtest failed for {risk_profile}")
                results[risk_profile] = None
                
        except Exception as e:
            print(f"❌ Error testing {risk_profile}: {str(e)}")
            results[risk_profile] = None
    
    return results


def generate_arthur_hill_monthly_summaries(results):
    """Generate monthly summaries for Arthur Hill strategies"""
    
    print("\\n📅 ARTHUR HILL MONTHLY PERFORMANCE SUMMARIES")
    print("=" * 80)
    
    for risk_profile, strategy in results.items():
        if strategy is None:
            continue
        
        print(f"\\n🏆 {risk_profile.upper()} PROFILE - MONTHLY BREAKDOWN")
        print("-" * 70)
        
        if not strategy.monthly_summaries:
            print("❌ No monthly data available")
            continue
        
        # Summary table header
        print(f"{'Month':<10} {'Start Balance':<15} {'End Balance':<15} {'P&L':<12} {'P&L %':<8} {'Trades':<8}")
        print("-" * 80)
        
        total_pnl = 0
        profitable_months = 0
        
        for month_data in strategy.monthly_summaries:
            month = month_data['month']
            start_bal = month_data['starting_balance']
            end_bal = month_data['ending_balance']
            pnl = month_data['pnl']
            pnl_pct = month_data['pnl_pct']
            trades = month_data['trades']
            
            total_pnl += pnl
            if pnl > 0:
                profitable_months += 1
            
            # Format with emoji
            emoji = "📈" if pnl > 0 else "📉"
            
            print(f"{month:<10} ${start_bal:<14,.0f} ${end_bal:<14,.0f} ${pnl:<+11,.0f} {pnl_pct:<+7.2f}% {trades:<3} {emoji}")
        
        # Monthly statistics
        print("-" * 80)
        print(f"SUMMARY: Total P&L: ${total_pnl:+,.0f} | Profitable: {profitable_months}/{len(strategy.monthly_summaries)} ({profitable_months/len(strategy.monthly_summaries)*100:.1f}%)")


def generate_arthur_hill_comparison(results):
    """Generate comparison report for Arthur Hill strategies"""
    
    print("\\n📊 ARTHUR HILL COMPREHENSIVE COMPARISON")
    print("=" * 70)
    
    print(f"{'Risk Profile':<15} {'Total Return':<12} {'Max DD':<10} {'Win Rate':<10} {'Trades':<8} {'PF':<6}")
    print("-" * 70)
    
    best_performer = None
    best_return = float('-inf')
    
    for risk_profile, strategy in results.items():
        if strategy is None:
            print(f"{risk_profile.title():<15} {'FAILED':<12}")
            continue
        
        total_return = (strategy.current_balance - strategy.initial_balance) / strategy.initial_balance * 100
        
        # Calculate other metrics
        completed_trades = [t for t in strategy.trades if 'pnl' in t]
        total_trades = len(completed_trades)
        
        if total_trades > 0:
            win_trades = [t for t in completed_trades if t['pnl'] > 0]
            win_rate = len(win_trades) / total_trades * 100
            
            gross_profit = sum(t['pnl'] for t in win_trades)
            gross_loss = abs(sum(t['pnl'] for t in completed_trades if t['pnl'] < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999.99
        else:
            win_rate = 0
            profit_factor = 0
        
        # Simple max drawdown estimate
        if strategy.equity_curve:
            equity_series = pd.Series(strategy.equity_curve)
            running_max = equity_series.expanding().max()
            drawdown = (equity_series - running_max) / running_max * 100
            max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0
        else:
            max_drawdown = 0
        
        print(f"{risk_profile.title():<15} {total_return:<+11.2f}% {max_drawdown:<9.2f}% {win_rate:<9.1f}% {total_trades:<8} {profit_factor:<5.2f}")
        
        if total_return > best_return:
            best_return = total_return
            best_performer = risk_profile
    
    print("-" * 70)
    
    if best_performer:
        print(f"🏆 BEST PERFORMER: {best_performer.upper()} with {best_return:+.2f}% return")


def main():
    """Main execution function"""
    
    print("🎯 Arthur Hill Trend Strategy - 24 Month Comprehensive Analysis")
    print("📊 Testing trend composite strategy with real Bitcoin data")
    print("⏰ This may take a few minutes...")
    
    try:
        # Run comprehensive test
        results = run_arthur_hill_comprehensive_test()
        
        if not any(results.values()):
            print("\\n❌ All Arthur Hill backtests failed.")
            return
        
        # Generate detailed analysis
        generate_arthur_hill_monthly_summaries(results)
        generate_arthur_hill_comparison(results)
        
        print("\\n🎉 24-MONTH ARTHUR HILL BACKTEST COMPLETED!")
        print("=" * 60)
        print("✅ Arthur Hill Trend strategy successfully tested")
        print("📊 Monthly summaries and comparison analysis generated")
        print("\\n💡 Key Arthur Hill Features Tested:")
        print("   - 5-indicator trend composite (MA, CCI, BB, Keltner, Stochastic)")
        print("   - ATR trailing stops for risk management")
        print("   - Volume confirmation requirements")
        print("   - Risk profile adaptations")
        
    except Exception as e:
        print(f"\\n❌ Critical error: {str(e)}")


if __name__ == "__main__":
    main()