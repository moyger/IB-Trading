#!/usr/bin/env python3
"""
Simple Nick Radge Momentum Backtest - Test Version
Monthly rebalancing to top 10 momentum stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def quick_backtest(capital=100000, start_date="2023-01-01", end_date="2024-01-01"):
    """Quick backtest using a smaller universe for testing"""
    
    print(f"🚀 QUICK RADGE MOMENTUM BACKTEST")
    print("=" * 50)
    print(f"💰 Capital: ${capital:,.0f}")
    print(f"📅 Period: {start_date} to {end_date}")
    print("=" * 50)
    
    # Use a smaller test universe (major S&P stocks)
    test_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'NVDA', 'META', 'NFLX', 'AMD', 'CRM',
        'PYPL', 'ADBE', 'INTC', 'CSCO', 'ORCL',
        'V', 'MA', 'JPM', 'JNJ', 'PG',
        'UNH', 'HD', 'BAC', 'DIS', 'KO'
    ]
    
    # Download data for test universe
    print(f"📊 Downloading data for {len(test_symbols)} test stocks...")
    
    # Get extended data for momentum calculation
    extended_start = (pd.to_datetime(start_date) - timedelta(days=400)).strftime('%Y-%m-%d')
    
    data = {}
    for symbol in test_symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=extended_start, end=end_date)
            if not df.empty and len(df) > 300:
                df.columns = [col.lower() for col in df.columns]
                data[symbol] = df
        except:
            continue
    
    # Get SPY for regime filter
    spy = yf.Ticker("SPY").history(start=extended_start, end=end_date)
    spy.columns = [col.lower() for col in spy.columns]
    
    print(f"✅ Got data for {len(data)} stocks")
    
    # Generate monthly rebalancing dates
    rebal_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Convert rebalancing dates to timezone-aware to match yfinance data
    if spy.index.tz is not None:
        rebal_dates = rebal_dates.tz_localize(spy.index.tz)
    
    # Initialize portfolio
    cash = capital
    holdings = {}
    portfolio_values = []
    
    print(f"\n📈 Running backtest for {len(rebal_dates)} months...")
    
    for i, rebal_date in enumerate(rebal_dates):
        print(f"\nMonth {i+1}: {rebal_date.date()}")
        
        # Calculate current portfolio value
        portfolio_value = cash
        for symbol, shares in holdings.items():
            if symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    portfolio_value += shares * current_price
        
        print(f"  Portfolio Value: ${portfolio_value:,.0f}")
        
        # Check SPY regime (200-day MA)
        spy_data = spy[spy.index <= rebal_date]
        if len(spy_data) >= 200:
            current_spy = spy_data['close'].iloc[-1]
            spy_ma200 = spy_data['close'].tail(200).mean()
            bullish = current_spy > spy_ma200
        else:
            bullish = True
        
        if not bullish:
            print("  🔴 Bearish regime - holding cash")
            # Sell all positions
            for symbol in list(holdings.keys()):
                holdings[symbol] = 0
            cash = portfolio_value
            portfolio_values.append(portfolio_value)
            continue
        
        # Calculate momentum scores for all stocks
        momentum_scores = []
        
        for symbol, df in data.items():
            stock_data = df[df.index <= rebal_date]
            
            if len(stock_data) < 273:  # Need 252 + 21 days
                continue
            
            # Apply basic filters
            current_price = stock_data['close'].iloc[-1]
            if current_price < 10:  # Min $10
                continue
                
            # Nick Radge momentum: (Price_now / Price_252_days_ago) - 1
            # With 21-day skip to avoid mean reversion
            price_now = stock_data['close'].iloc[-22]  # Skip 21 days
            price_then = stock_data['close'].iloc[-273]  # 252 days ago from price_now
            
            if price_then > 0:
                momentum = (price_now / price_then) - 1
                momentum_scores.append((symbol, momentum, current_price))
        
        # Sort by momentum and take top 10
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        top_10 = momentum_scores[:10]
        
        print(f"  🎯 Top 5 momentum stocks:")
        for j, (symbol, momentum, price) in enumerate(top_10[:5]):
            print(f"    {j+1}. {symbol}: {momentum:+.2%} @ ${price:.2f}")
        
        if not top_10:
            print("  ❌ No qualifying stocks found")
            portfolio_values.append(portfolio_value)
            continue
        
        # Calculate target allocation
        position_value = portfolio_value / len(top_10)
        
        # Sell positions not in top 10
        target_symbols = {symbol for symbol, _, _ in top_10}
        for symbol in list(holdings.keys()):
            if symbol not in target_symbols and holdings[symbol] > 0:
                # Sell position
                shares = holdings[symbol]
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    sell_price = price_data['close'].iloc[-1]
                    proceeds = shares * sell_price * 0.999  # 0.1% transaction cost
                    cash += proceeds
                    print(f"    📤 Sold {symbol}: {shares} shares @ ${sell_price:.2f}")
                holdings[symbol] = 0
        
        # Buy/adjust positions for top 10
        total_cost = 0
        for symbol, momentum, current_price in top_10:
            target_shares = int(position_value / current_price)
            current_shares = holdings.get(symbol, 0)
            
            if target_shares > current_shares:
                shares_to_buy = target_shares - current_shares
                cost = shares_to_buy * current_price * 1.001  # 0.1% transaction cost
                
                if cost <= cash - total_cost:
                    total_cost += cost
                    holdings[symbol] = target_shares
                    print(f"    📥 Bought {symbol}: {shares_to_buy} shares @ ${current_price:.2f}")
        
        cash -= total_cost
        
        # Record portfolio value
        final_value = cash
        for symbol, shares in holdings.items():
            if shares > 0 and symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    final_value += shares * price_data['close'].iloc[-1]
        
        portfolio_values.append(final_value)
        print(f"  💰 End Value: ${final_value:,.0f} | Cash: ${cash:,.0f}")
    
    # Calculate performance
    if portfolio_values:
        total_return = (portfolio_values[-1] / capital) - 1
        
        # Get SPY benchmark
        spy_start_price = spy[spy.index >= start_date]['close'].iloc[0]
        spy_end_price = spy[spy.index <= end_date]['close'].iloc[-1]
        spy_return = (spy_end_price / spy_start_price) - 1
        
        print(f"\n🏆 RESULTS SUMMARY")
        print("=" * 50)
        print(f"Final Value:    ${portfolio_values[-1]:,.0f}")
        print(f"Total Return:   {total_return:+.2%}")
        print(f"SPY Return:     {spy_return:+.2%}")
        print(f"Excess Return:  {total_return - spy_return:+.2%}")
        print(f"Months:         {len(portfolio_values)}")
        
        if total_return > spy_return:
            print("✅ OUTPERFORMED SPY!")
        else:
            print("❌ Underperformed SPY")
        
        return portfolio_values
    
    return []

if __name__ == "__main__":
    # Test with smaller capital and recent period
    results = quick_backtest(
        capital=100000,
        start_date="2023-01-01", 
        end_date="2024-08-01"
    )