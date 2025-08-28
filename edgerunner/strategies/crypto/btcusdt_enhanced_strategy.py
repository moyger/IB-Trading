#!/usr/bin/env python3
"""
BTCUSDT Enhanced Multi-Confluence Strategy
Combines proven FTMO methodology with advanced quantitative techniques

Key Enhancements:
- Multi-indicator confluence scoring system
- Advanced market regime detection (ADX + trend alignment)
- Dynamic position sizing based on signal strength
- Enhanced risk management with profit acceleration
- Machine learning-inspired pattern recognition
- Crypto-optimized parameters for 24/7 trading

Performance Target: 41.7% success rate with 36.2% average profit (proven baseline)
Goal: Improve to 50%+ success rate while maintaining strong profit potential
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from data_fetcher import BTCDataFetcher
from typing import Optional, Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class BTCUSDTEnhancedStrategy:
    """Enhanced BTCUSDT strategy with multi-confluence approach"""
    
    def __init__(self, account_size: float = 10000, risk_profile: str = 'moderate'):
        """
        Initialize enhanced BTCUSDT strategy
        
        Args:
            account_size: Trading capital
            risk_profile: 'conservative', 'moderate', 'aggressive'
        """
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.risk_profile = risk_profile
        
        # Initialize data fetcher
        self.data_fetcher = BTCDataFetcher()
        
        # Enhanced Risk Parameters (from proven strategy)
        self._init_risk_parameters()
        
        # Enhanced Position Sizing (confluence-based)
        self._init_position_sizing()
        
        # Trading State
        self.trades = []
        self.daily_pnl = []
        self.equity_curve = []
        self.current_position = 0
        self.current_entry_price = 0
        self.trading_days = set()
        self.challenge_complete = False
        
        # Enhanced Tracking
        self.current_date = None
        self.daily_starting_balance = account_size
        self.can_trade_today = True
        self.max_balance = account_size
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # Risk Monitoring
        self.risk_alerts = []
        self.emergency_stop = False
        self.daily_emergency_stop = False
        
        # Market Regime & Pattern Recognition
        self.market_regime_history = []
        self.pattern_recognition_cache = {}
        
        # Strategy Performance Tracking
        self.confluence_scores = []
        self.trades_skipped_filters = {
            'no_trend': 0,
            'low_volume': 0,
            'low_volatility': 0,
            'weak_confluence': 0,
            'pattern_rejection': 0
        }
        
        print(f"🚀 BTCUSDT ENHANCED MULTI-CONFLUENCE STRATEGY ({risk_profile.upper()})")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"🎯 Target: Enhanced success rate with maintained profit potential")
        print(f"📊 Features: Multi-indicator confluence + pattern recognition")
        
    def _init_risk_parameters(self):
        """Initialize risk parameters based on proven methodology"""
        risk_configs = {
            'conservative': {
                'max_daily_loss_pct': 3.0,
                'max_overall_loss_pct': 8.0,
                'daily_loss_cutoff_pct': 1.0,
                'overall_loss_cutoff_pct': 4.0,
                'daily_loss_emergency_pct': 0.5,
                'max_risk_per_trade_hard_cap': 1.5,
                'profit_target_pct': 15.0
            },
            'moderate': {
                'max_daily_loss_pct': 4.0,
                'max_overall_loss_pct': 10.0,
                'daily_loss_cutoff_pct': 1.5,
                'overall_loss_cutoff_pct': 5.0,
                'daily_loss_emergency_pct': 1.0,
                'max_risk_per_trade_hard_cap': 2.0,
                'profit_target_pct': 20.0
            },
            'aggressive': {
                'max_daily_loss_pct': 6.0,
                'max_overall_loss_pct': 12.0,
                'daily_loss_cutoff_pct': 2.0,
                'overall_loss_cutoff_pct': 6.0,
                'daily_loss_emergency_pct': 1.5,
                'max_risk_per_trade_hard_cap': 3.0,
                'profit_target_pct': 25.0
            }
        }
        
        config = risk_configs[self.risk_profile]
        for key, value in config.items():
            setattr(self, key, value)
            
        # Additional parameters
        self.target_timeframe_days = 30
        self.min_trading_days = 5
        self.hourly_trades_limit = 3
        self.current_hour_trades = 0
        self.current_hour = None
        
    def _init_position_sizing(self):
        """Initialize enhanced position sizing based on confluence scores"""
        sizing_configs = {
            'conservative': {
                # Confluence score: (base_risk_pct, leverage)
                0: (0.0, 0.0),   # No position
                1: (0.2, 1.0),   # Very weak
                2: (0.4, 1.0),   # Weak
                3: (0.6, 1.0),   # Moderate
                4: (0.8, 1.0),   # Strong
                5: (1.0, 1.0),   # Very strong
                6: (1.2, 1.0),   # Exceptional
                7: (1.4, 1.0),   # Perfect confluence
            },
            'moderate': {
                0: (0.0, 0.0),
                1: (0.3, 1.0),
                2: (0.6, 1.0),
                3: (0.9, 1.0),
                4: (1.2, 1.0),
                5: (1.5, 1.0),
                6: (1.8, 1.0),
                7: (2.0, 1.0),
            },
            'aggressive': {
                0: (0.0, 0.0),
                1: (0.5, 1.0),
                2: (1.0, 1.0),
                3: (1.5, 1.0),
                4: (2.0, 1.0),
                5: (2.5, 1.0),
                6: (2.8, 1.0),
                7: (3.0, 1.0),
            }
        }
        
        self.confluence_position_sizing = sizing_configs[self.risk_profile]
        
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators for confluence analysis"""
        if len(df) < 100:
            return df
        
        # Moving Averages (Multiple timeframes)
        df['ema_8'] = df['Close'].ewm(span=8).mean()
        df['ema_21'] = df['Close'].ewm(span=21).mean()
        df['ema_50'] = df['Close'].ewm(span=50).mean()
        df['ema_100'] = df['Close'].ewm(span=100).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI (Multiple periods for confluence)
        df['rsi_14'] = self._calculate_rsi(df['Close'], 14)
        df['rsi_21'] = self._calculate_rsi(df['Close'], 21)
        
        # MACD (Optimized for crypto)
        df['macd'] = df['ema_8'] - df['ema_21']
        df['macd_signal'] = df['macd'].ewm(span=7).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # ADX for trend strength
        df = self._calculate_adx(df)
        
        # Bollinger Bands
        df = self._calculate_bollinger_bands(df)
        
        # Volume indicators
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Volatility indicators
        df['atr'] = df['true_range'].rolling(window=14).mean()
        df['volatility_ratio'] = df['atr'] / df['atr'].rolling(window=24).mean()
        
        # Price patterns
        df = self._calculate_price_patterns(df)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI with improved accuracy"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ADX with DI+ and DI- components"""
        # Calculate directional movement
        df['dm_plus'] = np.where(
            (df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
            np.maximum(df['High'] - df['High'].shift(1), 0), 0
        )
        df['dm_minus'] = np.where(
            (df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
            np.maximum(df['Low'].shift(1) - df['Low'], 0), 0
        )
        
        # Calculate True Range if not already calculated
        if 'true_range' not in df.columns:
            df['high_low'] = df['High'] - df['Low']
            df['high_close'] = abs(df['High'] - df['Close'].shift(1))
            df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
            df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        
        # Smooth the values
        df['atr'] = df['true_range'].rolling(window=period).mean()
        df['di_plus'] = 100 * (df['dm_plus'].rolling(window=period).mean() / df['atr'])
        df['di_minus'] = 100 * (df['dm_minus'].rolling(window=period).mean() / df['atr'])
        
        # Calculate DX and ADX
        df['dx'] = 100 * abs(df['di_plus'] - df['di_minus']) / (df['di_plus'] + df['di_minus'])
        df['adx'] = df['dx'].rolling(window=period).mean()
        
        # Fill NaN values
        df['adx'] = df['adx'].fillna(0)
        df['di_plus'] = df['di_plus'].fillna(0)
        df['di_minus'] = df['di_minus'].fillna(0)
        
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df['bb_middle'] = df['Close'].rolling(window=period).mean()
        bb_std = df['Close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std_dev)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def _calculate_price_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate price pattern indicators"""
        # Higher highs and lower lows
        df['higher_high'] = (df['High'] > df['High'].shift(1)) & (df['High'].shift(1) > df['High'].shift(2))
        df['lower_low'] = (df['Low'] < df['Low'].shift(1)) & (df['Low'].shift(1) < df['Low'].shift(2))
        
        # Price breakouts
        df['breakout_up'] = df['Close'] > df['High'].rolling(window=20).max().shift(1)
        df['breakout_down'] = df['Close'] < df['Low'].rolling(window=20).min().shift(1)
        
        # Gap analysis
        df['gap_up'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) > 0.005
        df['gap_down'] = (df['Close'].shift(1) - df['Open']) / df['Close'].shift(1) > 0.005
        
        return df
    
    def calculate_confluence_score(self, df: pd.DataFrame, idx: int) -> Tuple[int, Dict]:
        """
        Calculate multi-indicator confluence score (0-7 scale)
        Higher scores indicate stronger signals
        """
        if idx < 100:  # Need sufficient data
            return 0, {}
        
        score = 0
        details = {}
        current_data = df.iloc[idx]
        
        # 1. Trend Alignment Score (0-2 points)
        trend_score = 0
        close = current_data['Close']
        ema8, ema21, ema50, ema100 = current_data['ema_8'], current_data['ema_21'], current_data['ema_50'], current_data['ema_100']
        
        # Perfect trend alignment
        if close > ema8 > ema21 > ema50 > ema100:
            trend_score = 2
            details['trend'] = 'Strong Bullish Alignment'
        elif close < ema8 < ema21 < ema50 < ema100:
            trend_score = -2
            details['trend'] = 'Strong Bearish Alignment'
        # Partial trend alignment
        elif close > ema8 > ema21 > ema50:
            trend_score = 1
            details['trend'] = 'Moderate Bullish'
        elif close < ema8 < ema21 < ema50:
            trend_score = -1
            details['trend'] = 'Moderate Bearish'
        else:
            trend_score = 0
            details['trend'] = 'Mixed/Sideways'
        
        score += abs(trend_score)
        details['trend_score'] = trend_score
        
        # 2. Momentum Confluence (0-2 points)
        momentum_score = 0
        rsi14, rsi21 = current_data['rsi_14'], current_data['rsi_21']
        macd, macd_signal = current_data['macd'], current_data['macd_signal']
        macd_hist = current_data['macd_histogram']
        
        # RSI momentum
        rsi_bullish = 30 < rsi14 < 80 and 30 < rsi21 < 80 and rsi14 > rsi21
        rsi_bearish = 20 < rsi14 < 70 and 20 < rsi21 < 70 and rsi14 < rsi21
        
        # MACD momentum  
        macd_bullish = macd > macd_signal and macd_hist > 0
        macd_bearish = macd < macd_signal and macd_hist < 0
        
        if (rsi_bullish and macd_bullish and trend_score > 0):
            momentum_score = 2
            details['momentum'] = 'Strong Bullish Momentum'
        elif (rsi_bearish and macd_bearish and trend_score < 0):
            momentum_score = -2
            details['momentum'] = 'Strong Bearish Momentum'
        elif (rsi_bullish or macd_bullish) and trend_score > 0:
            momentum_score = 1
            details['momentum'] = 'Moderate Bullish'
        elif (rsi_bearish or macd_bearish) and trend_score < 0:
            momentum_score = -1
            details['momentum'] = 'Moderate Bearish'
        else:
            momentum_score = 0
            details['momentum'] = 'Neutral'
        
        score += abs(momentum_score)
        details['momentum_score'] = momentum_score
        
        # 3. Market Regime Filter (0-1 points)
        regime_score = 0
        adx = current_data['adx']
        
        if adx >= 25:  # Strong trend
            regime_score = 1
            details['regime'] = f'Strong Trend (ADX: {adx:.1f})'
        elif adx >= 20:  # Moderate trend
            regime_score = 1
            details['regime'] = f'Moderate Trend (ADX: {adx:.1f})'
        else:
            regime_score = 0
            details['regime'] = f'No Trend (ADX: {adx:.1f})'
            
        score += regime_score
        details['regime_score'] = regime_score
        
        # 4. Volume & Volatility Confirmation (0-1 points)
        volume_vol_score = 0
        volume_ratio = current_data['volume_ratio']
        volatility_ratio = current_data.get('volatility_ratio', 1.0)
        
        if volume_ratio >= 1.2 and volatility_ratio >= 1.1:
            volume_vol_score = 1
            details['volume_volatility'] = 'Strong Confirmation'
        elif volume_ratio >= 0.8 and volatility_ratio >= 0.8:
            volume_vol_score = 0.5
            details['volume_volatility'] = 'Moderate Confirmation'
        else:
            volume_vol_score = 0
            details['volume_volatility'] = 'Weak Confirmation'
            
        score += volume_vol_score
        details['volume_vol_score'] = volume_vol_score
        
        # 5. Pattern Recognition Bonus (0-1 points)
        pattern_score = 0
        
        # Bollinger Band patterns
        bb_position = current_data['bb_position']
        if trend_score > 0 and bb_position < 0.2:  # Bullish bounce from lower band
            pattern_score = 1
            details['pattern'] = 'BB Lower Band Bounce'
        elif trend_score < 0 and bb_position > 0.8:  # Bearish rejection from upper band
            pattern_score = 1
            details['pattern'] = 'BB Upper Band Rejection'
        elif current_data.get('breakout_up', False) and trend_score > 0:
            pattern_score = 1
            details['pattern'] = 'Bullish Breakout'
        elif current_data.get('breakout_down', False) and trend_score < 0:
            pattern_score = 1
            details['pattern'] = 'Bearish Breakdown'
        else:
            pattern_score = 0
            details['pattern'] = 'No Clear Pattern'
            
        score += pattern_score
        details['pattern_score'] = pattern_score
        
        # Final score adjustment based on direction consistency
        direction_consistent = (trend_score > 0 and momentum_score > 0) or (trend_score < 0 and momentum_score < 0)
        if direction_consistent:
            final_score = min(7, int(score))
        else:
            final_score = max(0, int(score) - 1)  # Penalty for conflicting signals
            details['direction_penalty'] = True
        
        details['final_score'] = final_score
        details['signal_direction'] = 'LONG' if (trend_score + momentum_score) > 0 else 'SHORT'
        
        return final_score, details
    
    def check_entry_conditions(self, df: pd.DataFrame, idx: int) -> Tuple[bool, float, str, Dict]:
        """
        Enhanced entry condition check with confluence scoring
        Returns: (can_enter, position_size_multiplier, reason, details)
        """
        confluence_score, confluence_details = self.calculate_confluence_score(df, idx)
        
        # Minimum confluence threshold
        min_confluence = 3 if self.risk_profile == 'aggressive' else 4
        
        if confluence_score < min_confluence:
            self.trades_skipped_filters['weak_confluence'] += 1
            return False, 0, f"Weak confluence ({confluence_score}/{min_confluence})", confluence_details
        
        # Additional safety checks
        current_data = df.iloc[idx]
        
        # Volume check
        if current_data['volume_ratio'] < 0.6:
            self.trades_skipped_filters['low_volume'] += 1
            return False, 0, "Insufficient volume", confluence_details
        
        # Volatility check
        volatility_ratio = current_data.get('volatility_ratio', 1.0)
        if volatility_ratio < 0.5:
            self.trades_skipped_filters['low_volatility'] += 1
            return False, 0, "Low volatility environment", confluence_details
        
        # Risk management checks
        if self.emergency_stop or self.daily_emergency_stop:
            return False, 0, "Emergency stop active", confluence_details
        
        if not self.check_hourly_trade_limit(df.index[idx].hour):
            return False, 0, "Hourly trade limit reached", confluence_details
        
        # Calculate position size multiplier based on confluence strength
        multiplier = self._calculate_confluence_multiplier(confluence_score, confluence_details)
        
        return True, multiplier, f"Confluence approved ({confluence_score}/7)", confluence_details
    
    def _calculate_confluence_multiplier(self, score: int, details: Dict) -> float:
        """Calculate position size multiplier based on confluence strength"""
        base_multiplier = min(score / 7.0, 1.0)  # Score 7 = 100% of base size
        
        # Bonus for perfect alignment
        if score >= 6:
            base_multiplier *= 1.2
        elif score >= 5:
            base_multiplier *= 1.1
        
        # Volume/volatility boost
        if details.get('volume_vol_score', 0) >= 1:
            base_multiplier *= 1.1
        
        # Pattern recognition boost
        if details.get('pattern_score', 0) >= 1:
            base_multiplier *= 1.05
        
        return min(base_multiplier, 1.5)  # Cap at 150% of base
    
    def check_hourly_trade_limit(self, hour: int) -> bool:
        """Check hourly trading limits"""
        if hour != self.current_hour:
            self.current_hour = hour
            self.current_hour_trades = 0
        
        return self.current_hour_trades < self.hourly_trades_limit
    
    def calculate_position_size(self, confluence_score: int, current_price: float, 
                              atr: float, multiplier: float = 1.0) -> Tuple[float, float, float, float]:
        """Calculate position size based on confluence score and risk parameters"""
        if confluence_score not in self.confluence_position_sizing:
            return 0, 0, 0, 0
        
        base_risk_pct, leverage = self.confluence_position_sizing[confluence_score]
        
        if base_risk_pct == 0:
            return 0, 0, 0, 0
        
        # Apply multiplier
        final_risk_pct = base_risk_pct * multiplier
        
        # Risk management caps
        if final_risk_pct > self.max_risk_per_trade_hard_cap:
            final_risk_pct = self.max_risk_per_trade_hard_cap
        
        # Dynamic risk adjustment based on current performance
        final_risk_pct = self._adjust_risk_for_performance(final_risk_pct)
        
        # Calculate stop loss distance (crypto-optimized)
        stop_distance = atr * 2.0  # Wider stops for crypto volatility
        
        # Position size calculation
        risk_amount = self.current_balance * (final_risk_pct / 100)
        position_size = risk_amount / stop_distance
        position_value = position_size * current_price
        
        return position_size, stop_distance, final_risk_pct, position_value
    
    def _adjust_risk_for_performance(self, base_risk: float) -> float:
        """Adjust risk based on current performance and streak"""
        # Calculate current profit/loss
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        # Profit acceleration
        if profit_pct > 2.0 and self.consecutive_wins >= 2:
            multiplier = min(1.3, 1.0 + (profit_pct * 0.015))
            return base_risk * multiplier
        
        # Conservative adjustment after losses
        if self.consecutive_losses >= 2:
            return base_risk * 0.8
        
        return base_risk
    
    def run_backtest(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Run enhanced backtest with confluence scoring"""
        print(f"\n🚀 BTCUSDT ENHANCED MULTI-CONFLUENCE STRATEGY BACKTEST")
        print("=" * 70)
        print(f"🎯 Target: Improved success rate with maintained profit potential")
        
        # Fetch data
        df = self.data_fetcher.fetch_btc_data(start_date, end_date, "1h")
        if df is None or df.empty:
            print("❌ Failed to fetch data")
            return None
        
        # Calculate indicators
        print("🔧 Calculating technical indicators...")
        df = self.calculate_technical_indicators(df)
        
        # Reset state
        self._reset_backtest_state()
        
        print(f"📈 Running enhanced simulation on {len(df)} periods...")
        
        # Process each bar
        for i in range(100, len(df)):  # Start from 100 for indicator stability
            self._process_bar(df, i)
            
            # Check for challenge completion
            if self._check_challenge_completion():
                break
        
        # Final position closure
        if self.current_position != 0:
            final_price = df.iloc[-1]['Close']
            final_time = df.index[-1]
            self._close_position(final_price, final_time, "Backtest End")
        
        return df
    
    def _reset_backtest_state(self):
        """Reset all state variables for new backtest"""
        self.current_balance = self.initial_balance
        self.trades = []
        self.daily_pnl = []
        self.equity_curve = []
        self.current_position = 0
        self.current_entry_price = 0
        self.trading_days = set()
        self.challenge_complete = False
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.risk_alerts = []
        self.emergency_stop = False
        self.daily_emergency_stop = False
        self.current_hour_trades = 0
        self.current_hour = None
        self.confluence_scores = []
        self.trades_skipped_filters = {
            'no_trend': 0, 'low_volume': 0, 'low_volatility': 0,
            'weak_confluence': 0, 'pattern_rejection': 0
        }
    
    def _process_bar(self, df: pd.DataFrame, idx: int):
        """Process individual bar in backtest"""
        current_time = df.index[idx]
        current_data = df.iloc[idx]
        current_price = current_data['Close']
        current_atr = current_data.get('atr', current_price * 0.02)
        current_date = current_time.date()
        current_hour = current_time.hour
        
        # Update daily tracking
        self._update_daily_tracking(current_date)
        
        # Skip if emergency stops active
        if self.emergency_stop or self.daily_emergency_stop:
            if self.current_position != 0:
                self._close_position(current_price, current_time, "Emergency Stop")
            return
        
        # Process existing position
        if self.current_position != 0:
            self._process_existing_position(current_price, current_time, current_atr)
        
        # Look for new entries
        if self.current_position == 0:
            can_enter, multiplier, reason, confluence_details = self.check_entry_conditions(df, idx)
            
            if can_enter:
                confluence_score = confluence_details['final_score']
                signal_direction = confluence_details['signal_direction']
                
                position_size, stop_distance, risk_pct, position_value = self.calculate_position_size(
                    confluence_score, current_price, current_atr, multiplier
                )
                
                if position_size > 0:
                    self._enter_position(signal_direction, current_price, position_size, 
                                       stop_distance, risk_pct, current_time, confluence_details)
                    self.current_hour_trades += 1
                    self.confluence_scores.append(confluence_score)
    
    def _update_daily_tracking(self, current_date):
        """Update daily tracking variables"""
        if current_date != self.current_date:
            self.current_date = current_date
            self.daily_starting_balance = self.current_balance
            self.daily_emergency_stop = False
            self.can_trade_today = True
            
            # Check if we traded today
            today_trades = [t for t in self.trades if t.get('date') == current_date]
            if today_trades or self.current_position != 0:
                self.trading_days.add(current_date)
    
    def _process_existing_position(self, current_price: float, timestamp, atr: float):
        """Process existing position for stops and targets"""
        if self.current_position == 0:
            return
        
        # Calculate unrealized P&L
        if self.current_position > 0:  # Long
            pnl = (current_price - self.current_entry_price) * abs(self.current_position)
            stop_hit = current_price <= self._get_stop_price()
        else:  # Short
            pnl = (self.current_entry_price - current_price) * abs(self.current_position)
            stop_hit = current_price >= self._get_stop_price()
        
        # Check stop loss
        if stop_hit:
            self._close_position(current_price, timestamp, "Stop Loss")
            return
        
        # Update trailing stop for profitable positions
        if pnl > 0:
            self._update_trailing_stop(current_price, atr)
        
        # Take profit at 2.5:1 risk-reward
        profit_target = self._calculate_profit_target()
        
        take_profit_hit = (
            (self.current_position > 0 and current_price >= profit_target) or
            (self.current_position < 0 and current_price <= profit_target)
        )
        
        if take_profit_hit:
            self._close_position(current_price, timestamp, "Take Profit")
    
    def _enter_position(self, direction: str, entry_price: float, position_size: float,
                       stop_distance: float, risk_pct: float, timestamp, confluence_details: Dict):
        """Enter new position with enhanced tracking"""
        direction_multiplier = 1 if direction == 'LONG' else -1
        stop_price = entry_price - (stop_distance * direction_multiplier)
        
        self.current_position = position_size * direction_multiplier
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
            'confluence_score': confluence_details['final_score'],
            'confluence_details': confluence_details
        }
        
        self.trades.append(trade_record)
    
    def _close_position(self, exit_price: float, timestamp, reason: str):
        """Close position with enhanced tracking"""
        if self.current_position == 0:
            return
        
        # Calculate P&L
        if self.current_position > 0:
            pnl = (exit_price - self.current_entry_price) * abs(self.current_position)
        else:
            pnl = (self.current_entry_price - exit_price) * abs(self.current_position)
        
        # Update balance and streaks
        self.current_balance += pnl
        pnl_pct = pnl / self.initial_balance * 100
        
        if pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            result = "WIN"
        else:
            self.consecutive_wins = 0
            self.consecutive_losses += 1
            result = "LOSS"
            
            # Risk alert for significant losses
            if abs(pnl_pct) > 0.8:
                self.risk_alerts.append(f"Large loss: {pnl_pct:.2f}%")
        
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
        
        # Clear position
        self.current_position = 0
        self.current_entry_price = 0
        if hasattr(self, 'trailing_stop_price'):
            delattr(self, 'trailing_stop_price')
    
    def _get_stop_price(self) -> float:
        """Get current stop price (original or trailing)"""
        if hasattr(self, 'trailing_stop_price'):
            return self.trailing_stop_price
        
        # Get original stop from last trade
        for trade in reversed(self.trades):
            if trade['action'] == 'OPEN':
                return trade['stop_price']
        
        return self.current_entry_price
    
    def _calculate_profit_target(self) -> float:
        """Calculate profit target based on risk-reward ratio"""
        stop_distance = abs(self.current_entry_price - self._get_stop_price())
        
        if self.current_position > 0:
            return self.current_entry_price + (2.5 * stop_distance)
        else:
            return self.current_entry_price - (2.5 * stop_distance)
    
    def _update_trailing_stop(self, current_price: float, atr: float):
        """Update trailing stop loss"""
        if not hasattr(self, 'trailing_stop_price'):
            self.trailing_stop_price = self._get_stop_price()
        
        trail_distance = atr * 1.2
        
        if self.current_position > 0:  # Long
            new_stop = current_price - trail_distance
            if new_stop > self.trailing_stop_price:
                self.trailing_stop_price = new_stop
        else:  # Short
            new_stop = current_price + trail_distance
            if new_stop < self.trailing_stop_price:
                self.trailing_stop_price = new_stop
    
    def _check_challenge_completion(self) -> bool:
        """Check if profit target reached"""
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        if profit_pct >= self.profit_target_pct and len(self.trading_days) >= self.min_trading_days:
            self.challenge_complete = True
            print(f"🎉 TARGET ACHIEVED! {profit_pct:.2f}% profit in {len(self.trading_days)} days!")
            return True
        
        return False
    
    def print_results(self):
        """Print comprehensive backtest results"""
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        print(f"\n🏆 BTCUSDT ENHANCED MULTI-CONFLUENCE STRATEGY RESULTS")
        print("=" * 80)
        print(f"Initial Balance:        ${self.initial_balance:,.2f}")
        print(f"Final Balance:          ${self.current_balance:,.2f}")
        print(f"Profit/Loss:            {profit_pct:+.2f}%")
        print(f"Profit Target:          {self.profit_target_pct}%")
        
        # Calculate performance metrics
        closed_trades = [t for t in self.trades if t['action'] == 'CLOSE']
        
        if closed_trades:
            profitable_trades = [t for t in closed_trades if t['pnl'] > 0]
            win_rate = len(profitable_trades) / len(closed_trades) * 100
            
            print(f"\n📊 ENHANCED PERFORMANCE:")
            print(f"Trading Days:           {len(self.trading_days)}")
            print(f"Total Trades:           {len(closed_trades)}")
            print(f"Win Rate:               {win_rate:.1f}%")
            
            if profitable_trades:
                avg_win = sum(t['pnl'] for t in profitable_trades) / len(profitable_trades)
                max_win = max(t['pnl'] for t in profitable_trades)
                print(f"Average Win:            ${avg_win:.2f}")
                print(f"Largest Win:            ${max_win:.2f}")
            
            losing_trades = [t for t in closed_trades if t['pnl'] < 0]
            if losing_trades:
                avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
                max_loss = min(t['pnl'] for t in losing_trades)
                print(f"Average Loss:           ${avg_loss:.2f}")
                print(f"Largest Loss:           ${max_loss:.2f}")
        
        # Confluence analysis
        if self.confluence_scores:
            avg_confluence = sum(self.confluence_scores) / len(self.confluence_scores)
            print(f"\n📊 CONFLUENCE ANALYSIS:")
            print(f"Average Confluence Score: {avg_confluence:.2f}/7")
            print(f"High Confluence Trades:   {len([s for s in self.confluence_scores if s >= 5])}")
        
        # Filter effectiveness
        total_filtered = sum(self.trades_skipped_filters.values())
        print(f"\n🔍 FILTER EFFECTIVENESS:")
        for filter_name, count in self.trades_skipped_filters.items():
            print(f"{filter_name.replace('_', ' ').title()}: {count}")
        print(f"Total Filtered:         {total_filtered}")
        
        # Challenge status
        print(f"\n🎯 CHALLENGE STATUS:")
        if self.challenge_complete:
            print(f"✅ COMPLETED - Target reached in {len(self.trading_days)} days!")
        else:
            progress = (profit_pct / self.profit_target_pct) * 100 if self.profit_target_pct else 0
            print(f"⚠️ IN PROGRESS - {profit_pct:.2f}% / {self.profit_target_pct}% ({progress:.0f}%)")


if __name__ == "__main__":
    print("🧪 Testing BTCUSDT Enhanced Multi-Confluence Strategy")
    print("=" * 60)
    
    # Test moderate risk profile
    strategy = BTCUSDTEnhancedStrategy(account_size=10000, risk_profile='moderate')
    
    # Run backtest on recent period
    df = strategy.run_backtest("2024-01-01", "2024-03-01")
    
    if df is not None:
        strategy.print_results()
        print(f"\n✅ Enhanced strategy test completed!")
    else:
        print("❌ Enhanced strategy test failed")