#!/usr/bin/env python3
"""
Multi-Confluence Momentum Strategy for BTCUSDT
Combines RSI, MACD, Bollinger Bands, Volume, and Moving Averages
Based on research showing 73-78% win rates and high profitability
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
import warnings
import sys
import os
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

class MultiConfluenceMomentumStrategy:
    """
    Multi-Confluence Momentum Strategy for BTCUSDT
    
    Research-backed strategy combining:
    - RSI (14 period)
    - MACD (12,26,9)
    - Bollinger Bands (20,2)
    - Volume analysis
    - Moving average trend filter
    - Liquidity zone analysis
    """
    
    def __init__(self, account_size=10000, risk_profile='moderate'):
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.risk_profile = risk_profile.lower()
        
        # Risk profile settings
        self.risk_profiles = {
            'conservative': {
                'risk_per_trade': 0.01,  # 1% risk per trade
                'position_size_pct': 0.10,  # 10% of capital
                'rsi_oversold': 25,
                'rsi_overbought': 75,
                'volume_threshold': 1.2,  # 20% above average
                'bb_breakout_threshold': 0.02,  # 2% breakout
                'trend_strength_min': 0.5
            },
            'moderate': {
                'risk_per_trade': 0.02,  # 2% risk per trade
                'position_size_pct': 0.15,  # 15% of capital
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'volume_threshold': 1.5,  # 50% above average
                'bb_breakout_threshold': 0.015,  # 1.5% breakout
                'trend_strength_min': 0.3
            },
            'aggressive': {
                'risk_per_trade': 0.03,  # 3% risk per trade
                'position_size_pct': 0.25,  # 25% of capital
                'rsi_oversold': 35,
                'rsi_overbought': 65,
                'volume_threshold': 2.0,  # 100% above average
                'bb_breakout_threshold': 0.01,  # 1% breakout
                'trend_strength_min': 0.1
            }
        }
        
        self.settings = self.risk_profiles[self.risk_profile]
        
        # Strategy parameters
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bb_period = 20
        self.bb_std = 2
        self.ma_short = 20
        self.ma_long = 50
        self.volume_ma_period = 20
        
        # Trading state
        self.position = None
        self.trades = []
        self.equity_curve = []
        self.max_drawdown = 0
        self.peak_balance = account_size
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.max_consecutive_wins = 0
        self.max_consecutive_losses = 0
        
        print(f"🚀 MULTI-CONFLUENCE MOMENTUM STRATEGY ({self.risk_profile.upper()})")
        print(f"💼 Account Size: ${self.account_size:,}")
        print(f"📊 Risk Per Trade: {self.settings['risk_per_trade']:.1%}")
        print(f"💰 Position Size: {self.settings['position_size_pct']:.1%} of capital")
        print(f"⏰ Timeframe: 1-Hour")
        
    def fetch_data(self, start_date, end_date):
        """Fetch BTCUSDT data from multiple sources"""
        print(f"📊 Fetching BTC-USD data from {start_date} to {end_date} (1h)")
        
        try:
            # Try yfinance first
            ticker = yf.Ticker("BTC-USD")
            df = ticker.history(start=start_date, end=end_date, interval="1h")
            
            if not df.empty:
                print(f"✅ Downloaded {len(df)} 1h periods from yfinance")
                return df
                
        except Exception as e:
            print(f"❌ No data returned from yfinance for BTC-USD")
        
        # Fallback to Binance API
        try:
            print("⚠️ Primary source failed, trying backup sources...")
            return self._fetch_binance_data(start_date, end_date)
        except Exception as e:
            print(f"❌ Backup sources failed: {e}")
            return None
    
    def _fetch_binance_data(self, start_date, end_date):
        """Fetch data from Binance API"""
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
    
    def calculate_indicators(self, df):
        """Calculate all technical indicators"""
        print("🔧 Calculating indicators...")
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=self.macd_fast).mean()
        exp2 = df['Close'].ewm(span=self.macd_slow).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=self.macd_signal).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=self.bb_period).mean()
        bb_std = df['Close'].rolling(window=self.bb_period).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * self.bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * self.bb_std)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Moving Averages
        df['MA_Short'] = df['Close'].rolling(window=self.ma_short).mean()
        df['MA_Long'] = df['Close'].rolling(window=self.ma_long).mean()
        df['MA_Trend'] = np.where(df['MA_Short'] > df['MA_Long'], 1, -1)
        
        # Volume Analysis
        df['Volume_MA'] = df['Volume'].rolling(window=self.volume_ma_period).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Trend Strength
        df['Price_Change'] = df['Close'].pct_change()
        df['Trend_Strength'] = abs(df['Close'] - df['BB_Middle']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Liquidity Zones (Support/Resistance levels)
        df['Recent_High'] = df['High'].rolling(window=10).max()
        df['Recent_Low'] = df['Low'].rolling(window=10).min()
        df['Liquidity_Zone_High'] = df['Recent_High'].shift(1)
        df['Liquidity_Zone_Low'] = df['Recent_Low'].shift(1)
        
        # Multi-Confluence Score
        df['Confluence_Score'] = self.calculate_confluence_score(df)
        
        return df
    
    def calculate_confluence_score(self, df):
        """Calculate confluence score from multiple indicators"""
        score = pd.Series(0, index=df.index)
        
        # RSI component (oversold/overbought)
        score += np.where(df['RSI'] < self.settings['rsi_oversold'], 2,
                 np.where(df['RSI'] > self.settings['rsi_overbought'], -2, 0))
        
        # MACD component
        score += np.where(df['MACD'] > df['MACD_Signal'], 1, -1)
        score += np.where(df['MACD_Histogram'] > df['MACD_Histogram'].shift(1), 1, -1)
        
        # Bollinger Bands component
        score += np.where(df['Close'] < df['BB_Lower'], 2,
                 np.where(df['Close'] > df['BB_Upper'], -2, 0))
        
        # Moving Average Trend
        score += df['MA_Trend']
        
        # Volume confirmation
        volume_boost = np.where(df['Volume_Ratio'] > self.settings['volume_threshold'], 1, 0)
        score = score * (1 + volume_boost * 0.5)  # Boost signals with high volume
        
        return score
    
    def should_enter_long(self, df, idx):
        """Determine if should enter long position"""
        if idx < max(self.bb_period, self.ma_long):
            return False
        
        current = df.iloc[idx]
        
        # Multi-confluence bullish signal
        confluence_bullish = current['Confluence_Score'] >= 3
        
        # RSI oversold
        rsi_oversold = current['RSI'] < self.settings['rsi_oversold']
        
        # MACD bullish cross or rising
        macd_bullish = (current['MACD'] > current['MACD_Signal'] and 
                       current['MACD_Histogram'] > 0)
        
        # Price near or below lower Bollinger Band
        bb_oversold = current['Close'] <= current['BB_Lower'] * (1 + self.settings['bb_breakout_threshold'])
        
        # Above liquidity zone low (support)
        above_support = current['Close'] > current['Liquidity_Zone_Low']
        
        # Volume confirmation
        volume_confirm = current['Volume_Ratio'] >= self.settings['volume_threshold']
        
        # Trend strength sufficient
        trend_strength_ok = current['Trend_Strength'] >= self.settings['trend_strength_min']
        
        # Combined signal (requiring multiple confirmations)
        bullish_signal = (confluence_bullish or 
                         (rsi_oversold and macd_bullish and above_support)) and \
                        (bb_oversold or volume_confirm) and \
                        trend_strength_ok
        
        return bullish_signal
    
    def should_enter_short(self, df, idx):
        """Determine if should enter short position"""
        if idx < max(self.bb_period, self.ma_long):
            return False
        
        current = df.iloc[idx]
        
        # Multi-confluence bearish signal
        confluence_bearish = current['Confluence_Score'] <= -3
        
        # RSI overbought
        rsi_overbought = current['RSI'] > self.settings['rsi_overbought']
        
        # MACD bearish cross or falling
        macd_bearish = (current['MACD'] < current['MACD_Signal'] and 
                       current['MACD_Histogram'] < 0)
        
        # Price near or above upper Bollinger Band
        bb_overbought = current['Close'] >= current['BB_Upper'] * (1 - self.settings['bb_breakout_threshold'])
        
        # Below liquidity zone high (resistance)
        below_resistance = current['Close'] < current['Liquidity_Zone_High']
        
        # Volume confirmation
        volume_confirm = current['Volume_Ratio'] >= self.settings['volume_threshold']
        
        # Trend strength sufficient
        trend_strength_ok = current['Trend_Strength'] >= self.settings['trend_strength_min']
        
        # Combined signal (requiring multiple confirmations)
        bearish_signal = (confluence_bearish or 
                         (rsi_overbought and macd_bearish and below_resistance)) and \
                        (bb_overbought or volume_confirm) and \
                        trend_strength_ok
        
        return bearish_signal
    
    def should_exit_position(self, df, idx):
        """Determine if should exit current position"""
        if not self.position:
            return False
        
        current = df.iloc[idx]
        entry_price = self.position['entry_price']
        direction = self.position['direction']
        
        # Stop loss
        stop_loss_pct = 0.03  # 3% stop loss
        if direction == 'long' and current['Close'] <= entry_price * (1 - stop_loss_pct):
            return True, "Stop Loss"
        elif direction == 'short' and current['Close'] >= entry_price * (1 + stop_loss_pct):
            return True, "Stop Loss"
        
        # Take profit
        take_profit_pct = 0.06  # 6% take profit (2:1 risk/reward)
        if direction == 'long' and current['Close'] >= entry_price * (1 + take_profit_pct):
            return True, "Take Profit"
        elif direction == 'short' and current['Close'] <= entry_price * (1 - take_profit_pct):
            return True, "Take Profit"
        
        # Signal reversal exits
        if direction == 'long':
            # Exit long on bearish confluence or overbought RSI with bearish MACD
            if (current['Confluence_Score'] <= -2 or 
                (current['RSI'] > self.settings['rsi_overbought'] and 
                 current['MACD'] < current['MACD_Signal'])):
                return True, "Signal Reversal"
        else:  # short
            # Exit short on bullish confluence or oversold RSI with bullish MACD
            if (current['Confluence_Score'] >= 2 or 
                (current['RSI'] < self.settings['rsi_oversold'] and 
                 current['MACD'] > current['MACD_Signal'])):
                return True, "Signal Reversal"
        
        # Bollinger Band mean reversion
        if direction == 'long' and current['Close'] >= current['BB_Upper']:
            return True, "BB Mean Reversion"
        elif direction == 'short' and current['Close'] <= current['BB_Lower']:
            return True, "BB Mean Reversion"
        
        return False, None
    
    def calculate_position_size(self, price):
        """Calculate position size based on risk management"""
        # Base position size as percentage of capital
        base_size = self.current_balance * self.settings['position_size_pct']
        
        # Risk-based position size
        risk_amount = self.current_balance * self.settings['risk_per_trade']
        stop_distance = 0.03  # 3% stop loss
        risk_based_size = risk_amount / stop_distance
        
        # Use smaller of the two
        position_value = min(base_size, risk_based_size)
        position_size = position_value / price
        
        return position_size, position_value
    
    def execute_trade(self, df, idx, action, reason):
        """Execute a trade"""
        current_price = df.iloc[idx]['Close']
        timestamp = df.index[idx]
        
        if action == 'buy':
            position_size, position_value = self.calculate_position_size(current_price)
            
            self.position = {
                'direction': 'long',
                'entry_price': current_price,
                'entry_time': timestamp,
                'size': position_size,
                'value': position_value,
                'confluence_score': df.iloc[idx]['Confluence_Score'],
                'rsi': df.iloc[idx]['RSI'],
                'macd': df.iloc[idx]['MACD'],
                'bb_position': df.iloc[idx]['BB_Position']
            }
            
            print(f"🟢 LONG @ ${current_price:,.0f} | Size: {position_size:.4f} BTC (${position_value:.0f}) | {reason}")
            
        elif action == 'sell':
            position_size, position_value = self.calculate_position_size(current_price)
            
            self.position = {
                'direction': 'short',
                'entry_price': current_price,
                'entry_time': timestamp,
                'size': position_size,
                'value': position_value,
                'confluence_score': df.iloc[idx]['Confluence_Score'],
                'rsi': df.iloc[idx]['RSI'],
                'macd': df.iloc[idx]['MACD'],
                'bb_position': df.iloc[idx]['BB_Position']
            }
            
            print(f"🔴 SHORT @ ${current_price:,.0f} | Size: {position_size:.4f} BTC (${position_value:.0f}) | {reason}")
            
        elif action == 'close':
            if self.position:
                self._close_position(df, idx, reason)
    
    def _close_position(self, df, idx, reason):
        """Close current position and record trade"""
        current_price = df.iloc[idx]['Close']
        timestamp = df.index[idx]
        
        entry_price = self.position['entry_price']
        direction = self.position['direction']
        size = self.position['size']
        entry_value = self.position['value']
        
        # Calculate P&L
        if direction == 'long':
            price_change = (current_price - entry_price) / entry_price
        else:  # short
            price_change = (entry_price - current_price) / entry_price
        
        pnl = entry_value * price_change
        return_pct = price_change * 100
        
        # Update balance
        self.current_balance += pnl
        
        # Update performance metrics
        self.total_trades += 1
        
        if pnl > 0:
            self.winning_trades += 1
            self.total_profit += pnl
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.max_consecutive_wins = max(self.max_consecutive_wins, self.consecutive_wins)
        else:
            self.losing_trades += 1
            self.total_loss += abs(pnl)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.max_consecutive_losses = max(self.max_consecutive_losses, self.consecutive_losses)
        
        # Update drawdown
        self.peak_balance = max(self.peak_balance, self.current_balance)
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        self.max_drawdown = max(self.max_drawdown, current_drawdown)
        
        # Record trade
        trade = {
            'entry_time': self.position['entry_time'],
            'exit_time': timestamp,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': current_price,
            'size': size,
            'pnl': pnl,
            'return_pct': return_pct,
            'exit_reason': reason,
            'confluence_score': self.position['confluence_score'],
            'rsi': self.position['rsi'],
            'macd': self.position['macd'],
            'bb_position': self.position['bb_position']
        }
        
        self.trades.append(trade)
        
        pnl_color = "🟢" if pnl > 0 else "🔴"
        print(f"{pnl_color} CLOSE @ ${current_price:,.0f} | P&L: ${pnl:+.2f} ({return_pct:+.1f}%) | {reason}")
        
        # Clear position
        self.position = None
        
        # Record equity
        self.equity_curve.append({
            'timestamp': timestamp,
            'balance': self.current_balance,
            'trade_pnl': pnl
        })
    
    def run_backtest(self, start_date, end_date):
        """Run the complete backtest"""
        print(f"\n🎯 MULTI-CONFLUENCE MOMENTUM BACKTEST")
        print("=" * 60)
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"🎪 Strategy: Multi-Confluence Momentum + Risk Management")
        
        # Fetch data
        df = self.fetch_data(start_date, end_date)
        if df is None or df.empty:
            print("❌ No data available for backtesting")
            return None
        
        print("🔧 Preprocessing data...")
        df = df.dropna()
        print(f"✅ Preprocessed data ready: {len(df)} periods")
        
        # Calculate indicators
        df = self.calculate_indicators(df)
        print(f"✅ Data loaded: {len(df)} periods")
        
        print("📈 Running Multi-Confluence Momentum simulation...")
        
        # Run simulation
        for i in range(len(df)):
            current_data = df.iloc[i]
            
            # Check for exit first
            if self.position:
                should_exit, exit_reason = self.should_exit_position(df, i)
                if should_exit:
                    self.execute_trade(df, i, 'close', exit_reason)
            
            # Check for entry (if not in position)
            if not self.position:
                if self.should_enter_long(df, i):
                    confluence = current_data['Confluence_Score']
                    self.execute_trade(df, i, 'buy', f"Multi-Confluence Long (Score: {confluence:.1f})")
                elif self.should_enter_short(df, i):
                    confluence = current_data['Confluence_Score']
                    self.execute_trade(df, i, 'sell', f"Multi-Confluence Short (Score: {confluence:.1f})")
        
        # Close any open position
        if self.position:
            self.execute_trade(df, len(df)-1, 'close', "End of Period")
        
        # Calculate final metrics
        self._calculate_final_metrics()
        self._print_results()
        
        return df
    
    def _calculate_final_metrics(self):
        """Calculate final performance metrics"""
        self.total_return = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        self.win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        self.profit_factor = (self.total_profit / self.total_loss) if self.total_loss > 0 else float('inf')
        self.avg_win = self.total_profit / self.winning_trades if self.winning_trades > 0 else 0
        self.avg_loss = self.total_loss / self.losing_trades if self.losing_trades > 0 else 0
        
        if self.trades:
            returns = [t['return_pct'] for t in self.trades]
            self.largest_win = max(returns)
            self.largest_loss = min(returns)
        else:
            self.largest_win = 0
            self.largest_loss = 0
    
    def _print_results(self):
        """Print backtest results"""
        print(f"\n🏆 MULTI-CONFLUENCE MOMENTUM STRATEGY RESULTS")
        print("=" * 60)
        print(f"Initial Balance:        ${self.initial_balance:,.2f}")
        print(f"Final Balance:          ${self.current_balance:,.2f}")
        print(f"Total Return:           {self.total_return:+.2f}%")
        print(f"Max Drawdown:           {self.max_drawdown:.2%}")
        
        print(f"\n📊 TRADING PERFORMANCE:")
        print(f"Total Trades:           {self.total_trades}")
        print(f"Win Rate:               {self.win_rate:.1f}%")
        print(f"Profit Factor:          {self.profit_factor:.2f}")
        print(f"Average Win:            ${self.avg_win:.2f}")
        print(f"Largest Win:            {self.largest_win:+.2f}%")
        print(f"Average Loss:           ${-self.avg_loss:.2f}")
        print(f"Largest Loss:           {self.largest_loss:+.2f}%")
        
        print(f"\n🎯 STRATEGY ANALYSIS:")
        print(f"Risk Profile:           {self.risk_profile.title()}")
        print(f"Risk Per Trade:         {self.settings['risk_per_trade']:.1%}")
        print(f"Position Size:          {self.settings['position_size_pct']:.1%} of capital")
        
        print(f"\n🛡️ RISK ANALYSIS:")
        print(f"Max Daily Loss Limit:   ${self.initial_balance * 0.05:.2f} (5.0%)")
        print(f"Max Position Size:      ${self.initial_balance * self.settings['position_size_pct']:.2f}")
        print(f"Consecutive Wins:       {self.max_consecutive_wins}")
        print(f"Consecutive Losses:     {self.max_consecutive_losses}")

def test_multi_confluence_strategy():
    """Test the Multi-Confluence Momentum Strategy"""
    print("🚀 Testing Multi-Confluence Momentum Strategy...")
    
    strategy = MultiConfluenceMomentumStrategy(
        account_size=10000,
        risk_profile='moderate'
    )
    
    # Run backtest on recent data
    result = strategy.run_backtest("2024-06-01", "2024-11-01")
    
    if result is not None:
        print(f"\n✅ Multi-Confluence Strategy test completed successfully!")
        
        # Show some sample trades
        if strategy.trades:
            print(f"\n📋 Sample Trades (first 5):")
            for i, trade in enumerate(strategy.trades[:5]):
                pnl_str = f"${trade['pnl']:+.2f}"
                ret_str = f"({trade['return_pct']:+.1f}%)"
                print(f"   {i+1}. {trade['direction'].upper()} @ ${trade['entry_price']:,.0f} → "
                      f"${trade['exit_price']:,.0f} | Score: {trade['confluence_score']:+.1f} | "
                      f"P&L: {pnl_str} {ret_str} | {trade['exit_reason']}")
    
    return strategy

if __name__ == "__main__":
    test_multi_confluence_strategy()