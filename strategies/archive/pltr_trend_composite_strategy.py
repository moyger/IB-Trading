#!/usr/bin/env python3
"""
PLTR Trend Composite Strategy - Arthur Hill's Method
Testing on individual stock (PLTR) instead of ETF (MTUM)

Trend Composite Components:
1. TIP Moving Average Trend
2. TIP CCI Close  
3. Bollinger Bands
4. Keltner Channels
5. TIP StochClose

Score: -5 (very bearish) to +5 (very bullish)
Individual stocks should respond better to trend composite than ETFs
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PLTRTrendComposite:
    """
    Arthur Hill's Trend Composite for individual stock (PLTR)
    """
    
    def __init__(self, capital=5000):
        self.capital = capital
        
        # Position allocation based on composite score
        # More aggressive for individual stocks
        self.position_levels = {
            5: 1.00,   # +5: 100% invested (very bullish)
            4: 0.90,   # +4: 90% invested (bullish)  
            3: 0.75,   # +3: 75% invested (moderately bullish)
            2: 0.60,   # +2: 60% invested (mildly bullish)
            1: 0.40,   # +1: 40% invested (slightly bullish)
            0: 0.25,   # 0: 25% invested (neutral - small position)
            -1: 0.10,  # -1: 10% invested (slightly bearish - minimal)
            -2: 0.00,  # -2: 0% invested (mildly bearish)
            -3: 0.00,  # -3: 0% invested (moderately bearish)
            -4: 0.00,  # -4: 0% invested (bearish)
            -5: 0.00   # -5: 0% invested (very bearish)
        }
    
    def calculate_tip_ma_trend(self, df, period=50):
        """
        TIP Moving Average Trend - Enhanced for individual stocks
        """
        ma = df['close'].rolling(period).mean()
        
        # Multi-timeframe MA analysis
        ma20 = df['close'].rolling(20).mean()
        ma50 = df['close'].rolling(50).mean()
        
        # Price above MA and MA trending up = strong bullish
        ma_slope = ma.diff(5)  # 5-day slope
        price_above_ma = df['close'] > ma
        ma_rising = ma_slope > 0
        
        # Additional: Short MA above long MA
        short_above_long = ma20 > ma50
        
        # Enhanced signal for stocks
        conditions = [price_above_ma, ma_rising, short_above_long]
        bullish_count = sum(conditions)
        
        signal = np.where(bullish_count >= 2, 1,
                 np.where(bullish_count <= 1, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_cci_close(self, df, period=20):
        """
        TIP CCI Close - More sensitive for individual stocks
        """
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - ma) / (0.015 * mad)
        
        # More nuanced CCI signals for stocks
        # CCI > 100 = strong bullish, CCI > 0 = mild bullish
        # CCI < -100 = strong bearish, CCI < 0 = mild bearish
        signal = np.where(cci > 50, 1, np.where(cci < -50, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """
        Bollinger Bands - Trend vs mean reversion for stocks
        """
        ma = df['close'].rolling(period).mean()
        std_dev = df['close'].rolling(period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        # BB Position analysis
        bb_position = (df['close'] - lower_band) / (upper_band - lower_band)
        
        # Trend bias: Price above middle + expanding bands = bullish trend
        # Price below middle + contracting bands = bearish trend
        band_width = (upper_band - lower_band) / ma
        band_expanding = band_width > band_width.shift(5)
        
        signal = np.where((df['close'] > ma) & band_expanding, 1,
                 np.where((df['close'] < ma) & ~band_expanding, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_keltner_channels(self, df, period=20, multiplier=2):
        """
        Keltner Channels - Breakout detection for stocks
        """
        ma = df['close'].rolling(period).mean()
        
        # Average True Range
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        
        upper_channel = ma + (multiplier * atr)
        lower_channel = ma - (multiplier * atr)
        
        # Breakout analysis - key for individual stocks
        breakout_up = df['close'] > upper_channel
        breakdown = df['close'] < lower_channel
        
        # Trend following: breakouts are bullish, breakdowns bearish
        signal = np.where(breakout_up | (df['close'] > ma), 1,
                 np.where(breakdown | (df['close'] < ma), -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_stochclose(self, df, k_period=14, d_period=3):
        """
        TIP StochClose - Momentum confirmation for stocks
        """
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(d_period).mean()
        
        # Stochastic trend analysis
        # Rising stoch above 50 = bullish momentum
        # Falling stoch below 50 = bearish momentum
        stoch_rising = d_percent > d_percent.shift(2)
        
        signal = np.where((d_percent > 50) & stoch_rising, 1,
                 np.where((d_percent < 50) & ~stoch_rising, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_trend_composite(self, df):
        """
        Calculate the 5-component Trend Composite score for PLTR
        """
        # Calculate all 5 components
        tip_ma = self.calculate_tip_ma_trend(df)
        tip_cci = self.calculate_tip_cci_close(df)
        bollinger = self.calculate_bollinger_bands(df)
        keltner = self.calculate_keltner_channels(df)
        tip_stoch = self.calculate_tip_stochclose(df)
        
        # Combine into composite score (-5 to +5)
        composite = tip_ma + tip_cci + bollinger + keltner + tip_stoch
        
        # Calculate position allocation
        allocation = composite.map(self.position_levels)
        
        return pd.DataFrame({
            'tip_ma_trend': tip_ma,
            'tip_cci_close': tip_cci,
            'bollinger_bands': bollinger,
            'keltner_channels': keltner,
            'tip_stochclose': tip_stoch,
            'composite_score': composite,
            'position_allocation': allocation
        })

def run_pltr_trend_composite_backtest():
    """
    Backtest PLTR using Arthur Hill's Trend Composite
    """
    
    print("🚀 PLTR TREND COMPOSITE STRATEGY (Individual Stock)")
    print("=" * 80)
    print("📊 Testing Arthur Hill's method on individual stock vs ETF")
    print("🎯 Symbol: PLTR (Palantir Technologies)")
    print("📊 Components:")
    print("   1. TIP Moving Average Trend (enhanced for stocks)")
    print("   2. TIP CCI Close (more sensitive)")
    print("   3. Bollinger Bands (trend vs mean reversion)")
    print("   4. Keltner Channels (breakout detection)")
    print("   5. TIP StochClose (momentum confirmation)")
    print("📏 Score Range: -5 (very bearish) to +5 (very bullish)")
    print("=" * 80)
    
    # Parameters
    capital = 5000
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    
    print(f"💰 Capital: ${capital:,}")
    print(f"📅 Period: {start_date} to {end_date}")
    print("=" * 80)
    
    # Download PLTR data
    try:
        extended_start = "2023-01-01"  # Need extra data for indicators
        
        print("📊 Downloading PLTR data...")
        pltr = yf.Ticker("PLTR")
        df = pltr.history(start=extended_start, end=end_date)
        
        if df.empty:
            print("❌ No PLTR data available")
            return
        
        # Clean column names
        df.columns = [col.lower() for col in df.columns]
        print(f"✅ PLTR data: {len(df)} days")
        
        # Check if we have reasonable price levels
        latest_price = df['close'].iloc[-1]
        print(f"💰 Latest PLTR price: ${latest_price:.2f}")
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return
    
    # Initialize strategy
    strategy = PLTRTrendComposite(capital)
    
    # Calculate trend composite
    print("🔧 Calculating Trend Composite indicators for PLTR...")
    trend_data = strategy.calculate_trend_composite(df)
    
    # Merge with price data
    df = df.join(trend_data)
    
    # Filter to backtest period
    backtest_df = df[df.index >= start_date].copy()
    
    if backtest_df.empty:
        print("❌ No backtest data available for the specified period")
        return
    
    # Initialize portfolio tracking
    cash = capital
    shares = 0
    current_allocation = 0.0
    
    results = []
    trades = []
    rebalances = 0
    
    print(f"\n📈 Running PLTR Trend Composite backtest...")
    print("🔄 Individual stock should respond better to trend signals...\n")
    
    for i, (date, row) in enumerate(backtest_df.iterrows()):
        price = row['close']
        score = row['composite_score']
        target_allocation = row['position_allocation']
        
        if pd.isna(score) or pd.isna(target_allocation):
            continue
        
        # Calculate current portfolio value
        portfolio_value = cash + (shares * price)
        
        # Check if allocation change is needed (5% threshold)
        allocation_change = abs(target_allocation - current_allocation)
        
        if allocation_change >= 0.05:  # Rebalance if 5%+ change
            rebalances += 1
            
            # Calculate new target position
            target_value = portfolio_value * target_allocation
            new_shares = target_value / price if target_value > 0 else 0
            
            # Execute rebalancing
            if new_shares > shares:
                # Buy more shares
                shares_to_buy = new_shares - shares
                cost = shares_to_buy * price * 1.001  # 0.1% transaction cost
                if cash >= cost:
                    cash -= cost
                    shares = new_shares
                    current_allocation = target_allocation
                    
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': price,
                        'allocation': target_allocation,
                        'score': score
                    })
                    
            elif new_shares < shares:
                # Sell shares
                shares_to_sell = shares - new_shares
                proceeds = shares_to_sell * price * 0.999  # 0.1% transaction cost
                cash += proceeds
                shares = new_shares
                current_allocation = target_allocation
                
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'shares': shares_to_sell,
                    'price': price,
                    'allocation': target_allocation,
                    'score': score
                })
            
            # Print key rebalancing events
            if i < 15 or rebalances <= 25:  # Show more detail for individual stock
                components = [
                    int(row['tip_ma_trend']), int(row['tip_cci_close']), 
                    int(row['bollinger_bands']), int(row['keltner_channels']), 
                    int(row['tip_stochclose'])
                ]
                
                print(f"{date.date()}: PLTR ${price:.2f}")
                print(f"  📊 Score: {score:+.0f} {components} → {target_allocation:.0%} allocation")
                print(f"  💼 Portfolio: ${portfolio_value:,.0f} | Shares: {shares:.0f}")
                
                if allocation_change >= 0.05:
                    action = "BUY" if target_allocation > current_allocation else "SELL" 
                    change_pct = (target_allocation - current_allocation) * 100
                    print(f"  🔄 REBALANCE: {action} ({change_pct:+.0f}%) to {target_allocation:.0%}")
                print()
        
        # Record daily results
        current_portfolio_value = cash + (shares * price)
        
        results.append({
            'date': date,
            'price': price,
            'composite_score': score,
            'allocation': current_allocation,
            'shares': shares,
            'cash': cash,
            'portfolio_value': current_portfolio_value,
            'components': [
                row['tip_ma_trend'], row['tip_cci_close'], 
                row['bollinger_bands'], row['keltner_channels'], 
                row['tip_stochclose']
            ]
        })
    
    # Final analysis
    results_df = pd.DataFrame(results)
    
    if results_df.empty:
        print("❌ No results generated")
        return
    
    final_price = results_df['price'].iloc[-1]
    final_value = results_df['portfolio_value'].iloc[-1]
    total_return = (final_value / capital) - 1
    
    # Benchmark comparison
    start_price = results_df['price'].iloc[0]
    pltr_return = (final_price / start_price) - 1
    
    # SPY comparison
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=start_date, end=end_date)
        spy_return = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[0]) - 1
    except:
        spy_return = 0
    
    # Calculate time-weighted allocation
    avg_allocation = results_df['allocation'].mean()
    
    # Performance analysis
    years = len(results_df) / 252
    annual_return = (1 + total_return) ** (1/years) - 1
    pltr_annual = (1 + pltr_return) ** (1/years) - 1
    spy_annual = (1 + spy_return) ** (1/years) - 1
    
    print(f"🏆 PLTR TREND COMPOSITE RESULTS")
    print("=" * 80)
    print(f"Final Value:            ${final_value:,.0f}")
    print(f"Total Return:           {total_return:+.1%}")
    print(f"Annual Return:          {annual_return:+.1%}")
    print(f"PLTR Buy-Hold:          {pltr_return:+.1%} ({pltr_annual:+.1%} annual)")
    print(f"SPY Benchmark:          {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs PLTR:                {total_return - pltr_return:+.1%}")
    print(f"vs SPY:                 {total_return - spy_return:+.1%}")
    print(f"Period:                 {years:.1f} years")
    
    print(f"\n📊 PLTR TREND COMPOSITE ANALYSIS:")
    print(f"Total Rebalances:       {rebalances}")
    print(f"Average Allocation:     {avg_allocation:.1%}")
    print(f"Time Fully Invested:    {(results_df['allocation'] >= 0.9).sum() / len(results_df) * 100:.1f}%")
    print(f"Time Partially Invested:{((results_df['allocation'] > 0.1) & (results_df['allocation'] < 0.9)).sum() / len(results_df) * 100:.1f}%")
    print(f"Time Minimal/Cash:      {(results_df['allocation'] <= 0.1).sum() / len(results_df) * 100:.1f}%")
    
    # Score distribution
    score_counts = results_df['composite_score'].value_counts().sort_index()
    print(f"\n📈 SCORE DISTRIBUTION:")
    for score in range(-5, 6):
        count = score_counts.get(score, 0)
        pct = count / len(results_df) * 100 if len(results_df) > 0 else 0
        allocation = strategy.position_levels.get(score, 0)
        bar = "█" * int(pct / 5) if pct > 0 else ""
        print(f"   Score {score:+2d}: {count:3d} days ({pct:4.1f}%) → {allocation:.0%} allocation {bar}")
    
    # Volatility comparison
    strategy_returns = results_df['portfolio_value'].pct_change().dropna()
    pltr_returns = results_df['price'].pct_change().dropna()
    
    strategy_vol = strategy_returns.std() * np.sqrt(252) * 100
    pltr_vol = pltr_returns.std() * np.sqrt(252) * 100
    
    print(f"\n📊 RISK ANALYSIS:")
    print(f"Strategy Volatility:    {strategy_vol:.1f}% annual")
    print(f"PLTR Volatility:        {pltr_vol:.1f}% annual")
    print(f"Volatility Reduction:   {pltr_vol - strategy_vol:.1f}% points")
    
    # Performance rating
    if total_return > pltr_return + 0.05:
        rating = "🏆 EXCELLENT - Beat PLTR by 5%+"
    elif total_return > pltr_return + 0.02:
        rating = "🏆 EXCELLENT - Beat PLTR significantly"
    elif total_return > pltr_return:
        rating = "✅ GOOD - Beat PLTR buy-and-hold"
    elif total_return > spy_return:
        rating = "⚠️ FAIR - Beat SPY but not PLTR"
    else:
        rating = "❌ POOR - Underperformed"
    
    print(f"\nStrategy Rating:        {rating}")
    
    # Key trades summary
    if trades:
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        
        print(f"\n📋 TRADING SUMMARY:")
        print(f"Buy Transactions:       {len(buy_trades)}")
        print(f"Sell Transactions:      {len(sell_trades)}")
        print(f"Total Transactions:     {len(trades)}")
        if trades:
            avg_trade_size = np.mean([abs(t.get('shares', 0)) * t.get('price', 0) for t in trades])
            print(f"Avg Trade Size:         ${avg_trade_size:.0f}")
    
    print(f"\n🎯 INDIVIDUAL STOCK ADVANTAGES:")
    print(f"   ✅ Higher volatility creates clearer trend signals")
    print(f"   ✅ Breakouts/breakdowns more meaningful")
    print(f"   ✅ Technical indicators less correlated")
    print(f"   ✅ Trend following works better on single names")
    print(f"   ✅ Position sizing flexibility important for risk")
    
    # Show some recent significant trades
    if trades and len(trades) >= 5:
        print(f"\n📋 RECENT SIGNIFICANT TRADES:")
        recent_trades = trades[-5:]
        for trade in recent_trades:
            action_emoji = "📥" if trade['action'] == 'BUY' else "📤"
            print(f"   {action_emoji} {trade['date'].date()}: {trade['action']} {trade['shares']:.0f} shares @ ${trade['price']:.2f} (Score: {trade['score']:+.0f})")
    
    return results_df, trades

if __name__ == "__main__":
    results_df, trades = run_pltr_trend_composite_backtest()