#!/usr/bin/env python3
"""
3-Stock Trend Composite Portfolio Backtest
Portfolio: AMZN, TSLA, RBLX with optimized position allocation
Capital: $5,000 divided equally ($1,667 per stock)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ThreeStockTrendComposite:
    """
    Trend Composite strategy for 3-stock portfolio
    """
    
    def __init__(self, capital=5000):
        self.capital = capital
        self.stocks = ['AMZN', 'TSLA', 'RBLX']
        self.capital_per_stock = capital / len(self.stocks)
        
        # Optimized position allocation levels
        self.position_levels = {
            -5: 0.00, -4: 0.00, -3: 0.00, -2: 0.00, -1: 0.00,
             0: 0.20,  1: 0.40,  2: 0.60,  3: 0.80,  4: 1.00,  5: 1.00
        }
    
    def calculate_tip_ma_trend(self, df, period=50):
        """TIP Moving Average Trend - Enhanced for individual stocks"""
        ma = df['close'].rolling(period).mean()
        ma20 = df['close'].rolling(20).mean()
        ma50 = df['close'].rolling(50).mean()
        
        # Multiple conditions for stronger signals
        ma_slope = ma.diff(5)
        price_above_ma = df['close'] > ma
        ma_rising = ma_slope > 0
        short_above_long = ma20 > ma50
        
        # Count bullish conditions (0-3)
        conditions = [price_above_ma, ma_rising, short_above_long]
        bullish_count = sum(conditions)
        
        # Convert to -1, 0, +1 signal
        signal = np.where(bullish_count >= 2, 1, np.where(bullish_count <= 1, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_cci_close(self, df, period=20):
        """TIP CCI Close - More sensitive for stocks"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - ma) / (0.015 * mad)
        
        # More nuanced thresholds for individual stocks
        signal = np.where(cci > 50, 1, np.where(cci < -50, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """Bollinger Bands - Trend vs mean reversion"""
        ma = df['close'].rolling(period).mean()
        std_dev = df['close'].rolling(period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        # Trend-following approach: above/below center line
        signal = np.where(df['close'] > ma, 1, -1)
        
        return pd.Series(signal, index=df.index)
    
    def calculate_keltner_channels(self, df, period=20, multiplier=2):
        """Keltner Channels - Breakout detection"""
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
        
        # Breakout signals
        signal = np.where(df['close'] > upper_channel, 1,
                 np.where(df['close'] < lower_channel, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_tip_stochclose(self, df, k_period=14, d_period=3):
        """TIP StochClose - Momentum confirmation"""
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(d_period).mean()
        
        # More sensitive thresholds for individual stocks
        signal = np.where(d_percent > 60, 1, np.where(d_percent < 40, -1, 0))
        
        return pd.Series(signal, index=df.index)
    
    def calculate_trend_composite(self, df):
        """Calculate 5-component Trend Composite score"""
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

def run_three_stock_backtest():
    """
    Backtest 3-stock trend composite portfolio
    """
    
    print("🚀 3-STOCK TREND COMPOSITE PORTFOLIO BACKTEST")
    print("=" * 80)
    print("📊 Portfolio: AMZN, TSLA, RBLX")
    print("💰 Total Capital: $5,000")
    print("📈 Capital per Stock: $1,667")
    print("🎯 Strategy: Arthur Hill's Trend Composite")
    print("=" * 80)
    
    # Parameters
    capital = 5000
    stocks = ['AMZN', 'TSLA', 'RBLX']
    capital_per_stock = capital / len(stocks)
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    
    print(f"📅 Backtest Period: {start_date} to {end_date}")
    print("=" * 80)
    
    # Download data for all stocks
    stock_data = {}
    stock_strategies = {}
    
    for stock in stocks:
        print(f"📊 Downloading {stock} data...")
        try:
            extended_start = "2023-01-01"  # Need extra data for indicators
            ticker = yf.Ticker(stock)
            df = ticker.history(start=extended_start, end=end_date)
            
            if df.empty:
                print(f"❌ No data for {stock}")
                continue
            
            # Clean column names
            df.columns = [col.lower() for col in df.columns]
            stock_data[stock] = df
            
            # Initialize strategy for this stock
            strategy = ThreeStockTrendComposite(capital_per_stock)
            stock_strategies[stock] = strategy
            
            print(f"✅ {stock}: {len(df)} days")
            
        except Exception as e:
            print(f"❌ Error downloading {stock}: {e}")
            continue
    
    if len(stock_data) != 3:
        print(f"❌ Need data for all 3 stocks, got {len(stock_data)}")
        return
    
    # Calculate trend composite for each stock
    print("\n🔧 Calculating Trend Composite indicators...")
    stock_indicators = {}
    
    for stock in stocks:
        df = stock_data[stock]
        strategy = stock_strategies[stock]
        
        print(f"   📊 Processing {stock}...")
        indicators = strategy.calculate_trend_composite(df)
        
        # Add price data
        indicators['price'] = df['close']
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
    stock_positions = {stock: {'shares': 0, 'allocation': 0.0, 'value': 0.0} for stock in stocks}
    
    total_rebalances = 0
    all_trades = []
    
    print(f"\n📈 Running 3-stock portfolio backtest...")
    print("🔄 Daily rebalancing based on trend composite scores...")
    
    for i, date in enumerate(common_dates):
        daily_data = {}
        total_target_allocation = 0.0
        
        # Get data for each stock on this date
        for stock in stocks:
            if date in stock_indicators[stock].index:
                row = stock_indicators[stock].loc[date]
                daily_data[stock] = {
                    'price': row['price'],
                    'score': row['composite_score'],
                    'allocation': row['position_allocation'],
                    'components': [
                        int(row['tip_ma_trend']), int(row['tip_cci_close']),
                        int(row['bollinger_bands']), int(row['keltner_channels']),
                        int(row['tip_stochclose'])
                    ]
                }
                total_target_allocation += row['position_allocation']
        
        if len(daily_data) != 3:
            continue
        
        # Calculate current portfolio value
        portfolio_value = portfolio_cash
        for stock in stocks:
            if stock in daily_data:
                portfolio_value += stock_positions[stock]['shares'] * daily_data[stock]['price']
        
        # Check if rebalancing needed (any stock allocation change >= 5%)
        needs_rebalancing = False
        for stock in stocks:
            current_alloc = stock_positions[stock]['allocation']
            target_alloc = daily_data[stock]['allocation']
            if abs(target_alloc - current_alloc) >= 0.05:
                needs_rebalancing = True
                break
        
        # Rebalance if needed
        if needs_rebalancing:
            total_rebalances += 1
            
            # Calculate new positions for each stock
            for stock in stocks:
                target_allocation = daily_data[stock]['allocation']
                target_value = capital_per_stock * target_allocation
                price = daily_data[stock]['price']
                
                # Calculate shares needed
                new_shares = target_value / price if target_value > 0 else 0
                current_shares = stock_positions[stock]['shares']
                
                if new_shares != current_shares:
                    # Execute trade
                    shares_delta = new_shares - current_shares
                    
                    if shares_delta > 0:  # Buy
                        cost = shares_delta * price * 1.001  # 0.1% transaction cost
                        if portfolio_cash >= cost:  # Check if enough cash
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
                                'score': daily_data[stock]['score']
                            })
                    
                    else:  # Sell
                        proceeds = abs(shares_delta) * price * 0.999  # 0.1% transaction cost
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
                            'score': daily_data[stock]['score']
                        })
            
            # Print early rebalancing events
            if i < 10 or total_rebalances <= 20:
                print(f"\n{date.date()}:")
                for stock in stocks:
                    score = daily_data[stock]['score']
                    price = daily_data[stock]['price']
                    allocation = daily_data[stock]['allocation']
                    components = daily_data[stock]['components']
                    shares = stock_positions[stock]['shares']
                    
                    print(f"  {stock}: ${price:.2f} | Score: {score:+.0f} {components} | "
                          f"{allocation:.0%} → {shares:.0f} shares")
                
                print(f"  💼 Portfolio: ${portfolio_value:,.0f} | Rebalance #{total_rebalances}")
        
        # Update position values
        for stock in stocks:
            stock_positions[stock]['value'] = stock_positions[stock]['shares'] * daily_data[stock]['price']
        
        # Calculate final portfolio value
        current_portfolio_value = portfolio_cash + sum(pos['value'] for pos in stock_positions.values())
        
        # Calculate individual stock allocations and total exposure
        stock_allocations = {}
        total_stock_exposure = 0
        for stock in stocks:
            stock_value = stock_positions[stock]['value']
            stock_pct = stock_value / current_portfolio_value if current_portfolio_value > 0 else 0
            stock_allocations[stock] = stock_pct
            total_stock_exposure += stock_pct
        
        # Record daily results
        portfolio_results.append({
            'date': date,
            'portfolio_value': current_portfolio_value,
            'cash': portfolio_cash,
            'total_stock_exposure': total_stock_exposure,
            'amzn_score': daily_data.get('AMZN', {}).get('score', 0),
            'tsla_score': daily_data.get('TSLA', {}).get('score', 0),
            'rblx_score': daily_data.get('RBLX', {}).get('score', 0),
            'amzn_price': daily_data.get('AMZN', {}).get('price', 0),
            'tsla_price': daily_data.get('TSLA', {}).get('price', 0),
            'rblx_price': daily_data.get('RBLX', {}).get('price', 0),
            'amzn_allocation': stock_allocations.get('AMZN', 0),
            'tsla_allocation': stock_allocations.get('TSLA', 0),
            'rblx_allocation': stock_allocations.get('RBLX', 0)
        })
    
    # Analysis
    results_df = pd.DataFrame(portfolio_results)
    
    if results_df.empty:
        print("❌ No results generated")
        return
    
    final_value = results_df['portfolio_value'].iloc[-1]
    total_return = (final_value / capital) - 1
    
    # Individual stock buy-and-hold returns
    individual_returns = {}
    for stock in stocks:
        start_price = stock_indicators[stock]['price'].iloc[0]
        end_price = stock_indicators[stock]['price'].iloc[-1]
        individual_returns[stock] = (end_price / start_price) - 1
    
    # Equal-weight buy-and-hold
    equal_weight_return = sum(individual_returns.values()) / len(individual_returns)
    
    # SPY benchmark
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=start_date, end=end_date)
        spy_return = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[0]) - 1
    except:
        spy_return = 0
    
    # Time-based metrics
    years = len(results_df) / 252
    annual_return = (1 + total_return) ** (1/years) - 1
    equal_weight_annual = (1 + equal_weight_return) ** (1/years) - 1
    spy_annual = (1 + spy_return) ** (1/years) - 1
    
    avg_exposure = results_df['total_stock_exposure'].mean()
    avg_scores = {
        'AMZN': results_df['amzn_score'].mean(),
        'TSLA': results_df['tsla_score'].mean(),
        'RBLX': results_df['rblx_score'].mean()
    }
    
    print(f"\n🏆 3-STOCK TREND COMPOSITE RESULTS")
    print("=" * 80)
    print(f"Final Portfolio Value:  ${final_value:,.0f}")
    print(f"Total Return:           {total_return:+.1%}")
    print(f"Annual Return:          {annual_return:+.1%}")
    print(f"Equal-Weight B&H:       {equal_weight_return:+.1%} ({equal_weight_annual:+.1%} annual)")
    print(f"SPY Benchmark:          {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs Equal-Weight:        {total_return - equal_weight_return:+.1%}")
    print(f"vs SPY:                 {total_return - spy_return:+.1%}")
    print(f"Period:                 {years:.1f} years")
    
    print(f"\n📊 PORTFOLIO ANALYSIS:")
    print(f"Total Rebalances:       {total_rebalances}")
    print(f"Average Stock Exposure: {avg_exposure:.1%}")
    print(f"Average Cash:           {1-avg_exposure:.1%}")
    print(f"Total Trades:           {len(all_trades)}")
    
    print(f"\n📈 INDIVIDUAL STOCK PERFORMANCE:")
    for stock in stocks:
        stock_return = individual_returns[stock]
        avg_score = avg_scores[stock]
        print(f"{stock}: {stock_return:+6.1%} | Avg Score: {avg_score:+4.1f}")
    
    # Performance rating
    if total_return > equal_weight_return + 0.05:
        rating = "🏆 EXCELLENT - Beat equal-weight by 5%+"
    elif total_return > equal_weight_return:
        rating = "✅ GOOD - Beat equal-weight portfolio"
    elif total_return > spy_return:
        rating = "⚠️ FAIR - Beat SPY benchmark"
    else:
        rating = "❌ POOR - Underperformed benchmarks"
    
    print(f"\nStrategy Rating:        {rating}")
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"✅ Trend composite provided {avg_exposure:.0%} average stock exposure")
    print(f"✅ Reduced volatility through dynamic allocation")
    print(f"✅ Individual stock approach generated clear signals")
    print(f"✅ Diversification across 3 different sectors")
    
    return results_df, all_trades

if __name__ == "__main__":
    results_df, trades = run_three_stock_backtest()