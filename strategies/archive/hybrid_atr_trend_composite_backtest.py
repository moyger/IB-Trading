#!/usr/bin/env python3
"""
Hybrid ATR + Trend Composite Strategy Backtest
Combines our successful trend composite allocation system with Arthur Hill's ATR trailing stops

Strategy:
1. Use trend composite for dynamic allocation (0%, 20%, 40%, 60%, 80%, 100%)
2. Add ATR trailing stops as individual stock protection
3. If stock hits ATR stop → Force allocation to 0%, redistribute capital
4. Re-enter only on new trend composite entry signal
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class HybridATRTrendComposite:
    """
    Hybrid strategy: Trend Composite allocation + ATR trailing stops
    """
    
    def __init__(self, capital=5000, atr_multiplier=4):
        self.capital = capital
        self.stocks = ['AMZN', 'TSLA', 'RBLX']
        self.capital_per_stock = capital / len(self.stocks)
        self.atr_multiplier = atr_multiplier  # 4x ATR(22) - more responsive than Arthur Hill's 5x
        
        # Optimized position allocation levels
        self.position_levels = {
            -5: 0.00, -4: 0.00, -3: 0.00, -2: 0.00, -1: 0.00,
             0: 0.20,  1: 0.40,  2: 0.60,  3: 0.80,  4: 1.00,  5: 1.00
        }
    
    def calculate_atr(self, df, period=22):
        """
        Calculate Average True Range (ATR)
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        
        return atr
    
    def calculate_atr_trailing_stop(self, df, atr_multiplier=4):
        """
        Calculate ATR trailing stop (Arthur Hill method)
        Stop = Current Price - (ATR_multiplier × ATR(22))
        """
        atr = self.calculate_atr(df)
        
        # Initialize trailing stop series
        trailing_stop = pd.Series(index=df.index, dtype=float)
        highest_close = df['close'].iloc[0]
        
        for i in range(len(df)):
            current_close = df['close'].iloc[i]
            current_atr = atr.iloc[i]
            
            # Update highest close since start or last stop reset
            if current_close > highest_close:
                highest_close = current_close
            
            # Calculate trailing stop
            if pd.notna(current_atr):
                new_stop = highest_close - (atr_multiplier * current_atr)
                
                # Trailing stop can only move up, never down
                if i == 0 or pd.isna(trailing_stop.iloc[i-1]):
                    trailing_stop.iloc[i] = new_stop
                else:
                    trailing_stop.iloc[i] = max(trailing_stop.iloc[i-1], new_stop)
                
                # If price breaks below stop, reset highest close
                if current_close <= trailing_stop.iloc[i]:
                    highest_close = current_close
                    trailing_stop.iloc[i] = current_close - (atr_multiplier * current_atr)
        
        return trailing_stop, atr
    
    def calculate_tip_ma_trend(self, df, period=50):
        """TIP Moving Average Trend - Enhanced for individual stocks"""
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
        """TIP CCI Close - More sensitive for stocks"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - ma) / (0.015 * mad)
        
        signal = np.where(cci > 50, 1, np.where(cci < -50, -1, 0))
        return pd.Series(signal, index=df.index)
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """Bollinger Bands - Trend vs mean reversion"""
        ma = df['close'].rolling(period).mean()
        signal = np.where(df['close'] > ma, 1, -1)
        return pd.Series(signal, index=df.index)
    
    def calculate_keltner_channels(self, df, period=20, multiplier=2):
        """Keltner Channels - Breakout detection"""
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
        """TIP StochClose - Momentum confirmation"""
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(d_period).mean()
        
        signal = np.where(d_percent > 60, 1, np.where(d_percent < 40, -1, 0))
        return pd.Series(signal, index=df.index)
    
    def calculate_trend_composite_with_atr(self, df):
        """
        Calculate trend composite + ATR trailing stops
        """
        # Calculate trend composite components
        tip_ma = self.calculate_tip_ma_trend(df)
        tip_cci = self.calculate_tip_cci_close(df)
        bollinger = self.calculate_bollinger_bands(df)
        keltner = self.calculate_keltner_channels(df)
        tip_stoch = self.calculate_tip_stochclose(df)
        
        # Combine into composite score
        composite = tip_ma + tip_cci + bollinger + keltner + tip_stoch
        
        # Calculate ATR trailing stop
        trailing_stop, atr = self.calculate_atr_trailing_stop(df, self.atr_multiplier)
        
        # Calculate base position allocation from trend composite
        base_allocation = composite.map(self.position_levels)
        
        # ATR stop override: if price below stop, force allocation to 0
        atr_stopped = df['close'] <= trailing_stop
        final_allocation = np.where(atr_stopped, 0.0, base_allocation)
        
        return pd.DataFrame({
            'price': df['close'],
            'tip_ma_trend': tip_ma,
            'tip_cci_close': tip_cci,
            'bollinger_bands': bollinger,
            'keltner_channels': keltner,
            'tip_stochclose': tip_stoch,
            'composite_score': composite,
            'base_allocation': base_allocation,
            'atr': atr,
            'atr_trailing_stop': trailing_stop,
            'atr_stopped': atr_stopped,
            'final_allocation': final_allocation
        })

def run_hybrid_atr_backtest():
    """
    Backtest hybrid ATR + Trend Composite strategy
    """
    
    print("🚀 HYBRID ATR + TREND COMPOSITE STRATEGY BACKTEST")
    print("=" * 80)
    print("📊 Portfolio: AMZN, TSLA, RBLX")
    print("💰 Capital: $5,000")
    print("🎯 Strategy: Trend Composite allocation + ATR trailing stops")
    print("🛡️ ATR Setup: 4x ATR(22) trailing stops")
    print("=" * 80)
    
    # Parameters
    capital = 5000
    stocks = ['AMZN', 'TSLA', 'RBLX']
    capital_per_stock = capital / len(stocks)
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    
    print(f"📅 Period: {start_date} to {end_date}")
    print("🔧 ATR Stop Rule: If price < ATR stop → Force allocation to 0%")
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
            
            strategy = HybridATRTrendComposite(capital_per_stock)
            stock_strategies[stock] = strategy
            
            print(f"✅ {stock}: {len(df)} days")
            
        except Exception as e:
            print(f"❌ Error downloading {stock}: {e}")
            continue
    
    if len(stock_data) != 3:
        print(f"❌ Need data for all 3 stocks, got {len(stock_data)}")
        return
    
    # Calculate hybrid indicators for each stock
    print("\n🔧 Calculating Hybrid ATR + Trend Composite indicators...")
    stock_indicators = {}
    
    for stock in stocks:
        df = stock_data[stock]
        strategy = stock_strategies[stock]
        
        print(f"   📊 Processing {stock} (Trend Composite + ATR stops)...")
        indicators = strategy.calculate_trend_composite_with_atr(df)
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
    
    # Initialize portfolio tracking
    portfolio_results = []
    portfolio_cash = capital
    stock_positions = {stock: {'shares': 0, 'allocation': 0.0, 'value': 0.0, 'atr_stopped': False} for stock in stocks}
    
    total_rebalances = 0
    atr_stops_triggered = 0
    all_trades = []
    
    print(f"\n📈 Running Hybrid ATR + Trend Composite backtest...")
    print("🔄 Dynamic allocation + ATR stop protection...")
    
    for i, date in enumerate(common_dates):
        daily_data = {}
        
        # Get data for each stock on this date
        for stock in stocks:
            if date in stock_indicators[stock].index:
                row = stock_indicators[stock].loc[date]
                daily_data[stock] = {
                    'price': row['price'],
                    'base_score': row['composite_score'],
                    'base_allocation': row['base_allocation'],
                    'atr_stop': row['atr_trailing_stop'],
                    'atr_stopped': row['atr_stopped'],
                    'final_allocation': row['final_allocation'],
                    'atr': row['atr']
                }
        
        if len(daily_data) != 3:
            continue
        
        # Calculate current portfolio value
        portfolio_value = portfolio_cash
        for stock in stocks:
            if stock in daily_data:
                portfolio_value += stock_positions[stock]['shares'] * daily_data[stock]['price']
        
        # Check for ATR stops and rebalancing needs
        needs_rebalancing = False
        atr_stops_today = 0
        
        for stock in stocks:
            current_alloc = stock_positions[stock]['allocation']
            target_alloc = daily_data[stock]['final_allocation']
            
            # Check if ATR stop triggered
            if daily_data[stock]['atr_stopped'] and not stock_positions[stock]['atr_stopped']:
                atr_stops_triggered += 1
                atr_stops_today += 1
                stock_positions[stock]['atr_stopped'] = True
                needs_rebalancing = True
                
                all_trades.append({
                    'date': date,
                    'stock': stock,
                    'action': 'ATR_STOP',
                    'price': daily_data[stock]['price'],
                    'stop_price': daily_data[stock]['atr_stop'],
                    'shares': stock_positions[stock]['shares'],
                    'reason': 'ATR trailing stop triggered'
                })
            
            # Reset ATR stop flag if price moves back above stop
            if not daily_data[stock]['atr_stopped']:
                stock_positions[stock]['atr_stopped'] = False
            
            # Check if allocation change needed
            if abs(target_alloc - current_alloc) >= 0.05:
                needs_rebalancing = True
        
        # Rebalance if needed
        if needs_rebalancing:
            total_rebalances += 1
            
            # Calculate total available allocation (sum of final allocations)
            total_target_allocation = sum(daily_data[stock]['final_allocation'] for stock in stocks)
            
            # Redistribute capital among non-stopped stocks
            if total_target_allocation > 0:
                for stock in stocks:
                    target_allocation = daily_data[stock]['final_allocation']
                    
                    # If stock is ATR stopped, force to 0%
                    if daily_data[stock]['atr_stopped']:
                        target_allocation = 0.0
                    else:
                        # Redistribute capital from stopped stocks
                        # Each non-stopped stock gets proportionally more capital
                        non_stopped_stocks = [s for s in stocks if not daily_data[s]['atr_stopped']]
                        if len(non_stopped_stocks) > 0:
                            redistribution_factor = 3.0 / len(non_stopped_stocks)  # Total capital / active stocks
                            target_allocation = min(1.0, target_allocation * redistribution_factor)
                    
                    target_value = capital_per_stock * target_allocation
                    price = daily_data[stock]['price']
                    new_shares = target_value / price if target_value > 0 else 0
                    current_shares = stock_positions[stock]['shares']
                    
                    if abs(new_shares - current_shares) > 0.1:  # Minimum trade threshold
                        shares_delta = new_shares - current_shares
                        
                        if shares_delta > 0:  # Buy
                            cost = shares_delta * price * 1.001
                            if portfolio_cash >= cost:
                                portfolio_cash -= cost
                                stock_positions[stock]['shares'] = new_shares
                                stock_positions[stock]['allocation'] = target_allocation
                                
                                all_trades.append({
                                    'date': date,
                                    'stock': stock,
                                    'action': 'BUY',
                                    'shares': shares_delta,
                                    'price': price,
                                    'allocation': target_allocation,
                                    'score': daily_data[stock]['base_score']
                                })
                        
                        else:  # Sell
                            proceeds = abs(shares_delta) * price * 0.999
                            portfolio_cash += proceeds
                            stock_positions[stock]['shares'] = new_shares
                            stock_positions[stock]['allocation'] = target_allocation
                            
                            all_trades.append({
                                'date': date,
                                'stock': stock,
                                'action': 'SELL',
                                'shares': abs(shares_delta),
                                'price': price,
                                'allocation': target_allocation,
                                'score': daily_data[stock]['base_score']
                            })
            
            # Print key events
            if i < 10 or total_rebalances <= 20 or atr_stops_today > 0:
                print(f"\n{date.date()}:")
                for stock in stocks:
                    price = daily_data[stock]['price']
                    score = daily_data[stock]['base_score']
                    allocation = daily_data[stock]['final_allocation']
                    atr_stop = daily_data[stock]['atr_stop']
                    shares = stock_positions[stock]['shares']
                    stopped = daily_data[stock]['atr_stopped']
                    
                    stop_status = "🛑 ATR STOPPED" if stopped else f"ATR: ${atr_stop:.2f}"
                    
                    print(f"  {stock}: ${price:.2f} | Score: {score:+.0f} | "
                          f"{allocation:.0%} → {shares:.0f} shares | {stop_status}")
                
                if atr_stops_today > 0:
                    print(f"  🚨 {atr_stops_today} ATR stop(s) triggered today!")
                
                portfolio_value_current = portfolio_cash + sum(stock_positions[s]['shares'] * daily_data[s]['price'] for s in stocks)
                print(f"  💼 Portfolio: ${portfolio_value_current:,.0f} | Rebalance #{total_rebalances}")
        
        # Update position values
        for stock in stocks:
            stock_positions[stock]['value'] = stock_positions[stock]['shares'] * daily_data[stock]['price']
        
        # Record daily results
        current_portfolio_value = portfolio_cash + sum(pos['value'] for pos in stock_positions.values())
        total_stock_exposure = sum(stock_positions[stock]['value'] for stock in stocks) / current_portfolio_value if current_portfolio_value > 0 else 0
        
        portfolio_results.append({
            'date': date,
            'portfolio_value': current_portfolio_value,
            'cash': portfolio_cash,
            'total_stock_exposure': total_stock_exposure,
            'amzn_allocation': stock_positions['AMZN']['allocation'],
            'tsla_allocation': stock_positions['TSLA']['allocation'],
            'rblx_allocation': stock_positions['RBLX']['allocation'],
            'amzn_stopped': daily_data['AMZN']['atr_stopped'],
            'tsla_stopped': daily_data['TSLA']['atr_stopped'],
            'rblx_stopped': daily_data['RBLX']['atr_stopped']
        })
    
    # Final analysis
    results_df = pd.DataFrame(portfolio_results)
    
    if results_df.empty:
        print("❌ No results generated")
        return None, None
    
    final_value = results_df['portfolio_value'].iloc[-1]
    total_return = (final_value / capital) - 1
    
    # Individual stock returns for comparison
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
    
    # ATR stop analysis
    total_days = len(results_df)
    days_with_stops = (results_df['amzn_stopped'] | results_df['tsla_stopped'] | results_df['rblx_stopped']).sum()
    
    print(f"\n🏆 HYBRID ATR + TREND COMPOSITE RESULTS")
    print("=" * 80)
    print(f"Final Portfolio Value:  ${final_value:,.0f}")
    print(f"Total Return:           {total_return:+.1%}")
    print(f"Annual Return:          {annual_return:+.1%}")
    print(f"Equal-Weight B&H:       {equal_weight_return:+.1%} ({equal_weight_annual:+.1%} annual)")
    print(f"SPY Benchmark:          {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs Equal-Weight:        {total_return - equal_weight_return:+.1%}")
    print(f"vs SPY:                 {total_return - spy_return:+.1%}")
    
    print(f"\n🛡️ ATR TRAILING STOP ANALYSIS:")
    print(f"ATR Stops Triggered:    {atr_stops_triggered} times")
    print(f"Days with ATR Stops:    {days_with_stops}/{total_days} ({days_with_stops/total_days*100:.1f}%)")
    print(f"Average Stock Exposure: {avg_exposure:.1%}")
    print(f"ATR Multiplier Used:    4x ATR(22)")
    
    print(f"\n📊 PORTFOLIO ANALYSIS:")
    print(f"Total Rebalances:       {total_rebalances}")
    print(f"Total Trades:           {len(all_trades)}")
    print(f"ATR-Triggered Trades:   {len([t for t in all_trades if t.get('action') == 'ATR_STOP'])}")
    
    # Performance rating vs original system
    original_return = 0.478  # +47.8% from original backtest
    improvement = total_return - original_return
    
    if improvement > 0.05:
        rating = "🏆 EXCELLENT - Significant improvement over original"
    elif improvement > 0.02:
        rating = "✅ GOOD - Notable improvement over original"
    elif improvement > 0:
        rating = "✅ SLIGHT IMPROVEMENT over original"
    elif improvement > -0.02:
        rating = "⚠️ SIMILAR performance to original"
    else:
        rating = "❌ UNDERPERFORMED original strategy"
    
    print(f"\nHybrid Strategy Rating: {rating}")
    print(f"Improvement vs Original: {improvement:+.1%}")
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"✅ ATR stops provided {atr_stops_triggered} protective exits")
    print(f"✅ Reduced exposure during {days_with_stops/total_days*100:.0f}% of trading days")
    print(f"✅ Maintained {avg_exposure:.0%} average stock exposure")
    print(f"✅ {'Improved' if improvement > 0 else 'Similar'} performance vs original strategy")
    
    return results_df, all_trades

if __name__ == "__main__":
    results_df, trades = run_hybrid_atr_backtest()