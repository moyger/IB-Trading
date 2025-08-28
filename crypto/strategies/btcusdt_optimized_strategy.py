#!/usr/bin/env python3
"""
BTCUSDT Optimized Strategy - Conservative Improvements
Implements Priority 1 optimization: Confluence threshold tuning (3.5-4.5 range)

Key Optimizations (Anti-Overfitting Approach):
1. Flexible confluence threshold (3.8 vs fixed 4.0)
2. Dynamic volume filtering (percentile-based)
3. Improved market regime detection
4. Enhanced risk management

Maintains all proven logic while allowing conservative fine-tuning.
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from data_fetcher import BTCDataFetcher
from typing import Optional, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class BTCUSDTOptimizedStrategy:
    """Optimized BTCUSDT strategy with conservative improvements"""
    
    def __init__(self, account_size: float = 10000, risk_profile: str = 'moderate'):
        """Initialize optimized strategy with tunable parameters"""
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.risk_profile = risk_profile
        
        # Data fetcher
        self.data_fetcher = BTCDataFetcher()
        
        # OPTIMIZATION 1: Flexible Confluence Threshold
        self.confluence_configs = {
            'conservative': 4.2,  # Slightly higher for quality
            'moderate': 3.8,      # Optimized from 4.0
            'aggressive': 3.5     # Lower for more trades
        }
        self.confluence_threshold = self.confluence_configs[risk_profile]
        
        # OPTIMIZATION 2: Dynamic Volume Percentile (vs fixed 1.2x)
        self.volume_percentile = 70  # Top 30% volume periods
        self.volume_lookback = 100   # Periods for percentile calculation
        
        # OPTIMIZATION 3: Market Regime Detection
        self.volatility_regime_enabled = True
        self.regime_lookback = 50
        
        # Initialize other parameters from proven strategy
        self._init_risk_parameters()
        self._init_position_sizing()
        
        # Trading state
        self.trades = []
        self.daily_pnl = []
        self.equity_curve = []
        self.current_position = 0
        self.current_entry_price = 0
        self.trading_days = set()
        
        # Enhanced tracking
        self.current_date = None
        self.daily_starting_balance = account_size
        self.can_trade_today = True
        self.max_balance = account_size
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # Risk monitoring
        self.risk_alerts = []
        self.emergency_stop = False
        self.daily_emergency_stop = False
        
        # Performance tracking
        self.confluence_scores = []
        self.market_regimes = []
        self.trades_skipped_filters = {
            'no_trend': 0,
            'low_volume': 0,
            'low_volatility': 0,
            'weak_confluence': 0,
            'pattern_rejection': 0,
            'regime_mismatch': 0
        }
        
        print(f"🚀 BTCUSDT OPTIMIZED STRATEGY ({risk_profile.upper()})")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"🎯 Confluence Threshold: {self.confluence_threshold} (optimized from 4.0)")
        print(f"📊 Dynamic Volume Filter: Top {100-self.volume_percentile}% periods")
        print(f"🌡️ Volatility Regime Detection: {'Enabled' if self.volatility_regime_enabled else 'Disabled'}")
    
    def _init_risk_parameters(self):
        """Initialize proven risk parameters (unchanged)"""
        risk_configs = {
            'conservative': {
                'max_daily_loss_pct': 3.0,
                'max_total_loss_pct': 6.0,
                'max_position_size_pct': 5.0,
                'daily_profit_target_pct': 2.0
            },
            'moderate': {
                'max_daily_loss_pct': 4.0,
                'max_total_loss_pct': 8.0,
                'max_position_size_pct': 8.0,
                'daily_profit_target_pct': 3.0
            },
            'aggressive': {
                'max_daily_loss_pct': 5.0,
                'max_total_loss_pct': 10.0,
                'max_position_size_pct': 12.0,
                'daily_profit_target_pct': 4.0
            }
        }
        
        config = risk_configs[self.risk_profile]
        self.max_daily_loss = self.account_size * config['max_daily_loss_pct'] / 100
        self.max_total_loss = self.account_size * config['max_total_loss_pct'] / 100
        self.max_position_size = self.account_size * config['max_position_size_pct'] / 100
        self.daily_profit_target = self.account_size * config['daily_profit_target_pct'] / 100

    def _init_position_sizing(self):
        """Initialize confluence-based position sizing (unchanged proven logic)"""
        self.base_position_sizes = {
            'conservative': {3: 0.03, 4: 0.05, 5: 0.07, 6: 0.08, 7: 0.10},
            'moderate': {3: 0.05, 4: 0.08, 5: 0.12, 6: 0.15, 7: 0.18},
            'aggressive': {3: 0.08, 4: 0.12, 5: 0.18, 6: 0.22, 7: 0.25}
        }
        self.position_sizes = self.base_position_sizes[self.risk_profile]
    
    def get_volatility_regime(self, df: pd.DataFrame, current_idx: int) -> str:
        """OPTIMIZATION 3: Detect volatility regime"""
        if not self.volatility_regime_enabled or current_idx < self.regime_lookback:
            return 'normal'
        
        # Calculate volatility as ATR percentage
        recent_data = df.iloc[current_idx-self.regime_lookback:current_idx]
        atr_pct = recent_data['atr'] / recent_data['Close'] * 100
        
        current_vol = atr_pct.iloc[-1]
        avg_vol = atr_pct.mean()
        vol_std = atr_pct.std()
        
        if current_vol > avg_vol + vol_std:
            return 'high_volatility'
        elif current_vol < avg_vol - vol_std:
            return 'low_volatility'
        return 'normal_volatility'
    
    def calculate_dynamic_volume_threshold(self, df: pd.DataFrame, current_idx: int) -> float:
        """OPTIMIZATION 2: Dynamic volume filtering using percentiles"""
        if current_idx < self.volume_lookback:
            # Fallback to original method for early periods
            volume_sma = df['Volume'].iloc[:current_idx].mean()
            return volume_sma * 1.2
        
        # Use percentile-based threshold
        recent_volume = df['Volume'].iloc[current_idx-self.volume_lookback:current_idx]
        threshold = np.percentile(recent_volume, self.volume_percentile)
        return threshold
    
    def calculate_confluence_score(self, df: pd.DataFrame, idx: int) -> Tuple[float, Dict]:
        """
        Enhanced confluence calculation with regime awareness
        Returns float (vs int) for more precise threshold testing
        """
        if idx < 100:
            return 0.0, {}
        
        score = 0.0
        details = {}
        current_data = df.iloc[idx]
        
        # Get market regime
        volatility_regime = self.get_volatility_regime(df, idx)
        details['volatility_regime'] = volatility_regime
        
        # 1. Trend Alignment Score (0-2 points) - UNCHANGED
        close = current_data['Close']
        ema8, ema21, ema50, ema100 = current_data['ema_8'], current_data['ema_21'], current_data['ema_50'], current_data['ema_100']
        
        if close > ema8 > ema21 > ema50 > ema100:
            trend_score = 2.0
            trend_direction = 1
            details['trend'] = 'Strong Bullish Alignment'
        elif close < ema8 < ema21 < ema50 < ema100:
            trend_score = 2.0
            trend_direction = -1
            details['trend'] = 'Strong Bearish Alignment'
        elif close > ema8 > ema21 > ema50:
            trend_score = 1.0
            trend_direction = 1
            details['trend'] = 'Moderate Bullish'
        elif close < ema8 < ema21 < ema50:
            trend_score = 1.0
            trend_direction = -1
            details['trend'] = 'Moderate Bearish'
        else:
            trend_score = 0.0
            trend_direction = 0
            details['trend'] = 'Mixed/Sideways'
        
        score += trend_score
        details['trend_score'] = trend_score
        details['trend_direction'] = trend_direction
        
        # 2. Momentum Confluence (0-2 points) - UNCHANGED
        rsi14, rsi21 = current_data['rsi_14'], current_data['rsi_21']
        macd, macd_signal = current_data['macd'], current_data['macd_signal']
        macd_hist = current_data['macd_histogram']
        
        # RSI momentum
        rsi_bullish = 30 < rsi14 < 80 and 30 < rsi21 < 80 and rsi14 > rsi21
        rsi_bearish = 20 < rsi14 < 70 and 20 < rsi21 < 70 and rsi14 < rsi21
        
        # MACD momentum  
        macd_bullish = macd > macd_signal and macd_hist > 0
        macd_bearish = macd < macd_signal and macd_hist < 0
        
        momentum_score = 0.0
        if (rsi_bullish and macd_bullish and trend_direction > 0) or \
           (rsi_bearish and macd_bearish and trend_direction < 0):
            momentum_score = 2.0
        elif ((rsi_bullish or macd_bullish) and trend_direction > 0) or \
             ((rsi_bearish or macd_bearish) and trend_direction < 0):
            momentum_score = 1.0
        
        score += momentum_score
        details['momentum_score'] = momentum_score
        
        # 3. Market Regime Score (0-1 points) - ENHANCED
        regime_score = 0.0
        adx = current_data['adx']
        
        # ADX strength (unchanged)
        if adx >= 25:
            regime_score += 0.5
        elif adx >= 20:
            regime_score += 0.3
        
        # OPTIMIZATION: Volatility regime bonus/penalty
        if volatility_regime == 'high_volatility' and trend_direction != 0:
            regime_score += 0.3  # High volatility trends can be very profitable
        elif volatility_regime == 'low_volatility':
            regime_score += 0.2  # Low volatility is generally safer
        # Normal volatility gets no bonus/penalty
        
        score += regime_score
        details['regime_score'] = regime_score
        
        # 4. Volume Confirmation (0-1 points) - ENHANCED
        volume_threshold = self.calculate_dynamic_volume_threshold(df, idx)
        current_volume = current_data['Volume']
        
        volume_score = 0.0
        if current_volume >= volume_threshold:
            volume_score = 1.0
        elif current_volume >= volume_threshold * 0.8:
            volume_score = 0.5
        
        score += volume_score
        details['volume_score'] = volume_score
        details['volume_threshold'] = volume_threshold
        
        # 5. Pattern Recognition (0-1 points) - UNCHANGED
        pattern_score = 0.0
        bb_position = current_data['bb_position']
        
        if trend_direction > 0:
            if 0.1 <= bb_position <= 0.8:  # Not at extremes
                pattern_score = 1.0
        elif trend_direction < 0:
            if 0.2 <= bb_position <= 0.9:
                pattern_score = 1.0
        
        score += pattern_score
        details['pattern_score'] = pattern_score
        
        # Final score and direction
        details['final_score'] = round(score, 2)
        details['signal_direction'] = trend_direction if score >= self.confluence_threshold else 0
        
        return score, details
    
    def should_enter_trade(self, confluence_score: float, confluence_details: Dict, df: pd.DataFrame, idx: int) -> bool:
        """Enhanced entry logic with regime awareness"""
        # Primary threshold check (OPTIMIZED)
        if confluence_score < self.confluence_threshold:
            self.trades_skipped_filters['weak_confluence'] += 1
            return False
        
        # Market regime filter
        regime = confluence_details.get('volatility_regime', 'normal')
        trend_direction = confluence_details.get('trend_direction', 0)
        
        # Skip trades in extreme volatility without strong trend
        if regime == 'high_volatility' and abs(trend_direction) < 1:
            self.trades_skipped_filters['regime_mismatch'] += 1
            return False
        
        # All other filters remain unchanged from proven strategy
        current_data = df.iloc[idx]
        
        # Trend filter
        if trend_direction == 0:
            self.trades_skipped_filters['no_trend'] += 1
            return False
        
        # Volume filter (now dynamic)
        volume_threshold = self.calculate_dynamic_volume_threshold(df, idx)
        if current_data['Volume'] < volume_threshold * 0.8:
            self.trades_skipped_filters['low_volume'] += 1
            return False
        
        # Risk management checks (unchanged)
        if self.emergency_stop or self.daily_emergency_stop:
            return False
        
        daily_loss = self.daily_starting_balance - self.current_balance
        if daily_loss >= self.max_daily_loss:
            return False
        
        return True
    
    def run_backtest(self, start_date: str = "2024-01-01", end_date: str = "2024-03-01") -> Optional[pd.DataFrame]:
        """Run optimized backtest with enhanced reporting"""
        print(f"\n🚀 BTCUSDT OPTIMIZED STRATEGY BACKTEST")
        print("=" * 55)
        print(f"🎯 Testing confluence threshold: {self.confluence_threshold}")
        print(f"📊 Volume filter: Top {100-self.volume_percentile}% dynamic")
        print(f"🌡️ Regime detection: {'Enabled' if self.volatility_regime_enabled else 'Disabled'}")
        
        # Fetch data
        print(f"📊 Fetching BTC-USD data from {start_date} to {end_date} (1h)")
        df = self.data_fetcher.fetch_btc_data(start_date, end_date, "1h")
        
        if df is None or df.empty:
            print("❌ Failed to fetch data")
            return None
        
        print(f"✅ Data loaded: {len(df)} periods")
        
        # Calculate indicators (same as proven strategy)
        df = self._calculate_all_indicators(df)
        print("🔧 Technical indicators calculated")
        
        # Reset state
        self._reset_backtest_state()
        
        # Run simulation
        print("📈 Running optimized simulation...")
        
        balance_history = [self.current_balance]
        regime_counts = {'high_volatility': 0, 'low_volatility': 0, 'normal_volatility': 0}
        
        for i in range(100, len(df)):  # Start after indicator warm-up
            current_data = df.iloc[i]
            current_date = df.index[i].date()
            
            # Update daily tracking
            if current_date != self.current_date:
                self._update_daily_tracking(current_date)
            
            # Calculate confluence
            confluence_score, confluence_details = self.calculate_confluence_score(df, i)
            self.confluence_scores.append(confluence_score)
            
            # Track regime distribution
            regime = confluence_details.get('volatility_regime', 'normal_volatility')
            regime_counts[regime] += 1
            
            # Check for trade entry
            if self.current_position == 0 and self.should_enter_trade(confluence_score, confluence_details, df, i):
                self._enter_trade(current_data, confluence_score, confluence_details)
            
            # Check for trade exit
            elif self.current_position != 0:
                if self._should_exit_trade(current_data, df, i):
                    self._exit_trade(current_data)
            
            # Update balance history
            balance_history.append(self.current_balance)
            
            # Emergency stops
            if self._check_emergency_stops():
                break
        
        # Final results
        self._print_optimized_results(regime_counts)
        
        return df
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators (unchanged from proven strategy)"""
        # EMA calculations
        df['ema_8'] = df['Close'].ewm(span=8).mean()
        df['ema_21'] = df['Close'].ewm(span=21).mean()
        df['ema_50'] = df['Close'].ewm(span=50).mean()
        df['ema_100'] = df['Close'].ewm(span=100).mean()
        
        # RSI calculations
        df['rsi_14'] = self._calculate_rsi(df['Close'], 14)
        df['rsi_21'] = self._calculate_rsi(df['Close'], 21)
        
        # MACD calculations
        df['macd'] = df['ema_8'] - df['ema_21']
        df['macd_signal'] = df['macd'].ewm(span=7).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # ATR and ADX
        df = self._calculate_atr(df)
        df = self._calculate_adx(df)
        
        # Bollinger Bands
        df = self._calculate_bollinger_bands(df)
        
        # Volume indicators
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI (unchanged)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ATR (unchanged)"""
        df['high_low'] = df['High'] - df['Low']
        df['high_close'] = abs(df['High'] - df['Close'].shift(1))
        df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['true_range'].rolling(window=period).mean()
        return df
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ADX (unchanged)"""
        df['dm_plus'] = np.where(
            (df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
            np.maximum(df['High'] - df['High'].shift(1), 0), 0
        )
        df['dm_minus'] = np.where(
            (df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
            np.maximum(df['Low'].shift(1) - df['Low'], 0), 0
        )
        
        df['di_plus'] = 100 * (df['dm_plus'].rolling(window=period).mean() / df['atr'])
        df['di_minus'] = 100 * (df['dm_minus'].rolling(window=period).mean() / df['atr'])
        df['dx'] = 100 * abs(df['di_plus'] - df['di_minus']) / (df['di_plus'] + df['di_minus'])
        df['adx'] = df['dx'].rolling(window=period).mean()
        df['adx'] = df['adx'].fillna(0)
        
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Calculate Bollinger Bands (unchanged)"""
        df['bb_middle'] = df['Close'].rolling(window=period).mean()
        bb_std = df['Close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std_dev)
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        return df
    
    def _reset_backtest_state(self):
        """Reset state for backtest (unchanged)"""
        self.current_balance = self.initial_balance
        self.trades = []
        self.daily_pnl = []
        self.equity_curve = []
        self.current_position = 0
        self.current_entry_price = 0
        self.trading_days = set()
        self.current_date = None
        self.daily_starting_balance = self.initial_balance
        self.can_trade_today = True
        self.max_balance = self.initial_balance
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.emergency_stop = False
        self.daily_emergency_stop = False
        self.confluence_scores = []
        self.market_regimes = []
    
    def _update_daily_tracking(self, current_date):
        """Update daily tracking (unchanged)"""
        if self.current_date is not None:
            daily_pnl = self.current_balance - self.daily_starting_balance
            self.daily_pnl.append(daily_pnl)
        
        self.current_date = current_date
        self.daily_starting_balance = self.current_balance
        self.daily_emergency_stop = False
        self.can_trade_today = True
        self.trading_days.add(current_date)
    
    def _enter_trade(self, current_data, confluence_score: float, confluence_details: Dict):
        """Enter trade with proven position sizing logic"""
        signal_direction = confluence_details['signal_direction']
        if signal_direction == 0:
            return
        
        # Position sizing based on confluence score (unchanged proven logic)
        confluence_int = min(7, max(3, int(confluence_score)))
        position_size_pct = self.position_sizes.get(confluence_int, 0.05)
        position_value = self.current_balance * position_size_pct
        position_value = min(position_value, self.max_position_size)
        
        # Entry price and position
        entry_price = current_data['Close']
        self.current_position = position_value / entry_price * signal_direction
        self.current_entry_price = entry_price
        
        # Calculate stop loss and take profit (unchanged)
        atr = current_data['atr']
        if signal_direction > 0:  # Long
            stop_loss = entry_price - (atr * 2)
            take_profit = entry_price + (atr * 3)
        else:  # Short
            stop_loss = entry_price + (atr * 2)
            take_profit = entry_price - (atr * 3)
        
        # Record trade entry
        trade_entry = {
            'entry_time': current_data.name,
            'entry_price': entry_price,
            'position_size': abs(self.current_position),
            'position_value': position_value,
            'direction': 'long' if signal_direction > 0 else 'short',
            'confluence_score': confluence_score,
            'confluence_details': confluence_details,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'volatility_regime': confluence_details.get('volatility_regime', 'normal')
        }
        
        self.trades.append(trade_entry)
    
    def _should_exit_trade(self, current_data, df: pd.DataFrame, idx: int) -> bool:
        """Check exit conditions (unchanged proven logic)"""
        if not self.trades or self.current_position == 0:
            return False
        
        current_trade = self.trades[-1]
        current_price = current_data['Close']
        
        # Stop loss
        if self.current_position > 0:  # Long position
            if current_price <= current_trade['stop_loss']:
                return True
            if current_price >= current_trade['take_profit']:
                return True
        else:  # Short position
            if current_price >= current_trade['stop_loss']:
                return True
            if current_price <= current_trade['take_profit']:
                return True
        
        return False
    
    def _exit_trade(self, current_data):
        """Exit current trade (unchanged proven logic)"""
        if not self.trades or self.current_position == 0:
            return
        
        current_trade = self.trades[-1]
        exit_price = current_data['Close']
        
        # Calculate P&L
        if self.current_position > 0:  # Long
            pnl = (exit_price - current_trade['entry_price']) * abs(self.current_position)
        else:  # Short
            pnl = (current_trade['entry_price'] - exit_price) * abs(self.current_position)
        
        # Update balance
        self.current_balance += pnl
        self.max_balance = max(self.max_balance, self.current_balance)
        
        # Update trade record
        current_trade['exit_time'] = current_data.name
        current_trade['exit_price'] = exit_price
        current_trade['pnl'] = pnl
        current_trade['return_pct'] = (pnl / current_trade['position_value']) * 100
        
        # Update consecutive tracking
        if pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Clear position
        self.current_position = 0
        self.current_entry_price = 0
    
    def _check_emergency_stops(self) -> bool:
        """Check emergency stop conditions (unchanged)"""
        total_loss = self.initial_balance - self.current_balance
        daily_loss = self.daily_starting_balance - self.current_balance
        
        if total_loss >= self.max_total_loss:
            self.emergency_stop = True
            return True
        
        if daily_loss >= self.max_daily_loss:
            self.daily_emergency_stop = True
            return True
        
        return False
    
    def _print_optimized_results(self, regime_counts):
        """Print enhanced results with optimization metrics"""
        if not self.trades:
            print("❌ No trades executed")
            return
        
        # Calculate metrics
        completed_trades = [t for t in self.trades if 'pnl' in t]
        if not completed_trades:
            print("❌ No completed trades")
            return
        
        total_pnl = sum([t['pnl'] for t in completed_trades])
        win_trades = [t for t in completed_trades if t['pnl'] > 0]
        loss_trades = [t for t in completed_trades if t['pnl'] <= 0]
        
        win_rate = len(win_trades) / len(completed_trades) * 100
        total_return = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        print(f"\n🏆 BTCUSDT OPTIMIZED STRATEGY RESULTS")
        print("=" * 50)
        print(f"Initial Balance:        ${self.initial_balance:,.2f}")
        print(f"Final Balance:          ${self.current_balance:,.2f}")
        print(f"Profit/Loss:            {total_return:+.2f}%")
        
        print(f"\n📊 OPTIMIZED PERFORMANCE:")
        print(f"Trading Days:           {len(self.trading_days)}")
        print(f"Total Trades:           {len(completed_trades)}")
        print(f"Win Rate:               {win_rate:.1f}%")
        
        if win_trades:
            print(f"Average Win:            ${np.mean([t['pnl'] for t in win_trades]):,.2f}")
            print(f"Largest Win:            ${max([t['pnl'] for t in win_trades]):,.2f}")
        
        if loss_trades:
            print(f"Average Loss:           ${np.mean([t['pnl'] for t in loss_trades]):,.2f}")
            print(f"Largest Loss:           ${min([t['pnl'] for t in loss_trades]):,.2f}")
        
        # Optimization-specific metrics
        print(f"\n📈 OPTIMIZATION ANALYSIS:")
        print(f"Confluence Threshold:   {self.confluence_threshold} (vs 4.0 baseline)")
        avg_confluence = np.mean(self.confluence_scores) if self.confluence_scores else 0
        print(f"Average Confluence:     {avg_confluence:.2f}/7")
        
        # High confluence trades
        high_confluence_trades = [t for t in completed_trades if t['confluence_score'] >= 5.0]
        print(f"High Confluence (5+):   {len(high_confluence_trades)}")
        
        # Volume filtering effectiveness
        total_filtered = sum(self.trades_skipped_filters.values())
        print(f"Dynamic Volume Filter:  Top {100-self.volume_percentile}% periods")
        
        # Market regime analysis
        print(f"\n🌡️ MARKET REGIME DISTRIBUTION:")
        total_periods = sum(regime_counts.values())
        for regime, count in regime_counts.items():
            pct = count / total_periods * 100 if total_periods > 0 else 0
            print(f"{regime.replace('_', ' ').title()}: {count:>8} periods ({pct:.1f}%)")
        
        # Regime-specific trade performance
        regime_trades = {}
        for trade in completed_trades:
            regime = trade.get('volatility_regime', 'unknown')
            if regime not in regime_trades:
                regime_trades[regime] = []
            regime_trades[regime].append(trade)
        
        print(f"\n📊 REGIME PERFORMANCE:")
        for regime, trades in regime_trades.items():
            if trades:
                regime_wins = [t for t in trades if t['pnl'] > 0]
                regime_win_rate = len(regime_wins) / len(trades) * 100
                regime_pnl = sum([t['pnl'] for t in trades])
                print(f"{regime.replace('_', ' ').title()}: {len(trades)} trades, {regime_win_rate:.1f}% win rate, ${regime_pnl:+.2f}")
        
        print(f"\n🔍 FILTER EFFECTIVENESS:")
        for filter_name, count in self.trades_skipped_filters.items():
            filter_display = filter_name.replace('_', ' ').title()
            print(f"{filter_display}: {count:>8}")
        print(f"Total Filtered:         {total_filtered:>8}")
        
        # Performance comparison hint
        print(f"\n💡 OPTIMIZATION IMPACT:")
        print(f"✅ Confluence threshold: {self.confluence_threshold} (optimized)")
        print(f"✅ Dynamic volume filter: Percentile-based")
        print(f"✅ Volatility regime detection: Enabled")
        print(f"📊 Compare with baseline 4.0 threshold for improvement validation")

def main():
    """Test optimized strategy"""
    print("🧪 Testing BTCUSDT Optimized Strategy")
    print("=" * 45)
    
    # Test different risk profiles
    profiles = ['conservative', 'moderate', 'aggressive']
    
    for profile in profiles:
        print(f"\n🎯 Testing {profile.upper()} profile:")
        strategy = BTCUSDTOptimizedStrategy(account_size=10000, risk_profile=profile)
        
        # Run short test
        result = strategy.run_backtest("2024-01-01", "2024-03-01")
        
        if result is not None:
            print(f"✅ {profile.title()} profile test completed")
        else:
            print(f"❌ {profile.title()} profile test failed")
    
    print(f"\n🎉 OPTIMIZATION TESTING COMPLETE")
    print("💡 Ready for out-of-sample validation")

if __name__ == "__main__":
    main()