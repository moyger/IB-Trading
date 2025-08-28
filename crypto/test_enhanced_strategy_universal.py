#!/usr/bin/env python3
"""
Adapter to test the existing BTCUSDTEnhancedStrategy with the Universal Backtesting Engine
"""

import pandas as pd
import numpy as np
from universal_backtesting_engine import UniversalStrategy, UniversalBacktestEngine
from backtesting.lib import crossover

class BTCUSDTEnhancedAdapter(UniversalStrategy):
    """
    Adapter class to use the existing BTCUSDTEnhancedStrategy 
    with the Universal Backtesting Engine
    """
    
    # Strategy parameters (matching original strategy)
    risk_profile = 'moderate'  # 'conservative', 'moderate', 'aggressive'
    
    # Risk profiles from original strategy
    RISK_PROFILES = {
        'conservative': {
            'risk_per_trade': 0.01,
            'max_daily_loss': 0.03,
            'confluence_threshold': 5,
            'position_size': 0.10
        },
        'moderate': {
            'risk_per_trade': 0.02,
            'max_daily_loss': 0.05,
            'confluence_threshold': 4,
            'position_size': 0.15
        },
        'aggressive': {
            'risk_per_trade': 0.03,
            'max_daily_loss': 0.07,
            'confluence_threshold': 3,
            'position_size': 0.25
        }
    }
    
    def strategy_init(self):
        """Initialize the enhanced Bitcoin strategy indicators"""
        
        # Apply risk profile settings
        profile = self.RISK_PROFILES[self.risk_profile]
        self.risk_per_trade = profile['risk_per_trade']
        self.max_daily_loss = profile['max_daily_loss']
        self.confluence_threshold = profile['confluence_threshold']
        self.base_position_size = profile['position_size']
        
        # Calculate EMAs (matching original strategy)
        self.ema_8 = self.I(lambda x: pd.Series(x).ewm(span=8).mean(), self.data.Close)
        self.ema_21 = self.I(lambda x: pd.Series(x).ewm(span=21).mean(), self.data.Close)
        self.ema_50 = self.I(lambda x: pd.Series(x).ewm(span=50).mean(), self.data.Close)
        self.ema_100 = self.I(lambda x: pd.Series(x).ewm(span=100).mean(), self.data.Close)
        self.ema_200 = self.I(lambda x: pd.Series(x).ewm(span=200).mean(), self.data.Close)
        
        # Calculate RSI indicators
        close_series = pd.Series(self.data.Close)
        
        # RSI 14
        delta_14 = close_series.diff()
        gain_14 = (delta_14.where(delta_14 > 0, 0)).rolling(window=14).mean()
        loss_14 = (-delta_14.where(delta_14 < 0, 0)).rolling(window=14).mean()
        rs_14 = gain_14 / loss_14
        self.rsi_14 = self.I(lambda: 100 - (100 / (1 + rs_14)))
        
        # RSI 21
        delta_21 = close_series.diff()
        gain_21 = (delta_21.where(delta_21 > 0, 0)).rolling(window=21).mean()
        loss_21 = (-delta_21.where(delta_21 < 0, 0)).rolling(window=21).mean()
        rs_21 = gain_21 / loss_21
        self.rsi_21 = self.I(lambda: 100 - (100 / (1 + rs_21)))
        
        # MACD
        exp1 = close_series.ewm(span=12, adjust=False).mean()
        exp2 = close_series.ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        self.macd = self.I(lambda: macd_line)
        self.macd_signal = self.I(lambda: macd_line.ewm(span=9, adjust=False).mean())
        self.macd_histogram = self.I(lambda: macd_line - macd_line.ewm(span=9, adjust=False).mean())
        
        # ADX for trend strength
        high_series = pd.Series(self.data.High)
        low_series = pd.Series(self.data.Low)
        
        # Calculate +DM and -DM
        plus_dm = high_series.diff()
        minus_dm = -low_series.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # True Range
        tr = pd.concat([
            high_series - low_series,
            abs(high_series - close_series.shift()),
            abs(low_series - close_series.shift())
        ], axis=1).max(axis=1)
        
        # Smoothed values
        atr_14 = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr_14)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr_14)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        self.adx = self.I(lambda: dx.rolling(window=14).mean())
        
        # Volume analysis
        volume_series = pd.Series(self.data.Volume)
        self.volume_ma = self.I(lambda: volume_series.rolling(window=20).mean())
        self.volume_ratio = self.I(lambda: volume_series / volume_series.rolling(window=20).mean())
        
        # ATR for volatility
        self.atr = self.I(lambda: tr.rolling(window=14).mean())
        
        # Bollinger Bands
        self.bb_middle = self.I(lambda: close_series.rolling(window=20).mean())
        bb_std = close_series.rolling(window=20).std()
        self.bb_upper = self.I(lambda: self.bb_middle[-1] + (bb_std * 2))
        self.bb_lower = self.I(lambda: self.bb_middle[-1] - (bb_std * 2))
        
    def calculate_confluence_score(self) -> int:
        """
        Calculate multi-indicator confluence score
        Simplified version of the original strategy's scoring
        """
        if len(self.data.Close) < 100:
            return 0
        
        score = 0
        
        # 1. Trend Alignment (0-2 points)
        close = self.data.Close[-1]
        if close > self.ema_8[-1] > self.ema_21[-1] > self.ema_50[-1]:
            score += 2  # Strong bullish
        elif close > self.ema_8[-1] > self.ema_21[-1]:
            score += 1  # Moderate bullish
        elif close < self.ema_8[-1] < self.ema_21[-1] < self.ema_50[-1]:
            score -= 2  # Strong bearish
        elif close < self.ema_8[-1] < self.ema_21[-1]:
            score -= 1  # Moderate bearish
        
        # 2. Momentum (0-2 points)
        rsi_bullish = 30 < self.rsi_14[-1] < 70 and self.rsi_14[-1] > self.rsi_21[-1]
        rsi_bearish = 30 < self.rsi_14[-1] < 70 and self.rsi_14[-1] < self.rsi_21[-1]
        macd_bullish = self.macd[-1] > self.macd_signal[-1] and self.macd_histogram[-1] > 0
        macd_bearish = self.macd[-1] < self.macd_signal[-1] and self.macd_histogram[-1] < 0
        
        if rsi_bullish and macd_bullish:
            score += 2
        elif rsi_bullish or macd_bullish:
            score += 1
        elif rsi_bearish and macd_bearish:
            score -= 2
        elif rsi_bearish or macd_bearish:
            score -= 1
        
        # 3. Trend Strength (0-1 points)
        if self.adx[-1] >= 25:
            score += 1  # Strong trend
        elif self.adx[-1] >= 20:
            score += 0.5  # Moderate trend
        
        # 4. Volume Confirmation (0-1 points)
        if self.volume_ratio[-1] >= 1.2:
            score += 1  # High volume
        elif self.volume_ratio[-1] >= 0.8:
            score += 0.5  # Normal volume
        
        # 5. Volatility Filter (0-1 points)
        # Check if price is not at extremes
        bb_width = self.bb_upper[-1] - self.bb_lower[-1]
        bb_position = (close - self.bb_lower[-1]) / bb_width if bb_width > 0 else 0.5
        
        if 0.2 < bb_position < 0.8:  # Not at Bollinger Band extremes
            score += 1
        
        return int(score)
    
    def generate_signals(self) -> int:
        """
        Generate trading signals based on confluence score
        Returns: 1 for long, -1 for short, 0 for no signal
        """
        # Calculate confluence score
        confluence_score = self.calculate_confluence_score()
        
        # Check if we meet threshold for trading
        if abs(confluence_score) >= self.confluence_threshold:
            if confluence_score > 0:
                return 1  # Long signal
            elif confluence_score < 0:
                return -1  # Short signal
        
        # Exit signals
        if self.position:
            # Exit long if trend reverses
            if self.position.is_long and self.data.Close[-1] < self.ema_21[-1]:
                return -1
            # Exit short if trend reverses
            elif self.position.is_short and self.data.Close[-1] > self.ema_21[-1]:
                return 1
        
        return 0  # No signal


