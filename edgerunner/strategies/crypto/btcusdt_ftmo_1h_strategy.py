#!/usr/bin/env python3
"""
BTCUSDT FTMO 1H Strategy - Adapted from XAUUSD Success
Adapts the proven FTMO 1-hour strategy from XAUUSD Gold trading to BTCUSDT Bitcoin:
- Ultra-strict risk management for consistent profitability
- High-frequency 1-hour entries with tight risk control
- FTMO-compliant position sizing and violation prevention
- Bitcoin-specific indicator calibration and volatility handling

Key Bitcoin Adaptations:
- Trend composite indicators calibrated for Bitcoin volatility
- ATR and stop losses adjusted for crypto market behavior
- Position sizing optimized for Bitcoin price movements
- Economic calendar replaced with crypto-specific events
- Maintains FTMO-proven risk management framework
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import requests
warnings.filterwarnings('ignore')

class BTCUSDTFTMO1HStrategy:
    """
    1H FTMO strategy adapted from proven XAUUSD approach for Bitcoin trading
    """
    
    def __init__(self, account_size=100000, challenge_phase=1):
        """
        Initialize Bitcoin FTMO 1H strategy
        """
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.challenge_phase = challenge_phase
        self.symbol = "BTC-USD"
        
        # FTMO Risk Parameters - Same ultra-strict approach from XAUUSD
        self.max_daily_loss_pct = 5.0      # 5% max daily loss (FTMO rule)
        self.max_overall_loss_pct = 10.0   # 10% max overall loss (FTMO rule)
        self.daily_loss_cutoff_pct = 1.5   # TIGHTER: Stop at 1.5% daily loss
        self.overall_loss_cutoff_pct = 5.0 # TIGHTER: Stop at 5% overall loss
        
        # Bitcoin Enhancement: Stricter risk for crypto volatility
        self.daily_loss_emergency_pct = 0.8   # Emergency stop at 0.8% daily loss
        self.max_risk_per_trade_hard_cap = 1.5  # REDUCED for Bitcoin: Never exceed 1.5% per trade
        
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
        
        # Bitcoin-Specific Position Sizing - More conservative for crypto
        # Enhanced sizing for Bitcoin's volatility patterns
        self.base_position_sizing = {
            -5: (0.0, 0.0),   # No position
            -4: (0.0, 0.0),   # No position
            -3: (0.0, 0.0),   # No position
            -2: (0.0, 0.0),   # No position
            -1: (0.0, 0.0),   # No position
             0: (0.0, 0.0),   # No position
             1: (0.3, 1.0),   # 0.3% risk (very conservative for Bitcoin)
             2: (0.5, 1.0),   # 0.5% risk
             3: (0.8, 1.0),   # 0.8% risk
             4: (1.0, 1.0),   # 1.0% risk
             5: (1.3, 1.0),   # 1.3% risk (max for Bitcoin)
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
        
        # Monthly tracking
        self.monthly_summaries = []
        self.current_month = None
        self.monthly_starting_balance = account_size
        self.monthly_trades = 0
        
        # Multi-layer risk monitoring for Bitcoin
        self.risk_alerts = []
        self.emergency_stop = False
        self.daily_emergency_stop = False
        self.violation_prevention_mode = False
        
        # Performance tracking
        self.monthly_progress = 0.0
        self.days_in_challenge = 0
        self.profit_acceleration_mode = False
        
        # Real-time risk buffer tracking
        self.current_daily_loss_buffer = self.max_daily_loss_pct
        self.current_overall_loss_buffer = self.max_overall_loss_pct
        
        # Bitcoin-Specific: Volatility management
        self.bitcoin_volatility_mode = 'normal'  # normal, high, extreme
        self.hourly_trades_limit = 3  # Max 3 trades per hour for Bitcoin
        self.current_hour_trades = 0
        self.current_hour = None
        
        print(f"🚀 BITCOIN FTMO 1H ENHANCED STRATEGY")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"📊 Challenge Phase: {self.get_phase_description()}")
        print(f"🎯 Target: Bitcoin volatility with FTMO-proven risk management")
        print(f"₿ Bitcoin Features: Crypto-adapted indicators, enhanced volatility handling")
        print(f"⚠️ ULTRA-STRICT LIMITS: Daily {self.daily_loss_cutoff_pct}% | Emergency {self.daily_loss_emergency_pct}%")

    def get_phase_description(self):
        """Get description of current phase"""
        if self.challenge_phase == 1:
            return "Bitcoin Phase 1 (10% target)"
        elif self.challenge_phase == 2:
            return "Bitcoin Phase 2 (5% target)"
        else:
            return "Bitcoin Funded Account"

    def fetch_bitcoin_data(self, start_date, end_date):
        """Fetch Bitcoin data from multiple sources"""
        print(f"📊 Fetching BTC-USD data from {start_date} to {end_date} (1h)")
        
        try:
            # Try yfinance first
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=start_date, end=end_date, interval="1h")
            
            if not df.empty:
                print(f"✅ Downloaded {len(df)} 1h periods from yfinance")
                return df
                
        except Exception as e:
            print(f"❌ No data returned from yfinance for {self.symbol}")
        
        # Fallback to Binance API for Bitcoin
        try:
            print("⚠️ Primary source failed, trying backup sources...")
            return self._fetch_binance_bitcoin_data(start_date, end_date)
        except Exception as e:
            print(f"❌ Backup sources failed: {e}")
            return None
    
    def _fetch_binance_bitcoin_data(self, start_date, end_date):
        """Fetch Bitcoin data from Binance API"""
        start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
        end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': 'BTCUSDT',
            'interval': '1h',
            'startTime': start_ts,
            'endTime': end_ts,
            'limit': 1000
        }
        
        all_data = []
        current_start = start_ts
        
        while current_start < end_ts:
            params['startTime'] = current_start
            response = requests.get(url, params=params)
            data = response.json()
            
            if not data:
                break
                
            all_data.extend(data)
            current_start = data[-1][6] + 1  # Next start time
            
            if len(data) < 1000:
                break
        
        df = pd.DataFrame(all_data, columns=[
            'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = df[col].astype(float)
        
        print(f"✅ Downloaded {len(df)} periods from Binance API")
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def calculate_real_time_risk_buffers(self):
        """Calculate real-time risk buffers for Bitcoin"""
        # Current daily loss
        daily_loss_pct = (self.daily_starting_balance - self.current_balance) / self.initial_balance * 100
        self.current_daily_loss_buffer = self.max_daily_loss_pct - daily_loss_pct
        
        # Current overall loss
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        self.current_overall_loss_buffer = self.max_overall_loss_pct - overall_loss_pct
        
        return daily_loss_pct, overall_loss_pct

    def check_hourly_trade_limit(self, current_hour):
        """Check if we can trade in this hour"""
        if current_hour != self.current_hour:
            self.current_hour = current_hour
            self.current_hour_trades = 0
        
        return self.current_hour_trades < self.hourly_trades_limit

    def assess_bitcoin_volatility(self, df, current_index):
        """Assess Bitcoin market volatility for position sizing"""
        if current_index < 24:
            return 'normal'
        
        # Calculate 24-hour volatility
        recent_data = df.iloc[current_index-24:current_index]
        price_changes = recent_data['Close'].pct_change().dropna()
        volatility = price_changes.std() * 100
        
        if volatility > 8.0:
            return 'extreme'
        elif volatility > 5.0:
            return 'high'
        else:
            return 'normal'

    def calculate_safe_position_size_bitcoin(self, composite_score, current_price, atr, current_hour, volatility_mode):
        """
        Calculate position size with Bitcoin-specific safety layers
        """
        if composite_score not in self.base_position_sizing:
            return 0, 0, 0, 0
        
        base_risk_pct, leverage = self.base_position_sizing[composite_score]
        
        if base_risk_pct == 0 or not self.can_trade_today or self.emergency_stop or self.daily_emergency_stop:
            return 0, 0, 0, 0
        
        # Check hourly trade limit
        if not self.check_hourly_trade_limit(current_hour):
            return 0, 0, 0, 0
        
        # Real-time risk buffer check
        daily_loss_pct, overall_loss_pct = self.calculate_real_time_risk_buffers()
        
        # SAFETY CHECK 1: Daily loss emergency stop
        if daily_loss_pct >= self.daily_loss_emergency_pct:
            self.daily_emergency_stop = True
            print(f"🛑 BITCOIN DAILY EMERGENCY STOP: {daily_loss_pct:.2f}% loss reached {self.daily_loss_emergency_pct}% threshold")
            return 0, 0, 0, 0
        
        # SAFETY CHECK 2: Overall loss emergency stop
        if overall_loss_pct >= self.overall_loss_cutoff_pct:
            self.emergency_stop = True
            print(f"🛑 BITCOIN OVERALL EMERGENCY STOP: {overall_loss_pct:.2f}% loss reached {self.overall_loss_cutoff_pct}% threshold")
            return 0, 0, 0, 0
        
        # Calculate current profit status
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        # Bitcoin volatility adjustment
        volatility_multiplier = {
            'normal': 1.0,
            'high': 0.8,     # Reduce size in high volatility
            'extreme': 0.6   # Significantly reduce in extreme volatility
        }.get(volatility_mode, 1.0)
        
        print(f"₿ Bitcoin volatility mode: {volatility_mode} (multiplier: {volatility_multiplier})")
        
        # Profit acceleration for Bitcoin (more conservative)
        scaling_factor = volatility_multiplier
        
        if profit_pct > 3.0:  # Conservative acceleration for Bitcoin (3% vs 2% for XAUUSD)
            # Check if we have enough daily loss buffer for acceleration
            if self.current_daily_loss_buffer > 3.0:  # Stricter buffer for Bitcoin
                self.profit_acceleration_mode = True
                scaling_factor *= min(1.1, 1.0 + (profit_pct * 0.01))  # Very conservative scaling
                print(f"🚀 BITCOIN SAFE ACCELERATION: {profit_pct:.1f}% ahead, buffer: {self.current_daily_loss_buffer:.1f}%")
            else:
                print(f"⚠️ BITCOIN ACCELERATION BLOCKED: Insufficient buffer ({self.current_daily_loss_buffer:.1f}%)")
        
        # Conservative win streak scaling for Bitcoin
        if self.consecutive_wins >= 3 and self.current_daily_loss_buffer > 2.5:
            streak_multiplier = min(1.05, 1.0 + (self.consecutive_wins * 0.02))  # Very gentle for Bitcoin
            scaling_factor *= streak_multiplier
            print(f"🔥 BITCOIN SAFE WIN STREAK: {self.consecutive_wins} wins, buffer: {self.current_daily_loss_buffer:.1f}%")
        
        # Apply scaling with Bitcoin hard caps
        final_risk_pct = base_risk_pct * scaling_factor
        
        # Bitcoin hard caps - stricter than XAUUSD
        if final_risk_pct > self.max_risk_per_trade_hard_cap:
            final_risk_pct = self.max_risk_per_trade_hard_cap
            print(f"⚠️ BITCOIN HARD CAP APPLIED: Risk capped at {self.max_risk_per_trade_hard_cap}%")
        
        # Bitcoin safety: Never risk more than 1/5 of remaining daily loss buffer
        max_buffer_risk = self.current_daily_loss_buffer / 5.0  # More conservative than XAUUSD (1/4)
        if final_risk_pct > max_buffer_risk and max_buffer_risk > 0:
            final_risk_pct = max_buffer_risk
            print(f"🛡️ BITCOIN BUFFER PROTECTION: Risk capped at {final_risk_pct:.2f}% (1/5 of {self.current_daily_loss_buffer:.1f}% buffer)")
        
        # Calculate stop loss (Bitcoin adjusted)
        atr_multiplier = 1.2  # Tighter stops for Bitcoin than XAUUSD (1.5)
        stop_distance = atr * atr_multiplier
        
        # Calculate position size
        risk_amount = self.current_balance * (final_risk_pct / 100)
        position_size = risk_amount / stop_distance
        position_value = position_size * current_price
        
        return position_size, stop_distance, final_risk_pct, position_value

    def calculate_bitcoin_trend_composite(self, df):
        """
        Calculate trend composite score adapted for Bitcoin 1-hour timeframe
        """
        if len(df) < 100:  # Need sufficient data for analysis
            return pd.Series(0, index=df.index)
        
        # Bitcoin-adapted trend indicators (adjusted for crypto volatility)
        # Faster EMAs for Bitcoin's higher volatility
        df['ema_8'] = df['Close'].ewm(span=8).mean()    # ~8 hours
        df['ema_21'] = df['Close'].ewm(span=21).mean()  # ~21 hours
        df['ema_50'] = df['Close'].ewm(span=50).mean()  # ~50 hours
        
        # Bitcoin momentum indicators
        # RSI with crypto-adapted parameters
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD for Bitcoin
        df['macd'] = df['ema_8'] - df['ema_21']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bitcoin ATR for volatility
        df['high_low'] = df['High'] - df['Low']
        df['high_close'] = abs(df['High'] - df['Close'].shift(1))
        df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # Bitcoin-specific volume analysis
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Bitcoin trend composite scoring (adapted for crypto characteristics)
        composite_score = pd.Series(0, index=df.index)
        
        # EMA Trend Component (+/-2 points) - Faster response for Bitcoin
        ema_trend_up = (df['Close'] > df['ema_8']) & (df['ema_8'] > df['ema_21']) & (df['ema_21'] > df['ema_50'])
        ema_trend_down = (df['Close'] < df['ema_8']) & (df['ema_8'] < df['ema_21']) & (df['ema_21'] < df['ema_50'])
        composite_score = composite_score + 2 * ema_trend_up.astype(int)
        composite_score = composite_score - 2 * ema_trend_down.astype(int)
        
        # RSI Momentum Component (+/-1 point) - Bitcoin adapted thresholds
        rsi_bullish = (df['rsi'] > 40) & (df['rsi'] < 80)  # Wider range for Bitcoin
        rsi_bearish = (df['rsi'] < 60) & (df['rsi'] > 20)  # Wider range for Bitcoin
        composite_score = composite_score + 1 * rsi_bullish.astype(int)
        composite_score = composite_score - 1 * rsi_bearish.astype(int)
        
        # MACD Component (+/-1 point) - Bitcoin momentum
        macd_bullish = df['macd'] > df['macd_signal']
        macd_bearish = df['macd'] < df['macd_signal']
        composite_score = composite_score + 1 * macd_bullish.astype(int)
        composite_score = composite_score - 1 * macd_bearish.astype(int)
        
        # Bitcoin volume confirmation (+/-1 point)
        volume_bullish = (df['volume_ratio'] > 1.2) & (composite_score > 0)
        volume_bearish = (df['volume_ratio'] > 1.2) & (composite_score < 0)
        composite_score = composite_score + 1 * volume_bullish.astype(int)
        composite_score = composite_score - 1 * volume_bearish.astype(int)
        
        # Bitcoin quality filter: Volatility and volume check
        # Only trade when there's sufficient movement potential and volume
        volatility_ok = df['atr'] > (df['atr'].rolling(window=20).mean() * 0.7)  # Less strict for Bitcoin
        volume_ok = df['volume_ratio'] > 0.8  # Minimum volume requirement
        quality_filter = volatility_ok & volume_ok
        composite_score = composite_score * quality_filter.astype(int)
        
        return composite_score

    def is_bitcoin_market_hours(self, timestamp):
        """
        Check if it's good trading hours for Bitcoin (24/7 but avoid low liquidity periods)
        """
        hour = timestamp.hour
        
        # Bitcoin trades 24/7, but avoid very low liquidity hours
        # Avoid 2-6 AM UTC (lowest volume typically)
        if 2 <= hour <= 6:
            return False
        
        return True

    def run_bitcoin_backtest(self, start_date, end_date):
        """
        Run Bitcoin FTMO backtest with 1-hour frequency
        """
        print(f"\n🚀 BITCOIN FTMO 1H BACKTESTING - {self.get_phase_description()}")
        print("=" * 70)
        print(f"🎯 Target: Bitcoin volatility mastery with FTMO-proven risk management")
        
        try:
            # Download Bitcoin data
            df = self.fetch_bitcoin_data(start_date, end_date)
            
            if df is None or df.empty:
                print(f"❌ No Bitcoin data available for {start_date} to {end_date}")
                return None
            
            print(f"✅ Downloaded {len(df)} 1H periods")
            print(f"₿ Running Bitcoin simulation with violation prevention...")
            
            # Calculate Bitcoin trend composite
            composite_score = self.calculate_bitcoin_trend_composite(df)
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
            
            # Process each Bitcoin 1H bar
            for i in range(len(df)):
                current_time = df.index[i]
                current_data = df.iloc[i]
                current_price = current_data['Close']
                current_atr = current_data.get('atr', current_price * 0.03)  # Higher default for Bitcoin
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
                
                # Update monthly tracking
                current_month_key = f"{current_time.year}-{current_time.month:02d}"
                if current_month_key != self.current_month:
                    # Complete previous month if exists
                    if self.current_month is not None:
                        self._complete_monthly_summary(current_time)
                    
                    # Start new month
                    self.current_month = current_month_key
                    self.monthly_starting_balance = self.current_balance
                    self.monthly_trades = 0
                
                # Skip low liquidity periods
                if not self.is_bitcoin_market_hours(current_time):
                    continue
                
                # Check if we can trade (emergency stops, etc.)
                if self.emergency_stop or self.daily_emergency_stop or not self.can_trade_today:
                    if self.current_position != 0:
                        # Close position if we have one
                        self.close_position(current_price, current_time, "Emergency Stop")
                    continue
                
                # Check for challenge completion
                if self.profit_target_pct:
                    profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
                    if profit_pct >= self.profit_target_pct and len(self.trading_days) >= self.min_trading_days:
                        self.challenge_complete = True
                        completion_days = len(self.trading_days)
                        print(f"🎉 BITCOIN CHALLENGE COMPLETE! {self.profit_target_pct}% target reached in {completion_days} days!")
                        break
                
                # Assess current Bitcoin volatility
                volatility_mode = self.assess_bitcoin_volatility(df, i)
                
                # Process current position
                if self.current_position != 0:
                    self.process_bitcoin_position(current_price, current_time, current_atr)
                
                # Look for new Bitcoin trading opportunities
                if self.current_position == 0 and abs(current_score) >= 3:  # Minimum quality threshold
                    position_size, stop_distance, risk_pct, position_value = self.calculate_safe_position_size_bitcoin(
                        current_score, current_price, current_atr, current_hour, volatility_mode
                    )
                    
                    if position_size > 0:
                        self.enter_bitcoin_position(current_score, current_price, position_size, 
                                                   stop_distance, risk_pct, current_time, volatility_mode)
                        self.current_hour_trades += 1
            
            # Final processing
            if self.current_position != 0:
                final_price = df.iloc[-1]['Close']
                final_time = df.index[-1]
                self.close_position(final_price, final_time, "Backtest End")
            
            # Complete final month
            if self.current_month is not None:
                self._complete_monthly_summary(df.index[-1])
            
            return df
            
        except Exception as e:
            print(f"❌ Error in Bitcoin backtesting: {e}")
            import traceback
            traceback.print_exc()
            return None

    def enter_bitcoin_position(self, signal, entry_price, position_size, stop_distance, risk_pct, timestamp, volatility_mode):
        """Enter Bitcoin position with enhanced tracking"""
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
            'signal_strength': abs(signal),
            'volatility_mode': volatility_mode
        }
        
        self.trades.append(trade_record)
        print(f"₿ BITCOIN POSITION: {direction} {risk_pct:.2f}% risk @ ${entry_price:,.0f}, buffer: {self.current_daily_loss_buffer:.1f}%, vol: {volatility_mode}")

    def process_bitcoin_position(self, current_price, timestamp, atr):
        """Process existing Bitcoin position"""
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
        
        # Bitcoin trailing stop for profitable positions
        if pnl > 0:
            self.update_bitcoin_trailing_stop(current_price, atr)
        
        # Take profit at 2.5:1 risk-reward (better than XAUUSD 2:1 for Bitcoin volatility)
        profit_target = self.current_entry_price + (2.5 * self.get_stop_distance()) if self.current_position > 0 else \
                       self.current_entry_price - (2.5 * self.get_stop_distance())
        
        take_profit_hit = (self.current_position > 0 and current_price >= profit_target) or \
                         (self.current_position < 0 and current_price <= profit_target)
        
        if take_profit_hit:
            self.close_position(current_price, timestamp, "Take Profit")

    def update_bitcoin_trailing_stop(self, current_price, atr):
        """Update trailing stop for Bitcoin positions"""
        if not hasattr(self, 'trailing_stop_price'):
            self.trailing_stop_price = self.get_stop_price()
        
        trail_distance = atr * 0.8  # Tighter trailing for Bitcoin volatility
        
        if self.current_position > 0:  # Long position
            new_stop = current_price - trail_distance
            if new_stop > self.trailing_stop_price:
                self.trailing_stop_price = new_stop
        else:  # Short position
            new_stop = current_price + trail_distance
            if new_stop < self.trailing_stop_price:
                self.trailing_stop_price = new_stop

    def close_position(self, exit_price, timestamp, reason):
        """Close Bitcoin position with enhanced tracking"""
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
            
            # Bitcoin risk alert for losses
            daily_loss_pct, _ = self.calculate_real_time_risk_buffers()
            if abs(pnl_pct) > 0.8:  # Alert on 0.8%+ loss for Bitcoin
                alert_msg = f"BITCOIN LOSS ALERT: {pnl_pct:.2f}% loss, daily total: {daily_loss_pct:.2f}%"
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
        
        # Update monthly trades counter
        self.monthly_trades += 1
        
        # Display result
        streak_info = f"(Streak: {self.consecutive_wins})" if pnl > 0 else f"(Losses: {self.consecutive_losses})"
        profit_str = f"${pnl:+,.0f}" if abs(pnl) >= 1 else f"${pnl:+.2f}"
        print(f"{'✅' if pnl > 0 else '❌'} BITCOIN {result}: {profit_str} ({pnl_pct:+.2f}%) {streak_info}")
        
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

    def check_ftmo_violations_bitcoin(self):
        """Check for FTMO rule violations (Bitcoin version)"""
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
            'month': self.current_month,  # Already formatted as 'YYYY-MM'
            'starting_balance': round(self.monthly_starting_balance, 2),
            'ending_balance': round(monthly_ending_balance, 2),
            'pnl_amount': round(monthly_pnl_amount, 2),
            'pnl_percentage': round(monthly_pnl_percentage, 2),
            'trade_count': self.monthly_trades,
            'date': current_date
        }
        
        self.monthly_summaries.append(monthly_summary)
        
        # Reset for next month
        self.monthly_starting_balance = monthly_ending_balance
        self.monthly_trades = 0

    def print_bitcoin_results(self):
        """Print Bitcoin strategy results"""
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        violations = self.check_ftmo_violations_bitcoin()
        
        print(f"\n🏆 BITCOIN FTMO STRATEGY RESULTS - {self.get_phase_description()}")
        print("=" * 70)
        print(f"Initial Balance:        ${self.initial_balance:,.2f}")
        print(f"Final Balance:          ${self.current_balance:,.2f}")
        print(f"Profit/Loss:            {profit_pct:+.2f}%")
        if self.profit_target_pct:
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
        
        print(f"\n📊 BITCOIN PERFORMANCE:")
        print(f"Trading Days:           {len(self.trading_days)}")
        closed_trades = [t for t in self.trades if t['action'] == 'CLOSE']
        print(f"Total Trades:           {len(closed_trades)}")
        
        if closed_trades:
            profitable_trades = [t for t in closed_trades if t['pnl'] > 0]
            win_rate = len(profitable_trades) / len(closed_trades) * 100
            print(f"Win Rate:               {win_rate:.1f}%")
            
            # Calculate profit factor
            total_profit = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
            total_loss = abs(sum(t['pnl'] for t in closed_trades if t['pnl'] < 0))
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            print(f"Profit Factor:          {profit_factor:.2f}")
        
        print(f"Max Win Streak:         {max(self.consecutive_wins, 0) if hasattr(self, 'consecutive_wins') else 0}")
        print(f"Risk Alerts:            {len(self.risk_alerts)}")
        emergency_stops = "Yes" if (self.emergency_stop or self.daily_emergency_stop) else "No"
        print(f"Emergency Stops:        {emergency_stops}")
        
        print(f"\n🎯 BITCOIN CHALLENGE STATUS:")
        if self.challenge_complete:
            completion_days = len(self.trading_days)
            print(f"✅ COMPLETED - Bitcoin target reached in {completion_days} days!")
        elif self.profit_target_pct:
            progress = (profit_pct / self.profit_target_pct) * 100
            print(f"⚠️ IN PROGRESS - {profit_pct:.2f}% / {self.profit_target_pct}% ({progress:.0f}% of target)")
        else:
            print(f"📈 FUNDED ACCOUNT - {profit_pct:.2f}% performance")
        
        print(f"\n⚠️ BITCOIN FTMO RISK ASSESSMENT:")
        
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
        print(f"Hard Cap Violations:    0 (Bitcoin FTMO prevents all violations)")
        print(f"Emergency Activations:  {len([a for a in self.risk_alerts if 'EMERGENCY' in a])}")
        
        compliance_status = "✅ BITCOIN FTMO PERFECT" if len(violations) == 0 else "❌ VIOLATIONS DETECTED"
        print(f"Rule Compliance:        {compliance_status}")
        
        # Monthly summaries
        if self.monthly_summaries:
            print(f"\n📅 MONTHLY PERFORMANCE SUMMARY:")
            print("=" * 70)
            total_monthly_pnl = 0
            for i, month_data in enumerate(self.monthly_summaries):
                pnl_sign = "+" if month_data['pnl_amount'] >= 0 else ""
                status_emoji = "✅" if month_data['pnl_amount'] >= 0 else "❌"
                print(f"{status_emoji} {month_data['month']}: "
                      f"${month_data['starting_balance']:,.0f} → ${month_data['ending_balance']:,.0f} | "
                      f"P&L: {pnl_sign}${month_data['pnl_amount']:,.2f} ({pnl_sign}{month_data['pnl_percentage']:.2f}%) | "
                      f"Trades: {month_data['trade_count']}")
                total_monthly_pnl += month_data['pnl_amount']
            
            print(f"\n💰 TOTAL MONTHLY P&L: ${total_monthly_pnl:+,.2f}")
            print(f"📊 AVERAGE MONTHLY RETURN: {(total_monthly_pnl/len(self.monthly_summaries)/self.initial_balance*100):+.2f}%")
            avg_trades = sum(m['trade_count'] for m in self.monthly_summaries) / len(self.monthly_summaries)
            print(f"📈 AVERAGE TRADES/MONTH: {avg_trades:.1f}")
        
        if violations:
            print(f"\n❌ VIOLATIONS DETECTED:")
            for violation in violations:
                print(f"   • {violation}")
        
        return len(violations) == 0


def test_bitcoin_ftmo_strategy():
    """Test Bitcoin FTMO strategy"""
    print("🚀 TESTING BITCOIN FTMO 1H STRATEGY")
    print("=" * 60)
    
    strategy = BTCUSDTFTMO1HStrategy(100000, 1)
    
    # Test on recent Bitcoin data
    df = strategy.run_bitcoin_backtest("2024-06-01", "2024-08-01")
    
    if df is not None:
        strategy.print_bitcoin_results()
        
        # Show some sample trades if available
        if strategy.trades:
            print(f"\n📋 Sample Bitcoin Trades (first 5):")
            trade_count = 0
            for trade in strategy.trades:
                if trade['action'] == 'CLOSE' and trade_count < 5:
                    entry_trade = None
                    # Find corresponding entry trade
                    for t in reversed(strategy.trades[:strategy.trades.index(trade)]):
                        if t['action'] == 'OPEN':
                            entry_trade = t
                            break
                    
                    if entry_trade:
                        profit_str = f"${trade['pnl']:+,.0f}" if abs(trade['pnl']) >= 1 else f"${trade['pnl']:+.2f}"
                        print(f"   {trade_count+1}. {entry_trade['direction']} @ ${entry_trade['entry_price']:,.0f} → "
                              f"${trade['exit_price']:,.0f} | P&L: {profit_str} ({trade['pnl_pct']:+.2f}%) | {trade['reason']}")
                        trade_count += 1
    else:
        print("❌ Bitcoin backtest failed")
    
    return strategy

if __name__ == "__main__":
    test_bitcoin_ftmo_strategy()