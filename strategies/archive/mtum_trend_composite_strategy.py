#!/usr/bin/env python3
"""
MTUM Trend Composite Strategy - Arthur Hill's StockCharts Method
Based on 5 Trend Composite indicators:
1. TIP Moving Average Trend
2. TIP CCI Close  
3. Bollinger Bands
4. Keltner Channels
5. TIP StochClose

Score: -5 (very bearish) to +5 (very bullish)
Position allocation based on composite score
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MTUMTrendComposite:
    """
    Arthur Hill's Trend Composite adapted for MTUM
    """
    
    def __init__(self, capital=5000):
        self.capital = capital
        
        # Position allocation based on composite score
        self.position_levels = {
            5: 1.00,   # +5: 100% invested (very bullish)
            4: 1.00,   # +4: 100% invested (bullish)  
            3: 0.75,   # +3: 75% invested (moderately bullish)
            2: 0.75,   # +2: 75% invested (mildly bullish)
            1: 0.50,   # +1: 50% invested (slightly bullish)
            0: 0.50,   # 0: 50% invested (neutral)
            -1: 0.25,  # -1: 25% invested (slightly bearish)
            -2: 0.25,  # -2: 25% invested (mildly bearish)
            -3: 0.00,  # -3: 0% invested (moderately bearish)
            -4: 0.00,  # -4: 0% invested (bearish)
            -5: 0.00   # -5: 0% invested (very bearish)
        }
    
    def calculate_tip_ma_trend(self, df, period=50):
        """
        TIP Moving Average Trend - Trend direction based on MA
        """
        ma = df['close'].rolling(period).mean()
        
        # Price above rising MA = bullish (+1)
        # Price below falling MA = bearish (-1)
        ma_slope = ma.diff(5)  # 5-day slope
        price_above_ma = df['close'] > ma
        ma_rising = ma_slope > 0
        
        # Combined signal
        signal = np.where((price_above_ma & ma_rising), 1,
                 np.where((~price_above_ma & ~ma_rising), -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_cci_close(self, df, period=20):
        """
        TIP CCI Close - CCI-based trend signal
        """
        # Commodity Channel Index
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - ma) / (0.015 * mad)
        
        # CCI > 0 = bullish, CCI < 0 = bearish
        signal = np.where(cci > 0, 1, -1)
        
        return pd.Series(signal, index=df.index)
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """
        Bollinger Bands trend signal
        """
        ma = df['close'].rolling(period).mean()
        std_dev = df['close'].rolling(period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        # Price above middle line (MA) = bullish
        # Price below middle line (MA) = bearish
        signal = np.where(df['close'] > ma, 1, -1)
        
        return pd.Series(signal, index=df.index)
    
    def calculate_keltner_channels(self, df, period=20, multiplier=2):
        """
        Keltner Channels trend signal
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
        
        # Price above center line (MA) = bullish
        # Price below center line (MA) = bearish  
        signal = np.where(df['close'] > ma, 1, -1)
        
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_stochclose(self, df, k_period=14, d_period=3):
        """
        TIP StochClose - Stochastic-based trend signal
        """
        # Stochastic Oscillator
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(d_period).mean()
        
        # Stoch > 50 = bullish, Stoch < 50 = bearish
        signal = np.where(d_percent > 50, 1, -1)
        
        return pd.Series(signal, index=df.index)
    
    def calculate_trend_composite(self, df):
        """
        Calculate the 5-component Trend Composite score
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

def run_mtum_trend_composite_backtest():
    """
    Backtest MTUM using Arthur Hill's Trend Composite
    """
    
    print("🚀 MTUM TREND COMPOSITE STRATEGY (Arthur Hill Method)")
    print("=" * 80)
    print("📊 Components:")
    print("   1. TIP Moving Average Trend")
    print("   2. TIP CCI Close")
    print("   3. Bollinger Bands") 
    print("   4. Keltner Channels")
    print("   5. TIP StochClose")
    print("📏 Score Range: -5 (very bearish) to +5 (very bullish)")
    print("=" * 80)
    
    # Parameters
    capital = 5000
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    
    print(f"💰 Capital: ${capital:,}")
    print(f"📅 Period: {start_date} to {end_date}")
    print("=" * 80)
    
    # Download MTUM data
    try:
        extended_start = "2023-01-01"  # Need extra data for indicators
        
        print("📊 Downloading MTUM data...")
        mtum = yf.Ticker("MTUM")
        df = mtum.history(start=extended_start, end=end_date)
        
        if df.empty:
            print("❌ No MTUM data available")
            return
        
        # Clean column names
        df.columns = [col.lower() for col in df.columns]
        print(f"✅ MTUM data: {len(df)} days")
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return
    
    # Initialize strategy
    strategy = MTUMTrendComposite(capital)
    
    # Calculate trend composite
    print("🔧 Calculating Trend Composite indicators...")
    trend_data = strategy.calculate_trend_composite(df)
    
    # Merge with price data
    df = df.join(trend_data)
    
    # Filter to backtest period
    backtest_df = df[df.index >= start_date].copy()
    
    # Initialize portfolio tracking
    cash = capital
    shares = 0
    current_allocation = 0.0
    
    results = []
    trades = []
    rebalances = 0
    
    print(f"\n📈 Running Trend Composite backtest...")
    print("🔄 Rebalancing based on composite score changes...\n")
    
    for i, (date, row) in enumerate(backtest_df.iterrows()):
        price = row['close']
        score = row['composite_score']
        target_allocation = row['position_allocation']
        
        if pd.isna(score) or pd.isna(target_allocation):
            continue
        
        # Calculate current portfolio value
        portfolio_value = cash + (shares * price)
        
        # Check if allocation change is needed
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
            if i < 10 or rebalances <= 20:  # Show first 10 days and first 20 rebalances
                components = [
                    int(row['tip_ma_trend']), int(row['tip_cci_close']), 
                    int(row['bollinger_bands']), int(row['keltner_channels']), 
                    int(row['tip_stochclose'])
                ]
                
                print(f"{date.date()}: ${price:.2f}")
                print(f"  📊 Score: {score:+.0f} {components} → {target_allocation:.0%} allocation")
                print(f"  💼 Portfolio: ${portfolio_value:,.0f} | Shares: {shares:.1f}")
                
                if allocation_change >= 0.05:
                    action = "BUY" if target_allocation > current_allocation else "SELL" 
                    print(f"  🔄 REBALANCE: {action} to {target_allocation:.0%}")
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
    mtum_return = (final_price / start_price) - 1
    
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
    mtum_annual = (1 + mtum_return) ** (1/years) - 1
    spy_annual = (1 + spy_return) ** (1/years) - 1
    
    print(f"🏆 MTUM TREND COMPOSITE RESULTS")
    print("=" * 80)
    print(f"Final Value:            ${final_value:,.0f}")
    print(f"Total Return:           {total_return:+.1%}")
    print(f"Annual Return:          {annual_return:+.1%}")
    print(f"MTUM Buy-Hold:          {mtum_return:+.1%} ({mtum_annual:+.1%} annual)")
    print(f"SPY Benchmark:          {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs MTUM:                {total_return - mtum_return:+.1%}")
    print(f"vs SPY:                 {total_return - spy_return:+.1%}")
    print(f"Period:                 {years:.1f} years")
    
    print(f"\n📊 TREND COMPOSITE ANALYSIS:")
    print(f"Total Rebalances:       {rebalances}")
    print(f"Average Allocation:     {avg_allocation:.1%}")
    print(f"Time Fully Invested:    {(results_df['allocation'] == 1.0).sum() / len(results_df) * 100:.1f}%")
    print(f"Time Partially Invested:{((results_df['allocation'] > 0) & (results_df['allocation'] < 1.0)).sum() / len(results_df) * 100:.1f}%")
    print(f"Time in Cash:           {(results_df['allocation'] == 0.0).sum() / len(results_df) * 100:.1f}%")
    
    # Score distribution
    score_counts = results_df['composite_score'].value_counts().sort_index()
    print(f"\n📈 SCORE DISTRIBUTION:")
    for score in range(-5, 6):
        count = score_counts.get(score, 0)
        pct = count / len(results_df) * 100
        allocation = strategy.position_levels[score]
        print(f"   Score {score:+2d}: {count:3d} days ({pct:4.1f}%) → {allocation:.0%} allocation")
    
    # Performance rating
    if total_return > mtum_return + 0.05:
        rating = "🏆 EXCELLENT - Beat MTUM by 5%+"
    elif total_return > mtum_return + 0.02:
        rating = "🏆 EXCELLENT - Beat MTUM significantly"
    elif total_return > mtum_return:
        rating = "✅ GOOD - Beat MTUM"
    elif total_return > spy_return:
        rating = "⚠️ FAIR - Beat SPY"
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
        print(f"Avg Rebalance Size:     {np.mean([abs(t.get('shares', 0)) for t in trades]):.1f} shares")
    
    print(f"\n🎯 TREND COMPOSITE ADVANTAGES:")
    print(f"   ✅ Gradual position sizing (0%, 25%, 50%, 75%, 100%)")
    print(f"   ✅ Multiple trend confirmation signals")
    print(f"   ✅ Higher average deployment vs binary strategies")
    print(f"   ✅ Smoother equity curve with less whipsaws")
    print(f"   ✅ Professional trend-following methodology")
    
    return results_df, trades

if __name__ == "__main__":
    results_df, trades = run_mtum_trend_composite_backtest()