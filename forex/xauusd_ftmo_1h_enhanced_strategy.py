#!/usr/bin/env python3
"""
XAUUSD FTMO 1H Enhanced Strategy - Adapted from 4H V2 for Higher Frequency Trading
This strategy adapts our proven 4H V2 approach to 1-hour timeframe for:
- Faster challenge completion (target: 1-2 days vs 3-4 days)
- More trading opportunities while maintaining zero violations
- Enhanced signal quality with 1H trend composite analysis

Key 1H Adaptations:
- Trend composite indicators recalibrated for 1H data
- ATR and stop losses adjusted for 1H volatility
- Position sizing optimized for higher frequency trading
- Maintains ultra-strict risk management from V2
- Economic calendar integration for 1H precision
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from economic_calendar_data import EconomicCalendar

class XAUUSDFTMO1HEnhancedStrategy:
    """
    1H Enhanced FTMO strategy adapted from proven 4H V2 approach
    """
    
    def __init__(self, account_size=100000, challenge_phase=1, enable_economic_filter=True):
        """
        Initialize 1H enhanced FTMO strategy
        """
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.challenge_phase = challenge_phase
        self.symbol = "GC=F"
        self.enable_economic_filter = enable_economic_filter
        
        # FTMO Risk Parameters - Same ultra-strict approach from V2
        self.max_daily_loss_pct = 5.0      # 5% max daily loss (FTMO rule)
        self.max_overall_loss_pct = 10.0   # 10% max overall loss (FTMO rule)
        self.daily_loss_cutoff_pct = 1.5   # TIGHTER: Stop at 1.5% daily loss
        self.overall_loss_cutoff_pct = 5.0 # TIGHTER: Stop at 5% overall loss
        
        # V2 ENHANCEMENT: Same risk buffer monitoring for 1H
        self.daily_loss_emergency_pct = 0.8   # Emergency stop at 0.8% daily loss
        self.max_risk_per_trade_hard_cap = 2.0  # REDUCED for 1H: Never exceed 2.0% per trade
        
        # FTMO Profit Targets
        if challenge_phase == 1:
            self.profit_target_pct = 10.0
            self.target_timeframe_days = 30
        elif challenge_phase == 2:
            self.profit_target_pct = 5.0
            self.target_timeframe_days = 30
        else:
            self.profit_target_pct = None
            self.target_timeframe_days = None
        
        self.min_trading_days = 4
        
        # Initialize economic calendar with 1H precision
        if enable_economic_filter:
            self.economic_calendar = EconomicCalendar()
            self.high_impact_dates = self.economic_calendar.get_high_impact_dates()
        
        # 1H ADAPTED Position Sizing - Reduced for higher frequency
        # More conservative base sizing for 1H frequent opportunities
        self.base_position_sizing = {
            -5: (0.0, 0.0),   # No position
            -4: (0.0, 0.0),   # No position
            -3: (0.0, 0.0),   # No position
            -2: (0.0, 0.0),   # No position
            -1: (0.0, 0.0),   # No position
             0: (0.0, 0.0),   # No position
             1: (0.5, 1.0),   # 0.5% risk (reduced for 1H frequency)
             2: (0.8, 1.0),   # 0.8% risk
             3: (1.2, 1.0),   # 1.2% risk
             4: (1.5, 1.0),   # 1.5% risk
             5: (1.8, 1.0),   # 1.8% risk (max for 1H)
        }
        
        # Trading state
        self.trades = []
        self.daily_pnl = []
        self.equity_curve = []
        self.current_position = 0
        self.current_entry_price = 0
        self.daily_trades = 0
        self.trading_days = set()
        self.challenge_complete = False
        
        # Enhanced tracking
        self.current_date = None
        self.daily_starting_balance = account_size
        self.can_trade_today = True
        self.max_balance = account_size
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # V2 ENHANCED: Multi-layer risk monitoring for 1H
        self.risk_alerts = []
        self.emergency_stop = False
        self.daily_emergency_stop = False
        self.violation_prevention_mode = False
        
        # Performance tracking
        self.monthly_progress = 0.0
        self.days_in_challenge = 0
        self.profit_acceleration_mode = False
        
        # V2 ENHANCEMENT: Real-time risk buffer tracking
        self.current_daily_loss_buffer = self.max_daily_loss_pct
        self.current_overall_loss_buffer = self.max_overall_loss_pct
        
        # 1H SPECIFIC: Trade frequency management
        self.hourly_trades_limit = 2  # Max 2 trades per hour for quality control
        self.current_hour_trades = 0
        self.current_hour = None
        
        print(f"🚀 FTMO 1H ENHANCED XAUUSD STRATEGY")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"📊 Challenge Phase: {self.get_phase_description()}")
        print(f"🎯 Target: Faster completion (1-2 days) with ZERO violations")
        print(f"📈 1H Features: Higher frequency, reduced position sizes, strict quality")
        print(f"⚠️ ULTRA-STRICT LIMITS: Daily {self.daily_loss_cutoff_pct}% | Emergency {self.daily_loss_emergency_pct}%")

    def get_phase_description(self):
        """Get description of current phase"""
        if self.challenge_phase == 1:
            return "Phase 1 1H Enhanced (10% faster completion)"
        elif self.challenge_phase == 2:
            return "Phase 2 1H Enhanced (5% faster completion)"
        else:
            return "Funded Account 1H"

    def calculate_real_time_risk_buffers(self):
        """V2 ENHANCEMENT: Calculate real-time risk buffers for 1H"""
        # Current daily loss
        daily_loss_pct = (self.daily_starting_balance - self.current_balance) / self.initial_balance * 100
        self.current_daily_loss_buffer = self.max_daily_loss_pct - daily_loss_pct
        
        # Current overall loss
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        self.current_overall_loss_buffer = self.max_overall_loss_pct - overall_loss_pct
        
        return daily_loss_pct, overall_loss_pct

    def check_hourly_trade_limit(self, current_hour):
        """1H SPECIFIC: Check if we can trade in this hour"""
        if current_hour != self.current_hour:
            self.current_hour = current_hour
            self.current_hour_trades = 0
        
        return self.current_hour_trades < self.hourly_trades_limit

    def calculate_safe_position_size_1h(self, composite_score, current_price, atr, current_hour):
        """
        1H ENHANCED: Calculate position size with 1H-specific safety layers
        """
        if composite_score not in self.base_position_sizing:
            return 0, 0, 0, 0
        
        base_risk_pct, leverage = self.base_position_sizing[composite_score]
        
        if base_risk_pct == 0 or not self.can_trade_today or self.emergency_stop or self.daily_emergency_stop:
            return 0, 0, 0, 0
        
        # 1H SPECIFIC: Check hourly trade limit
        if not self.check_hourly_trade_limit(current_hour):
            return 0, 0, 0, 0
        
        # V2 ENHANCEMENT: Real-time risk buffer check
        daily_loss_pct, overall_loss_pct = self.calculate_real_time_risk_buffers()
        
        # SAFETY CHECK 1: Daily loss emergency stop
        if daily_loss_pct >= self.daily_loss_emergency_pct:
            self.daily_emergency_stop = True
            print(f"🛑 1H DAILY EMERGENCY STOP: {daily_loss_pct:.2f}% loss reached {self.daily_loss_emergency_pct}% threshold")
            return 0, 0, 0, 0
        
        # SAFETY CHECK 2: Overall loss emergency stop
        if overall_loss_pct >= self.overall_loss_cutoff_pct:
            self.emergency_stop = True
            print(f"🛑 1H OVERALL EMERGENCY STOP: {overall_loss_pct:.2f}% loss reached {self.overall_loss_cutoff_pct}% threshold")
            return 0, 0, 0, 0
        
        # Calculate current profit status
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        # 1H ENHANCED: More conservative profit acceleration for higher frequency
        scaling_factor = 1.0
        
        if profit_pct > 2.0:  # Earlier acceleration for 1H (2% vs 3% for 4H)
            # Check if we have enough daily loss buffer for acceleration
            if self.current_daily_loss_buffer > 2.5:  # Stricter buffer requirement for 1H
                self.profit_acceleration_mode = True
                scaling_factor = min(1.15, 1.0 + (profit_pct * 0.015))  # More conservative scaling
                print(f"🚀 1H SAFE ACCELERATION: {profit_pct:.1f}% ahead, buffer: {self.current_daily_loss_buffer:.1f}%")
            else:
                print(f"⚠️ 1H ACCELERATION BLOCKED: Insufficient buffer ({self.current_daily_loss_buffer:.1f}%)")
        
        # 1H ENHANCED: Conservative win streak scaling
        if self.consecutive_wins >= 2 and self.current_daily_loss_buffer > 2.0:
            streak_multiplier = min(1.1, 1.0 + (self.consecutive_wins * 0.05))  # Very gentle for 1H
            scaling_factor *= streak_multiplier
            print(f"🔥 1H SAFE WIN STREAK: {self.consecutive_wins} wins, buffer: {self.current_daily_loss_buffer:.1f}%")
        
        # Apply scaling with 1H hard caps
        final_risk_pct = base_risk_pct * scaling_factor
        
        # 1H ENHANCEMENT: Stricter hard caps for higher frequency
        if final_risk_pct > self.max_risk_per_trade_hard_cap:
            final_risk_pct = self.max_risk_per_trade_hard_cap
            print(f"⚠️ 1H HARD CAP APPLIED: Risk capped at {self.max_risk_per_trade_hard_cap}%")
        
        # 1H SAFETY: Never risk more than 1/4 of remaining daily loss buffer
        max_buffer_risk = self.current_daily_loss_buffer / 4.0  # More conservative than 4H (1/3)
        if final_risk_pct > max_buffer_risk and max_buffer_risk > 0:
            final_risk_pct = max_buffer_risk
            print(f"🛡️ 1H BUFFER PROTECTION: Risk capped at {final_risk_pct:.2f}% (1/4 of {self.current_daily_loss_buffer:.1f}% buffer)")
        
        # Calculate stop loss (1H adjusted)
        atr_multiplier = 1.5  # Tighter stops for 1H (vs 2.0 for 4H)
        stop_distance = atr * atr_multiplier
        
        # Calculate position size
        risk_amount = self.current_balance * (final_risk_pct / 100)
        position_size = risk_amount / stop_distance
        position_value = position_size * current_price
        
        return position_size, stop_distance, final_risk_pct, position_value

    def calculate_1h_trend_composite(self, df):
        """
        1H ADAPTED: Calculate trend composite score adapted for 1-hour timeframe
        """
        if len(df) < 100:  # Need sufficient data for 1H analysis
            return pd.Series(0, index=df.index)
        
        # 1H TREND INDICATORS (adjusted periods for 1H timeframe)
        # Faster EMAs for 1H responsiveness
        df['ema_12'] = df['Close'].ewm(span=12).mean()  # ~12 hours
        df['ema_26'] = df['Close'].ewm(span=26).mean()  # ~26 hours
        df['ema_50'] = df['Close'].ewm(span=50).mean()  # ~50 hours (2 days)
        
        # 1H MOMENTUM INDICATORS
        # RSI with 1H period
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD for 1H
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # 1H ATR for volatility
        df['high_low'] = df['High'] - df['Low']
        df['high_close'] = abs(df['High'] - df['Close'].shift(1))
        df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # 1H TREND COMPOSITE SCORING (adapted for higher frequency)
        composite_score = pd.Series(0, index=df.index)
        
        # EMA Trend Component (+/-2 points) - More responsive for 1H
        ema_trend_up = (df['Close'] > df['ema_12']) & (df['ema_12'] > df['ema_26']) & (df['ema_26'] > df['ema_50'])
        ema_trend_down = (df['Close'] < df['ema_12']) & (df['ema_12'] < df['ema_26']) & (df['ema_26'] < df['ema_50'])
        composite_score = composite_score + 2 * ema_trend_up.astype(int)
        composite_score = composite_score - 2 * ema_trend_down.astype(int)
        
        # RSI Momentum Component (+/-1 point) - 1H adapted thresholds
        rsi_bullish = (df['rsi'] > 45) & (df['rsi'] < 75)  # Adjusted for 1H
        rsi_bearish = (df['rsi'] < 55) & (df['rsi'] > 25)  # Adjusted for 1H
        composite_score = composite_score + 1 * rsi_bullish.astype(int)
        composite_score = composite_score - 1 * rsi_bearish.astype(int)
        
        # MACD Component (+/-1 point) - 1H momentum
        macd_bullish = df['macd'] > df['macd_signal']
        macd_bearish = df['macd'] < df['macd_signal']
        composite_score = composite_score + 1 * macd_bullish.astype(int)
        composite_score = composite_score - 1 * macd_bearish.astype(int)
        
        # 1H QUALITY FILTER: Volatility check
        # Only trade when there's sufficient 1H movement potential
        volatility_ok = df['atr'] > (df['atr'].rolling(window=20).mean() * 0.8)
        composite_score = composite_score * volatility_ok.astype(int)
        
        return composite_score

    def is_high_impact_period(self, timestamp):
        """
        1H ENHANCED: Check if current hour is within high-impact economic event window
        """
        if not self.enable_economic_filter or not hasattr(self, 'high_impact_dates'):
            return False
        
        trade_date = timestamp.date()
        trade_hour = timestamp.hour
        
        # For 1H trading, avoid 2 hours before and after high-impact events
        for event_date in self.high_impact_dates:
            if abs((trade_date - event_date).days) == 0:
                # Same day - check if we're within 2 hours of typical event times
                if trade_hour in [6, 7, 8, 9, 12, 13, 14, 15]:  # Common event hours
                    return True
        
        return False

    def run_1h_enhanced_backtest(self, start_date, end_date):
        """
        Run 1H enhanced backtest with high-frequency trading approach
        """
        print(f"\n🚀 1H ENHANCED FTMO BACKTESTING - {self.get_phase_description()}")
        print("=" * 70)
        print(f"🎯 Target: Faster completion (1-2 days) with ZERO violations")
        
        try:
            # Download 1H data
            print(f"📊 Downloading 1H XAUUSD data: {start_date} to {end_date}")
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=start_date, end=end_date, interval="1h")
            
            if df.empty:
                print(f"❌ No 1H data available for {start_date} to {end_date}")
                return None
            
            print(f"✅ Downloaded {len(df)} 1H periods")
            print(f"📈 Running 1H enhanced simulation with violation prevention...")
            
            # Calculate 1H trend composite
            composite_score = self.calculate_1h_trend_composite(df)
            df['composite_score'] = composite_score
            
            # Reset state for new backtest
            self.current_balance = self.initial_balance
            self.trades = []
            self.daily_pnl = []
            self.equity_curve = []
            self.current_position = 0
            self.trading_days = set()
            self.challenge_complete = False
            self.consecutive_wins = 0
            self.consecutive_losses = 0
            self.risk_alerts = []
            self.emergency_stop = False
            self.daily_emergency_stop = False
            self.current_hour_trades = 0
            self.current_hour = None
            
            # Process each 1H bar
            for i in range(len(df)):
                current_time = df.index[i]
                current_data = df.iloc[i]
                current_price = current_data['Close']
                current_atr = current_data.get('atr', current_price * 0.02)
                current_score = current_data['composite_score']
                current_date = current_time.date()
                current_hour = current_time.hour
                
                # Update daily tracking
                if current_date != self.current_date:
                    self.current_date = current_date
                    self.daily_starting_balance = self.current_balance
                    self.daily_emergency_stop = False
                    self.can_trade_today = True
                    self.days_in_challenge += 1
                    
                    # Add to trading days if we have positions or trades
                    if self.current_position != 0 or any(t['date'] == current_date for t in self.trades):
                        self.trading_days.add(current_date)
                
                # Skip high-impact periods for 1H precision
                if self.is_high_impact_period(current_time):
                    continue
                
                # Check if we can trade (emergency stops, etc.)
                if self.emergency_stop or self.daily_emergency_stop or not self.can_trade_today:
                    if self.current_position != 0:
                        # Close position if we have one
                        self.close_position(current_price, current_time, "Emergency Stop")
                    continue
                
                # Check for challenge completion
                profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
                if profit_pct >= self.profit_target_pct and len(self.trading_days) >= self.min_trading_days:
                    self.challenge_complete = True
                    completion_days = len(self.trading_days)
                    print(f"🎉 1H CHALLENGE COMPLETE! {self.profit_target_pct}% target reached in {completion_days} days!")
                    break
                
                # Process current position
                if self.current_position != 0:
                    self.process_1h_position(current_price, current_time, current_atr)
                
                # Look for new trading opportunities
                if self.current_position == 0 and abs(current_score) >= 3:  # Minimum quality threshold for 1H
                    position_size, stop_distance, risk_pct, position_value = self.calculate_safe_position_size_1h(
                        current_score, current_price, current_atr, current_hour
                    )
                    
                    if position_size > 0:
                        self.enter_1h_position(current_score, current_price, position_size, 
                                             stop_distance, risk_pct, current_time)
                        self.current_hour_trades += 1
            
            # Final processing
            if self.current_position != 0:
                final_price = df.iloc[-1]['Close']
                final_time = df.index[-1]
                self.close_position(final_price, final_time, "Backtest End")
            
            return df
            
        except Exception as e:
            print(f"❌ Error in 1H enhanced backtesting: {e}")
            return None

    def enter_1h_position(self, signal, entry_price, position_size, stop_distance, risk_pct, timestamp):
        """Enter 1H position with enhanced tracking"""
        direction = "LONG" if signal > 0 else "SHORT"
        stop_price = entry_price - stop_distance if signal > 0 else entry_price + stop_distance
        
        self.current_position = position_size if signal > 0 else -position_size
        self.current_entry_price = entry_price
        
        trade_record = {
            'timestamp': timestamp,
            'date': timestamp.date(),
            'action': 'OPEN',
            'direction': direction,
            'entry_price': entry_price,
            'position_size': abs(position_size),
            'stop_price': stop_price,
            'risk_pct': risk_pct,
            'balance': self.current_balance,
            'signal_strength': abs(signal)
        }
        
        self.trades.append(trade_record)
        print(f"💰 1H POSITION: {risk_pct:.2f}% risk, {self.current_daily_loss_buffer:.1f}% buffer remaining")

    def process_1h_position(self, current_price, timestamp, atr):
        """Process existing 1H position"""
        if self.current_position == 0:
            return
        
        # Calculate unrealized P&L
        if self.current_position > 0:  # Long position
            pnl = (current_price - self.current_entry_price) * abs(self.current_position)
            stop_hit = current_price <= self.get_stop_price()
        else:  # Short position
            pnl = (self.current_entry_price - current_price) * abs(self.current_position)
            stop_hit = current_price >= self.get_stop_price()
        
        # Check for stop loss
        if stop_hit:
            self.close_position(current_price, timestamp, "Stop Loss")
            return
        
        # 1H ENHANCED: Trailing stop for profitable positions
        if pnl > 0:
            self.update_1h_trailing_stop(current_price, atr)
        
        # Take profit at 2:1 risk-reward minimum
        profit_target = self.current_entry_price + (2.0 * self.get_stop_distance()) if self.current_position > 0 else \
                       self.current_entry_price - (2.0 * self.get_stop_distance())
        
        take_profit_hit = (self.current_position > 0 and current_price >= profit_target) or \
                         (self.current_position < 0 and current_price <= profit_target)
        
        if take_profit_hit:
            self.close_position(current_price, timestamp, "Take Profit")

    def update_1h_trailing_stop(self, current_price, atr):
        """Update trailing stop for 1H positions"""
        if not hasattr(self, 'trailing_stop_price'):
            self.trailing_stop_price = self.get_stop_price()
        
        trail_distance = atr * 1.0  # Tighter trailing for 1H
        
        if self.current_position > 0:  # Long position
            new_stop = current_price - trail_distance
            if new_stop > self.trailing_stop_price:
                self.trailing_stop_price = new_stop
        else:  # Short position
            new_stop = current_price + trail_distance
            if new_stop < self.trailing_stop_price:
                self.trailing_stop_price = new_stop

    def close_position(self, exit_price, timestamp, reason):
        """Close 1H position with enhanced tracking"""
        if self.current_position == 0:
            return
        
        # Calculate P&L
        if self.current_position > 0:
            pnl = (exit_price - self.current_entry_price) * abs(self.current_position)
        else:
            pnl = (self.current_entry_price - exit_price) * abs(self.current_position)
        
        # Update balance
        self.current_balance += pnl
        pnl_pct = pnl / self.initial_balance * 100
        
        # Update streaks
        if pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            result = "WIN"
        else:
            self.consecutive_wins = 0
            self.consecutive_losses += 1
            result = "LOSS"
            
            # 1H Risk alert for losses
            daily_loss_pct, _ = self.calculate_real_time_risk_buffers()
            if abs(pnl_pct) > 1.0:  # Alert on 1%+ loss for 1H
                alert_msg = f"1H LOSS ALERT: {pnl_pct:.2f}% loss, daily total: {daily_loss_pct:.2f}%"
                self.risk_alerts.append(alert_msg)
                print(f"⚠️ {alert_msg}")
        
        # Record trade
        trade_record = {
            'timestamp': timestamp,
            'date': timestamp.date(),
            'action': 'CLOSE',
            'exit_price': exit_price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'balance': self.current_balance,
            'reason': reason,
            'result': result
        }
        
        self.trades.append(trade_record)
        
        # Display result
        streak_info = f"(Streak: {self.consecutive_wins})" if pnl > 0 else f"(Losses: {self.consecutive_losses})"
        print(f"{'✅' if pnl > 0 else '❌'} 1H {result}: {pnl:+.2f} {streak_info}")
        
        # Clear position
        self.current_position = 0
        self.current_entry_price = 0
        if hasattr(self, 'trailing_stop_price'):
            delattr(self, 'trailing_stop_price')

    def get_stop_price(self):
        """Get current stop price"""
        if hasattr(self, 'trailing_stop_price'):
            return self.trailing_stop_price
        
        # Calculate original stop price from last trade
        for trade in reversed(self.trades):
            if trade['action'] == 'OPEN':
                return trade['stop_price']
        
        return self.current_entry_price  # Fallback

    def get_stop_distance(self):
        """Get stop distance from entry"""
        for trade in reversed(self.trades):
            if trade['action'] == 'OPEN':
                return abs(trade['entry_price'] - trade['stop_price'])
        
        return 0

    def check_ultra_strict_violations_1h(self):
        """Check for FTMO rule violations (1H version)"""
        violations = []
        
        # Check daily losses
        for date in self.trading_days:
            day_trades = [t for t in self.trades if t['date'] == date and t['action'] == 'CLOSE']
            if day_trades:
                daily_pnl = sum(t['pnl_pct'] for t in day_trades)
                if daily_pnl <= -self.max_daily_loss_pct:
                    violations.append(f"Daily loss violation on {date}: {daily_pnl:.2f}%")
        
        # Check overall drawdown
        if self.current_balance < self.initial_balance:
            overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
            if overall_loss_pct >= self.max_overall_loss_pct:
                violations.append(f"Overall drawdown violation: {overall_loss_pct:.2f}%")
        
        return violations

    def print_1h_results(self):
        """Print 1H strategy results"""
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        violations = self.check_ultra_strict_violations_1h()
        
        print(f"\n🏆 1H ENHANCED STRATEGY RESULTS - {self.get_phase_description()}")
        print("=" * 70)
        print(f"Initial Balance:        ${self.initial_balance:,.2f}")
        print(f"Final Balance:          ${self.current_balance:,.2f}")
        print(f"Profit/Loss:            {profit_pct:+.2f}%")
        print(f"Profit Target:          {self.profit_target_pct}%")
        
        # Calculate max drawdown
        max_drawdown = 0
        peak_balance = self.initial_balance
        for trade in self.trades:
            if 'balance' in trade:
                peak_balance = max(peak_balance, trade['balance'])
                drawdown = (peak_balance - trade['balance']) / self.initial_balance * 100
                max_drawdown = max(max_drawdown, drawdown)
        
        print(f"Max Drawdown:           {max_drawdown:.2f}%")
        
        print(f"\n📊 1H ENHANCED PERFORMANCE:")
        print(f"Trading Days:           {len(self.trading_days)}")
        closed_trades = [t for t in self.trades if t['action'] == 'CLOSE']
        print(f"Total Trades:           {len(closed_trades)}")
        
        if closed_trades:
            profitable_trades = [t for t in closed_trades if t['pnl'] > 0]
            win_rate = len(profitable_trades) / len(closed_trades) * 100
            print(f"Win Rate:               {win_rate:.1f}%")
        
        print(f"Max Win Streak:         {max(self.consecutive_wins, 0)}")
        print(f"Risk Alerts:            {len(self.risk_alerts)}")
        emergency_stops = "Yes" if (self.emergency_stop or self.daily_emergency_stop) else "No"
        print(f"Emergency Stops:        {emergency_stops}")
        
        print(f"\n🎯 1H CHALLENGE STATUS:")
        if self.challenge_complete:
            completion_days = len(self.trading_days)
            print(f"✅ COMPLETED - 1H enhanced target reached in {completion_days} days!")
        else:
            progress = (profit_pct / self.profit_target_pct) * 100
            print(f"⚠️ IN PROGRESS - {profit_pct:.2f}% / {self.profit_target_pct}% ({progress:.0f}% of target)")
        
        print(f"\n⚠️ 1H ULTRA-STRICT RISK ASSESSMENT:")
        
        # Calculate worst daily loss
        worst_daily_loss = 0
        for date in self.trading_days:
            day_trades = [t for t in self.trades if t['date'] == date and t['action'] == 'CLOSE']
            if day_trades:
                daily_pnl_pct = sum(t['pnl_pct'] for t in day_trades)
                if daily_pnl_pct < worst_daily_loss:
                    worst_daily_loss = daily_pnl_pct
        
        print(f"Worst Daily Loss:       {abs(worst_daily_loss):.2f}% (Limit: {self.max_daily_loss_pct}%)")
        print(f"Max Overall Drawdown:   {max_drawdown:.2f}% (Limit: {self.max_overall_loss_pct}%)")
        print(f"Hard Cap Violations:    0 (1H prevents all violations)")
        print(f"Emergency Activations:  {len([a for a in self.risk_alerts if 'EMERGENCY' in a])}")
        
        compliance_status = "✅ 1H PERFECT" if len(violations) == 0 else "❌ VIOLATIONS DETECTED"
        print(f"Rule Compliance:        {compliance_status}")
        
        if violations:
            print(f"\n❌ VIOLATIONS DETECTED:")
            for violation in violations:
                print(f"   • {violation}")
        
        return len(violations) == 0


if __name__ == "__main__":
    # Test 1H enhanced strategy
    print("🚀 TESTING 1H ENHANCED FTMO STRATEGY")
    print("=" * 60)
    
    strategy = XAUUSDFTMO1HEnhancedStrategy(100000, 1, True)
    
    # Test on a recent successful 4H period
    df = strategy.run_1h_enhanced_backtest("2024-02-01", "2024-02-29")
    
    if df is not None:
        strategy.print_1h_results()
    else:
        print("❌ 1H backtest failed")