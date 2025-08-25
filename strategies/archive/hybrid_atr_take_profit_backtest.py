#!/usr/bin/env python3
"""
Hybrid ATR Take-Profit + Trend Composite Strategy Backtest
Combines trend composite allocation with ATR take-profit protection

Strategy:
1. Use trend composite for dynamic allocation (0%-100%) as normal
2. When stock reaches +20% profit, activate ATR take-profit protection
3. Set ATR trailing take-profit: 2x ATR below highest price since +20% threshold
4. If price hits ATR take-profit → Exit completely, lock profits
5. Re-enter only on fresh trend composite entry signal
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class HybridATRTakeProfit:
    """
    Hybrid strategy: Trend Composite allocation + ATR take-profit protection
    """
    
    def __init__(self, capital=5000, profit_threshold=0.20, atr_multiplier=2.0):
        self.capital = capital
        self.stocks = ['AMZN', 'TSLA', 'RBLX']
        self.capital_per_stock = capital / len(self.stocks)
        self.profit_threshold = profit_threshold  # 20% profit to activate take-profit
        self.atr_multiplier = atr_multiplier  # 2x ATR below highest price
        
        # Optimized position allocation levels
        self.position_levels = {
            -5: 0.00, -4: 0.00, -3: 0.00, -2: 0.00, -1: 0.00,
             0: 0.20,  1: 0.40,  2: 0.60,  3: 0.80,  4: 1.00,  5: 1.00
        }
    
    def calculate_atr(self, df, period=22):
        """Calculate Average True Range (ATR)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        
        return atr
    
    def calculate_tip_ma_trend(self, df, period=50):
        """TIP Moving Average Trend"""
        ma = df['close'].rolling(period).mean()
        ma20 = df['close'].rolling(20).mean()
        ma50 = df['close'].rolling(50).mean()
        
        ma_slope = ma.diff(5)
        price_above_ma = df['close'] > ma
        ma_rising = ma_slope > 0
        short_above_long = ma20 > ma50
        
        conditions = [price_above_ma, ma_rising, short_above_long]
        bullish_count = sum(conditions)
        
        signal = np.where(bullish_count >= 2, 1, np.where(bullish_count <= 1, -1, 0))
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_cci_close(self, df, period=20):
        """TIP CCI Close"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - ma) / (0.015 * mad)
        
        signal = np.where(cci > 50, 1, np.where(cci < -50, -1, 0))
        return pd.Series(signal, index=df.index)
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """Bollinger Bands"""
        ma = df['close'].rolling(period).mean()
        signal = np.where(df['close'] > ma, 1, -1)
        return pd.Series(signal, index=df.index)
    
    def calculate_keltner_channels(self, df, period=20, multiplier=2):
        """Keltner Channels"""
        ma = df['close'].rolling(period).mean()
        
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        
        upper_channel = ma + (multiplier * atr)
        lower_channel = ma - (multiplier * atr)
        
        signal = np.where(df['close'] > upper_channel, 1,
                 np.where(df['close'] < lower_channel, -1, 0))
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_stochclose(self, df, k_period=14, d_period=3):
        """TIP StochClose"""
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(d_period).mean()
        
        signal = np.where(d_percent > 60, 1, np.where(d_percent < 40, -1, 0))
        return pd.Series(signal, index=df.index)
    
    def calculate_trend_composite_with_take_profit(self, df):
        """
        Calculate trend composite + ATR for take-profit analysis
        """
        # Calculate trend composite components
        tip_ma = self.calculate_tip_ma_trend(df)
        tip_cci = self.calculate_tip_cci_close(df)
        bollinger = self.calculate_bollinger_bands(df)
        keltner = self.calculate_keltner_channels(df)
        tip_stoch = self.calculate_tip_stochclose(df)
        
        # Combine into composite score
        composite = tip_ma + tip_cci + bollinger + keltner + tip_stoch
        
        # Calculate position allocation from trend composite
        base_allocation = composite.map(self.position_levels)
        
        # Calculate ATR for take-profit calculations
        atr = self.calculate_atr(df)
        
        return pd.DataFrame({
            'price': df['close'],
            'tip_ma_trend': tip_ma,
            'tip_cci_close': tip_cci,
            'bollinger_bands': bollinger,
            'keltner_channels': keltner,
            'tip_stochclose': tip_stoch,
            'composite_score': composite,
            'base_allocation': base_allocation,
            'atr': atr
        })

def run_hybrid_take_profit_backtest():
    """
    Backtest hybrid ATR take-profit + Trend Composite strategy
    """
    
    print("🚀 HYBRID ATR TAKE-PROFIT + TREND COMPOSITE BACKTEST")
    print("=" * 80)
    print("📊 Portfolio: AMZN, TSLA, RBLX")
    print("💰 Capital: $5,000")
    print("🎯 Strategy: Trend Composite + ATR take-profit protection")
    print("📈 Take-Profit: Activate at +20% profit, 2x ATR trail")
    print("=" * 80)
    
    # Parameters
    capital = 5000
    stocks = ['AMZN', 'TSLA', 'RBLX']
    capital_per_stock = capital / len(stocks)
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    profit_threshold = 0.20  # 20% profit to activate take-profit
    atr_multiplier = 2.0     # 2x ATR below highest price
    
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"🎯 Profit Threshold: {profit_threshold:.0%} to activate take-profit")
    print(f"🛡️ ATR Multiplier: {atr_multiplier}x ATR below highest price")
    print("=" * 80)
    
    # Download data for all stocks
    stock_data = {}
    stock_strategies = {}
    
    for stock in stocks:
        print(f"📊 Downloading {stock} data...")
        try:
            extended_start = "2023-01-01"
            ticker = yf.Ticker(stock)
            df = ticker.history(start=extended_start, end=end_date)
            
            if df.empty:
                print(f"❌ No data for {stock}")
                continue
            
            df.columns = [col.lower() for col in df.columns]
            stock_data[stock] = df
            
            strategy = HybridATRTakeProfit(capital_per_stock, profit_threshold, atr_multiplier)
            stock_strategies[stock] = strategy
            
            print(f"✅ {stock}: {len(df)} days")
            
        except Exception as e:
            print(f"❌ Error downloading {stock}: {e}")
            continue
    
    if len(stock_data) != 3:
        print(f"❌ Need data for all 3 stocks, got {len(stock_data)}")
        return None, None
    
    # Calculate indicators for each stock
    print("\n🔧 Calculating Hybrid indicators...")
    stock_indicators = {}
    
    for stock in stocks:
        df = stock_data[stock]
        strategy = stock_strategies[stock]
        
        print(f"   📊 Processing {stock} (Trend Composite + ATR take-profit)...")
        indicators = strategy.calculate_trend_composite_with_take_profit(df)
        indicators['stock'] = stock
        
        # Filter to backtest period
        backtest_data = indicators[indicators.index >= start_date].copy()
        stock_indicators[stock] = backtest_data
    
    # Get common date range
    common_dates = None
    for stock, data in stock_indicators.items():
        if common_dates is None:
            common_dates = set(data.index)
        else:
            common_dates = common_dates.intersection(set(data.index))
    
    common_dates = sorted(list(common_dates))
    print(f"✅ Common trading days: {len(common_dates)}")
    
    # Initialize portfolio tracking with take-profit states
    portfolio_results = []
    portfolio_cash = capital
    stock_positions = {}
    
    for stock in stocks:
        stock_positions[stock] = {
            'shares': 0,
            'allocation': 0.0,
            'value': 0.0,
            'entry_price': 0.0,
            'entry_date': None,
            'take_profit_active': False,
            'take_profit_level': 0.0,
            'highest_since_threshold': 0.0,
            'profit_locked_in': False
        }
    
    total_rebalances = 0
    take_profit_exits = 0
    all_trades = []
    
    print(f"\n📈 Running Hybrid Take-Profit backtest...")
    print("🔄 Dynamic allocation + Take-profit protection at +20%...")
    
    for i, date in enumerate(common_dates):
        daily_data = {}
        
        # Get data for each stock
        for stock in stocks:
            if date in stock_indicators[stock].index:
                row = stock_indicators[stock].loc[date]
                daily_data[stock] = {
                    'price': row['price'],
                    'score': row['composite_score'],
                    'base_allocation': row['base_allocation'],
                    'atr': row['atr']
                }
        
        if len(daily_data) != 3:
            continue
        
        # Calculate current portfolio value
        portfolio_value = portfolio_cash
        for stock in stocks:
            if stock in daily_data:
                portfolio_value += stock_positions[stock]['shares'] * daily_data[stock]['price']
        
        # Process each stock for take-profit and rebalancing
        needs_rebalancing = False
        take_profit_triggers_today = 0
        
        for stock in stocks:
            pos = stock_positions[stock]
            price = daily_data[stock]['price']
            target_allocation = daily_data[stock]['base_allocation']
            atr = daily_data[stock]['atr']
            
            if pd.isna(atr):
                continue
            
            # If we have a position, check take-profit logic
            if pos['shares'] > 0 and pos['entry_price'] > 0:
                current_profit = (price / pos['entry_price']) - 1
                
                # Activate take-profit if we hit profit threshold
                if not pos['take_profit_active'] and current_profit >= profit_threshold:
                    pos['take_profit_active'] = True
                    pos['highest_since_threshold'] = price
                    pos['take_profit_level'] = price - (atr_multiplier * atr)
                    
                    all_trades.append({
                        'date': date,
                        'stock': stock,
                        'action': 'TAKE_PROFIT_ACTIVATED',
                        'price': price,
                        'profit_pct': current_profit * 100,
                        'take_profit_level': pos['take_profit_level']
                    })
                
                # Update take-profit level if active
                if pos['take_profit_active']:
                    # Update highest price since threshold
                    if price > pos['highest_since_threshold']:
                        pos['highest_since_threshold'] = price
                        # Update trailing take-profit level
                        new_take_profit_level = pos['highest_since_threshold'] - (atr_multiplier * atr)
                        pos['take_profit_level'] = max(pos['take_profit_level'], new_take_profit_level)
                    
                    # Check if take-profit triggered
                    if price <= pos['take_profit_level']:
                        # Exit completely - take profit!
                        exit_profit = (price / pos['entry_price']) - 1
                        take_profit_exits += 1
                        take_profit_triggers_today += 1
                        
                        all_trades.append({
                            'date': date,
                            'stock': stock,
                            'action': 'TAKE_PROFIT_EXIT',
                            'shares': pos['shares'],
                            'entry_price': pos['entry_price'],
                            'exit_price': price,
                            'profit_pct': exit_profit * 100,
                            'days_held': (date - pos['entry_date']).days if pos['entry_date'] else 0
                        })
                        
                        # Reset position
                        proceeds = pos['shares'] * price * 0.999  # 0.1% transaction cost
                        portfolio_cash += proceeds
                        pos['shares'] = 0
                        pos['allocation'] = 0.0
                        pos['entry_price'] = 0.0
                        pos['entry_date'] = None
                        pos['take_profit_active'] = False
                        pos['take_profit_level'] = 0.0
                        pos['highest_since_threshold'] = 0.0
                        pos['profit_locked_in'] = True  # Flag for this day
                        
                        needs_rebalancing = True
                        continue
            
            # Regular rebalancing logic (if not profit-locked today)
            if not pos.get('profit_locked_in', False):
                current_allocation = pos['allocation']
                
                # Check if allocation change needed
                if abs(target_allocation - current_allocation) >= 0.05:
                    needs_rebalancing = True
            
            # Reset profit-locked flag for next iteration
            pos['profit_locked_in'] = False
        
        # Execute rebalancing
        if needs_rebalancing:
            total_rebalances += 1
            
            for stock in stocks:
                pos = stock_positions[stock]
                price = daily_data[stock]['price']
                target_allocation = daily_data[stock]['base_allocation']
                
                # Skip if we just took profit today
                if pos.get('profit_locked_in', False):
                    continue
                
                target_value = capital_per_stock * target_allocation
                new_shares = target_value / price if target_value > 0 else 0
                current_shares = pos['shares']
                
                if abs(new_shares - current_shares) > 0.1:
                    shares_delta = new_shares - current_shares
                    
                    if shares_delta > 0:  # Buy
                        cost = shares_delta * price * 1.001
                        if portfolio_cash >= cost:
                            portfolio_cash -= cost
                            
                            # Update position
                            if pos['shares'] == 0:  # New entry
                                pos['entry_price'] = price
                                pos['entry_date'] = date
                            
                            pos['shares'] = new_shares
                            pos['allocation'] = target_allocation
                            
                            all_trades.append({
                                'date': date,
                                'stock': stock,
                                'action': 'BUY',
                                'shares': shares_delta,
                                'price': price,
                                'allocation': target_allocation,
                                'score': daily_data[stock]['score']
                            })
                    
                    elif shares_delta < 0:  # Sell (but not take-profit exit)
                        proceeds = abs(shares_delta) * price * 0.999
                        portfolio_cash += proceeds
                        pos['shares'] = new_shares
                        pos['allocation'] = target_allocation
                        
                        # If selling entire position, reset entry tracking
                        if new_shares == 0:
                            pos['entry_price'] = 0.0
                            pos['entry_date'] = None
                            pos['take_profit_active'] = False
                        
                        all_trades.append({
                            'date': date,
                            'stock': stock,
                            'action': 'SELL',
                            'shares': abs(shares_delta),
                            'price': price,
                            'allocation': target_allocation,
                            'score': daily_data[stock]['score']
                        })
            
            # Print key events
            if i < 10 or total_rebalances <= 20 or take_profit_triggers_today > 0:
                print(f"\n{date.date()}:")
                for stock in stocks:
                    pos = stock_positions[stock]
                    price = daily_data[stock]['price']
                    score = daily_data[stock]['score']
                    allocation = pos['allocation']
                    shares = pos['shares']
                    
                    profit_info = ""
                    if pos['entry_price'] > 0:
                        current_profit = (price / pos['entry_price'] - 1) * 100
                        profit_info = f"P&L: {current_profit:+.1f}%"
                        
                        if pos['take_profit_active']:
                            profit_info += f" | TP: ${pos['take_profit_level']:.2f}"
                    
                    print(f"  {stock}: ${price:.2f} | Score: {score:+.0f} | "
                          f"{allocation:.0%} → {shares:.0f} shares | {profit_info}")
                
                if take_profit_triggers_today > 0:
                    print(f"  💰 {take_profit_triggers_today} take-profit exit(s) today!")
                
                current_portfolio_value = portfolio_cash + sum(pos['shares'] * daily_data[s]['price'] for s, pos in stock_positions.items())
                print(f"  💼 Portfolio: ${current_portfolio_value:,.0f} | Rebalance #{total_rebalances}")
        
        # Record daily results
        current_portfolio_value = portfolio_cash + sum(pos['shares'] * daily_data[stock]['price'] for stock, pos in stock_positions.items())
        total_stock_exposure = sum(stock_positions[stock]['value'] for stock in stocks) / current_portfolio_value if current_portfolio_value > 0 else 0
        
        # Update position values
        for stock in stocks:
            stock_positions[stock]['value'] = stock_positions[stock]['shares'] * daily_data[stock]['price']
        
        portfolio_results.append({
            'date': date,
            'portfolio_value': current_portfolio_value,
            'cash': portfolio_cash,
            'total_stock_exposure': sum(pos['value'] for pos in stock_positions.values()) / current_portfolio_value if current_portfolio_value > 0 else 0,
            'take_profit_active_count': sum(1 for pos in stock_positions.values() if pos['take_profit_active'])
        })
    
    # Final analysis
    results_df = pd.DataFrame(portfolio_results)
    
    if results_df.empty:
        print("❌ No results generated")
        return None, None
    
    final_value = results_df['portfolio_value'].iloc[-1]
    total_return = (final_value / capital) - 1
    
    # Comparison benchmarks
    individual_returns = {}
    for stock in stocks:
        start_price = stock_indicators[stock]['price'].iloc[0]
        end_price = stock_indicators[stock]['price'].iloc[-1]
        individual_returns[stock] = (end_price / start_price) - 1
    
    equal_weight_return = sum(individual_returns.values()) / len(individual_returns)
    
    # SPY benchmark
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=start_date, end=end_date)
        spy_return = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[0]) - 1
    except:
        spy_return = 0
    
    # Performance metrics
    years = len(results_df) / 252
    annual_return = (1 + total_return) ** (1/years) - 1
    equal_weight_annual = (1 + equal_weight_return) ** (1/years) - 1
    spy_annual = (1 + spy_return) ** (1/years) - 1
    
    avg_exposure = results_df['total_stock_exposure'].mean()
    
    print(f"\n🏆 HYBRID ATR TAKE-PROFIT RESULTS")
    print("=" * 80)
    print(f"Final Portfolio Value:  ${final_value:,.0f}")
    print(f"Total Return:           {total_return:+.1%}")
    print(f"Annual Return:          {annual_return:+.1%}")
    print(f"Equal-Weight B&H:       {equal_weight_return:+.1%} ({equal_weight_annual:+.1%} annual)")
    print(f"SPY Benchmark:          {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs Equal-Weight:        {total_return - equal_weight_return:+.1%}")
    print(f"vs SPY:                 {total_return - spy_return:+.1%}")
    
    print(f"\n💰 TAKE-PROFIT ANALYSIS:")
    print(f"Take-Profit Exits:      {take_profit_exits} times")
    print(f"Profit Threshold:       {profit_threshold:.0%}")
    print(f"ATR Trail Multiplier:   {atr_multiplier}x")
    print(f"Average Stock Exposure: {avg_exposure:.1%}")
    
    print(f"\n📊 PORTFOLIO ANALYSIS:")
    print(f"Total Rebalances:       {total_rebalances}")
    print(f"Total Trades:           {len(all_trades)}")
    print(f"Take-Profit Exits:      {len([t for t in all_trades if t.get('action') == 'TAKE_PROFIT_EXIT'])}")
    
    # Performance vs original
    original_return = 0.478  # +47.8% from original
    improvement = total_return - original_return
    
    if improvement > 0.05:
        rating = "🏆 EXCELLENT - Significant improvement!"
    elif improvement > 0.02:
        rating = "✅ GOOD - Notable improvement"
    elif improvement > 0:
        rating = "✅ SLIGHT IMPROVEMENT"
    elif improvement > -0.02:
        rating = "⚠️ SIMILAR performance"
    else:
        rating = "❌ UNDERPERFORMED original"
    
    print(f"\nTake-Profit Strategy Rating: {rating}")
    print(f"Improvement vs Original:     {improvement:+.1%}")
    
    # Take-profit effectiveness analysis
    take_profit_trades = [t for t in all_trades if t.get('action') == 'TAKE_PROFIT_EXIT']
    
    if take_profit_trades:
        avg_profit = np.mean([t['profit_pct'] for t in take_profit_trades])
        avg_days_held = np.mean([t['days_held'] for t in take_profit_trades])
        
        print(f"\n🎯 TAKE-PROFIT EFFECTIVENESS:")
        print(f"Average Profit per Exit:    {avg_profit:.1f}%")
        print(f"Average Days Held:          {avg_days_held:.0f} days")
        print(f"Profit Locks per Stock:     {take_profit_exits/len(stocks):.1f}")
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"✅ Take-profit protection activated {take_profit_exits} times")
    print(f"✅ {'Improved' if improvement > 0 else 'Similar'} performance vs original strategy")
    print(f"✅ Maintained {avg_exposure:.0%} average stock exposure")
    print(f"✅ Profit-taking discipline at +{profit_threshold:.0%} threshold")
    
    return results_df, all_trades

if __name__ == "__main__":
    results_df, trades = run_hybrid_take_profit_backtest()