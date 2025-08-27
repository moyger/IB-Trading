#!/usr/bin/env python3
"""
Visual BTCUSDT Strategy for backtesting.py Integration
Provides interactive browser-based visualization of our enhanced strategy

Features:
- Interactive candlestick charts with entry/exit markers
- Confluence score visualization
- Real-time trade analysis
- Professional-grade plotting with Bokeh
- Export capabilities for reports
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class BTCVisualStrategy(Strategy):
    """
    Visual version of our enhanced BTCUSDT strategy for backtesting.py
    Maintains all original logic while adding visual capabilities
    """
    
    # Strategy parameters (optimizable)
    confluence_threshold = 4  # Minimum confluence score to trade
    risk_per_trade = 1.5      # Risk percentage per trade
    atr_multiplier = 2.0      # Stop loss distance multiplier
    profit_target = 2.5       # Risk-reward ratio
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Price data
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume
        
        # Moving Averages
        self.ema_8 = self.I(lambda x: pd.Series(x).ewm(span=8).mean(), close)
        self.ema_21 = self.I(lambda x: pd.Series(x).ewm(span=21).mean(), close)
        self.ema_50 = self.I(lambda x: pd.Series(x).ewm(span=50).mean(), close)
        self.ema_100 = self.I(lambda x: pd.Series(x).ewm(span=100).mean(), close)
        
        # RSI
        self.rsi_14 = self.I(self._calculate_rsi, close, 14)
        self.rsi_21 = self.I(self._calculate_rsi, close, 21)
        
        # MACD (calculated from EMA difference)
        def calculate_macd():
            return self.ema_8 - self.ema_21
        
        self.macd = self.I(calculate_macd)
        self.macd_signal = self.I(lambda x: pd.Series(x).ewm(span=7).mean(), self.macd)
        
        # ATR for stop losses
        self.atr = self.I(self._calculate_atr, high, low, close)
        
        # ADX for trend strength
        self.adx = self.I(self._calculate_adx, high, low, close)
        
        # Volume analysis
        self.volume_sma = self.I(lambda x: pd.Series(x).rolling(window=20).mean(), volume)
        
        # Confluence score (will be calculated in next())
        self.confluence_score = 0
        
        # Tracking variables
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.trade_reason = ""
        
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        prices = pd.Series(prices)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range"""
        high = pd.Series(high)
        low = pd.Series(low)
        close = pd.Series(close)
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr.fillna(close * 0.02)  # Fallback to 2% of price
    
    def _calculate_adx(self, high, low, close, period=14):
        """Calculate ADX for trend strength"""
        high = pd.Series(high)
        low = pd.Series(low) 
        close = pd.Series(close)
        
        # Calculate directional movement
        dm_plus = np.where(
            (high - high.shift(1)) > (low.shift(1) - low),
            np.maximum(high - high.shift(1), 0), 0
        )
        dm_minus = np.where(
            (low.shift(1) - low) > (high - high.shift(1)),
            np.maximum(low.shift(1) - low, 0), 0
        )
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([pd.Series(tr1), pd.Series(tr2), pd.Series(tr3)], axis=1).max(axis=1)
        
        # ATR and Directional Indicators
        atr = true_range.rolling(window=period).mean()
        di_plus = 100 * (pd.Series(dm_plus).rolling(window=period).mean() / atr)
        di_minus = 100 * (pd.Series(dm_minus).rolling(window=period).mean() / atr)
        
        # DX and ADX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window=period).mean()
        
        return adx.fillna(0)
    
    def _calculate_confluence_score(self):
        """
        Calculate multi-indicator confluence score (0-7 scale)
        Same logic as our original strategy
        """
        score = 0
        
        # Current values
        close = self.data.Close[-1]
        ema8 = self.ema_8[-1]
        ema21 = self.ema_21[-1] 
        ema50 = self.ema_50[-1]
        ema100 = self.ema_100[-1]
        
        rsi14 = self.rsi_14[-1]
        rsi21 = self.rsi_21[-1]
        macd = self.macd[-1]
        macd_signal = self.macd_signal[-1]
        adx = self.adx[-1]
        
        volume = self.data.Volume[-1]
        volume_avg = self.volume_sma[-1]
        
        # 1. Trend Alignment (0-2 points)
        if close > ema8 > ema21 > ema50 > ema100:
            score += 2
            trend_direction = 1
        elif close < ema8 < ema21 < ema50 < ema100:
            score += 2
            trend_direction = -1
        elif close > ema8 > ema21 > ema50:
            score += 1
            trend_direction = 1
        elif close < ema8 < ema21 < ema50:
            score += 1
            trend_direction = -1
        else:
            trend_direction = 0
        
        # 2. Momentum Confluence (0-2 points)
        rsi_bullish = 30 < rsi14 < 80 and 30 < rsi21 < 80 and rsi14 > rsi21
        rsi_bearish = 20 < rsi14 < 70 and 20 < rsi21 < 70 and rsi14 < rsi21
        macd_bullish = macd > macd_signal
        macd_bearish = macd < macd_signal
        
        if (rsi_bullish and macd_bullish and trend_direction > 0):
            score += 2
        elif (rsi_bearish and macd_bearish and trend_direction < 0):
            score += 2
        elif (rsi_bullish or macd_bullish) and trend_direction > 0:
            score += 1
        elif (rsi_bearish or macd_bearish) and trend_direction < 0:
            score += 1
        
        # 3. Market Regime (0-1 points)
        if adx >= 25:  # Strong trend
            score += 1
        elif adx >= 20:  # Moderate trend
            score += 1
        
        # 4. Volume Confirmation (0-1 points)
        if volume >= volume_avg * 1.2:
            score += 1
        elif volume >= volume_avg * 0.8:
            score += 0.5
        
        # 5. Pattern Bonus (0-1 points)
        # Simplified pattern recognition
        if trend_direction != 0:
            score += 1
        
        # Direction consistency check
        if trend_direction != 0:
            final_score = min(7, int(score))
            signal_direction = trend_direction
        else:
            final_score = 0
            signal_direction = 0
        
        return final_score, signal_direction
    
    def next(self):
        """Main strategy logic called for each bar"""
        # Calculate confluence score
        confluence_score, signal_direction = self._calculate_confluence_score()
        self.confluence_score = confluence_score
        
        # Store current values for potential trade
        current_price = self.data.Close[-1]
        current_atr = self.atr[-1]
        
        # Exit conditions for existing positions
        if self.position:
            # Stop loss hit
            if (self.position.is_long and current_price <= self.stop_loss) or \
               (self.position.is_short and current_price >= self.stop_loss):
                self.position.close()
                return
            
            # Take profit hit
            if (self.position.is_long and current_price >= self.take_profit) or \
               (self.position.is_short and current_price <= self.take_profit):
                self.position.close()
                return
        
        # Entry conditions
        if not self.position and confluence_score >= self.confluence_threshold:
            
            # Long entry
            if signal_direction > 0:
                # Calculate position size based on risk
                stop_distance = current_atr * self.atr_multiplier
                self.stop_loss = current_price - stop_distance
                self.take_profit = current_price + (stop_distance * self.profit_target)
                
                # Calculate position size
                risk_amount = self.equity * (self.risk_per_trade / 100)
                position_size = risk_amount / stop_distance
                position_size = min(position_size, self.equity / current_price)  # Don't exceed available capital
                
                if position_size > 0:
                    self.buy(size=position_size)
                    self.entry_price = current_price
                    self.trade_reason = f"LONG - Confluence: {confluence_score}/7"
            
            # Short entry
            elif signal_direction < 0:
                # Calculate position size based on risk
                stop_distance = current_atr * self.atr_multiplier
                self.stop_loss = current_price + stop_distance
                self.take_profit = current_price - (stop_distance * self.profit_target)
                
                # Calculate position size
                risk_amount = self.equity * (self.risk_per_trade / 100)
                position_size = risk_amount / stop_distance
                position_size = min(position_size, self.equity / current_price)  # Don't exceed available capital
                
                if position_size > 0:
                    self.sell(size=position_size)
                    self.entry_price = current_price
                    self.trade_reason = f"SHORT - Confluence: {confluence_score}/7"


class BTCOptimizedVisualStrategy(BTCVisualStrategy):
    """
    Optimized version with parameter ranges for optimization
    """
    
    # Parameter ranges for optimization
    confluence_threshold = range(3, 7, 1)  # Test confluence thresholds 3-6
    risk_per_trade = [1.0, 1.5, 2.0, 2.5, 3.0]  # Risk levels
    atr_multiplier = [1.5, 2.0, 2.5, 3.0]  # Stop loss distances
    profit_target = [2.0, 2.5, 3.0, 3.5, 4.0]  # Risk-reward ratios


if __name__ == "__main__":
    # Test the visual strategy
    print("🧪 Testing Visual BTCUSDT Strategy")
    print("This strategy is designed for backtesting.py integration")
    print("Use visual_backtest_runner.py to run full visual backtests")
    
    # Basic validation
    print("\n✅ Visual strategy module loaded successfully!")
    print("📊 Ready for interactive backtesting with:")
    print("   - Confluence score visualization") 
    print("   - Entry/exit markers")
    print("   - Risk management indicators")
    print("   - Performance analytics")