def test_enhanced_strategy():
    """Test the BTCUSDTEnhancedStrategy with the Universal Backtesting Engine"""
    
    print("="*80)
    print("🚀 TESTING BTCUSDT ENHANCED STRATEGY WITH UNIVERSAL ENGINE")
    print("="*80)
    
    # Initialize the universal backtesting engine
    engine = UniversalBacktestEngine(data_source='yfinance')
    
    # Test with different risk profiles
    risk_profiles = ['conservative', 'moderate', 'aggressive']
    results = {}
    
    for profile in risk_profiles:
        print(f"\n📊 Testing {profile.upper()} Risk Profile")
        print("-"*40)
        
        result = engine.run_backtest(
            strategy_class=BTCUSDTEnhancedAdapter,
            symbol='BTC-USD',
            start_date='2024-01-01',
            end_date='2024-06-01',
            initial_cash=100000,
            commission=0.001,
            risk_profile=profile  # Pass risk profile parameter
        )
        
        results[profile] = result
    
    # Compare results
    print("\n" + "="*80)
    print("📈 RISK PROFILE COMPARISON:")
    print("-"*80)
    print(f"{'Profile':<15} {'Return':<12} {'Max DD':<12} {'Win Rate':<12} {'Trades':<10} {'Sharpe':<10}")
    print("-"*80)
    
    for profile, result in results.items():
        perf = result['performance']
        print(f"{profile:<15} "
              f"{perf['total_return']:>10.2f}% "
              f"{perf['max_drawdown']:>10.2f}% "
              f"{perf['win_rate']:>10.2f}% "
              f"{perf['total_trades']:>8} "
              f"{perf['sharpe_ratio']:>8.2f}")
    
    # Find best performer
    best_profile = max(results.keys(), key=lambda x: results[x]['performance']['total_return'])
    best_return = results[best_profile]['performance']['total_return']
    
    print("\n" + "="*80)
    print(f"🏆 BEST PERFORMER: {best_profile.upper()} with {best_return:.2f}% return")
    print("="*80)
    
    return results


if __name__ == "__main__":
    results = test_enhanced_strategy()