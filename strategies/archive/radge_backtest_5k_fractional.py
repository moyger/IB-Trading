#!/usr/bin/env python3
"""
Nick Radge Momentum Backtest - $5K with FRACTIONAL SHARES
Realistic implementation using fractional share capability
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def backtest_5k_fractional(capital=5000, start_date="2023-01-01", end_date="2024-08-01"):
    """Nick Radge backtest with $5K using fractional shares"""
    
    print(f"🚀 NICK RADGE MOMENTUM BACKTEST - $5K WITH FRACTIONAL SHARES")
    print("=" * 70)
    print(f"💰 Starting Capital: ${capital:,.0f}")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"🎯 Strategy: Top 10 momentum, equal weight")
    print(f"📊 Fractional Shares: ✅ ENABLED (like Schwab, Fidelity, M1)")
    print("=" * 70)
    
    # Same universe as $100K test - can now access ALL stocks with fractional shares
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'NVDA', 'META', 'NFLX', 'AMD', 'CRM',
        'PYPL', 'ADBE', 'INTC', 'CSCO', 'ORCL',
        'V', 'MA', 'JPM', 'JNJ', 'PG',
        'UNH', 'HD', 'BAC', 'DIS', 'KO'
    ]
    
    print(f"📊 Universe: {len(symbols)} major S&P 500 stocks")
    
    # Download data
    extended_start = (pd.to_datetime(start_date) - timedelta(days=400)).strftime('%Y-%m-%d')
    
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=extended_start, end=end_date)
            if not df.empty and len(df) > 300:
                df.columns = [col.lower() for col in df.columns]
                data[symbol] = df
        except:
            continue
    
    # SPY for regime
    spy = yf.Ticker("SPY").history(start=extended_start, end=end_date)
    spy.columns = [col.lower() for col in spy.columns]
    
    print(f"✅ Data loaded for {len(data)} stocks")
    
    # Monthly rebalancing
    rebal_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    if spy.index.tz is not None:
        rebal_dates = rebal_dates.tz_localize(spy.index.tz)
    
    # Portfolio tracking - using fractional shares
    cash = capital
    holdings = {}  # {symbol: fractional_shares}
    results = []
    
    print(f"\n📈 Running $5K fractional shares backtest...")
    
    for i, rebal_date in enumerate(rebal_dates):
        print(f"\n--- Month {i+1}: {rebal_date.date()} ---")
        
        # Calculate current portfolio value
        portfolio_value = cash
        for symbol, shares in holdings.items():
            if symbol in data and shares > 0:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    portfolio_value += shares * current_price
        
        print(f"💰 Portfolio Value: ${portfolio_value:,.0f}")
        
        # Check SPY regime
        spy_data = spy[spy.index <= rebal_date]
        if len(spy_data) >= 200:
            current_spy = spy_data['close'].iloc[-1]
            spy_ma200 = spy_data['close'].tail(200).mean()
            bullish = current_spy > spy_ma200
            regime_pct = ((current_spy / spy_ma200) - 1) * 100
            print(f"📊 SPY Regime: {'🟢 Bullish' if bullish else '🔴 Bearish'} ({regime_pct:+.1f}%)")
        else:
            bullish = True
        
        if not bullish:
            print("🔴 Bearish regime - liquidating to cash")
            # Sell all positions (fractional shares = exact proceeds)
            for symbol, shares in holdings.items():
                if shares > 0 and symbol in data:
                    price_data = data[symbol][data[symbol].index <= rebal_date]
                    if not price_data.empty:
                        sell_price = price_data['close'].iloc[-1]
                        proceeds = shares * sell_price * 0.999  # 0.1% transaction cost
                        cash += proceeds
            holdings = {}
            cash = portfolio_value * 0.999  # Small transaction cost for liquidation
            
            results.append({
                'date': rebal_date,
                'portfolio_value': cash,
                'cash': cash,
                'positions': 0,
                'regime': 'Bearish'
            })
            continue
        
        # Calculate momentum scores (same as $100K version)
        momentum_scores = []
        
        for symbol, df in data.items():
            stock_data = df[df.index <= rebal_date]
            
            if len(stock_data) < 273:  # Need 252 + 21 days
                continue
            
            # Basic filters
            current_price = stock_data['close'].iloc[-1]
            if current_price < 10:  # Min $10 (Nick Radge filter)
                continue
                
            # Volume filter
            avg_volume_50d = stock_data['volume'].tail(50).mean()
            avg_price_50d = stock_data['close'].tail(50).mean()
            dollar_volume = avg_volume_50d * avg_price_50d
            if dollar_volume < 1_000_000:  # Min $1M daily volume
                continue
            
            # Nick Radge momentum: (Price_now / Price_252_days_ago) - 1
            price_now = stock_data['close'].iloc[-22]  # Skip 21 days
            price_then = stock_data['close'].iloc[-273]  # 252 days ago
            
            if price_then > 0:
                momentum = (price_now / price_then) - 1
                momentum_scores.append((symbol, momentum, current_price))
        
        # Sort by momentum and take top 10 (exactly like $100K version)
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        top_10 = momentum_scores[:10]
        
        if not top_10:
            print("❌ No qualifying momentum stocks")
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'positions': 0,
                'regime': 'No Stocks'
            })
            continue
        
        print(f"🎯 Top 10 momentum stocks (with fractional shares):")
        for j, (symbol, momentum, price) in enumerate(top_10[:5]):  # Show top 5
            print(f"   {j+1}. {symbol}: {momentum:+.2%} @ ${price:.2f}")
        
        # FRACTIONAL SHARES: Equal weight regardless of stock price!
        target_position_value = portfolio_value / len(top_10)  # $500 per position with $5K
        target_symbols = {symbol for symbol, _, _ in top_10}
        
        print(f"💡 Target per position: ${target_position_value:.0f} (fractional shares enabled)")
        
        # Close positions not in top 10
        total_proceeds = 0
        for symbol in list(holdings.keys()):
            if symbol not in target_symbols and holdings[symbol] > 0:
                shares = holdings[symbol]
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    sell_price = price_data['close'].iloc[-1]
                    proceeds = shares * sell_price * 0.999  # Transaction cost
                    total_proceeds += proceeds
                    print(f"   📤 Sold {symbol}: {shares:.3f} shares @ ${sell_price:.2f} = ${proceeds:.0f}")
                holdings[symbol] = 0
        
        cash += total_proceeds
        
        # Buy fractional shares for top 10 (GAME CHANGER!)
        total_invested = 0
        successful_positions = 0
        
        for symbol, momentum, current_price in top_10:
            # With fractional shares, we can buy EXACTLY the target dollar amount
            target_cost = target_position_value
            
            if target_cost > 50:  # Minimum $50 position
                # Calculate exact fractional shares needed
                fractional_shares = target_cost / current_price
                actual_cost = fractional_shares * current_price * 1.001  # Transaction cost
                
                if actual_cost <= (cash - total_invested):
                    holdings[symbol] = fractional_shares
                    total_invested += actual_cost
                    successful_positions += 1
                    print(f"   📥 Bought {symbol}: {fractional_shares:.3f} shares @ ${current_price:.2f} = ${actual_cost:.0f}")
        
        cash -= total_invested
        
        # Calculate final portfolio value
        final_value = cash
        active_positions = 0
        total_position_value = 0
        
        for symbol, shares in holdings.items():
            if shares > 0 and symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    position_value = shares * price_data['close'].iloc[-1]
                    final_value += position_value
                    total_position_value += position_value
                    active_positions += 1
        
        print(f"💰 Final: ${final_value:.0f} | Cash: ${cash:.0f} | Positions: {active_positions}")
        print(f"📊 Position allocation: ${total_position_value:.0f} ({total_position_value/final_value*100:.1f}%)")
        
        results.append({
            'date': rebal_date,
            'portfolio_value': final_value,
            'cash': cash,
            'positions': active_positions,
            'regime': 'Bullish'
        })
    
    # Performance summary
    if results:
        final_value = results[-1]['portfolio_value']
        total_return = (final_value / capital) - 1
        
        # SPY benchmark
        spy_start = spy[spy.index >= start_date]['close'].iloc[0]
        spy_end = spy[spy.index <= end_date]['close'].iloc[-1]
        spy_return = (spy_end / spy_start) - 1
        
        print(f"\n🏆 $5K FRACTIONAL SHARES RESULTS")
        print("=" * 60)
        print(f"💰 Starting Capital:   ${capital:,.0f}")
        print(f"💰 Final Value:        ${final_value:,.0f}")
        print(f"📈 Total Return:       {total_return:+.1%}")
        print(f"📊 SPY Benchmark:      {spy_return:+.1%}")
        print(f"🎯 Excess Return:      {total_return - spy_return:+.1%}")
        print(f"💵 Dollar Gain:        ${final_value - capital:+,.0f}")
        print(f"📅 Period:             {len(results)} months")
        
        if total_return > spy_return:
            print(f"✅ OUTPERFORMED SPY by {(total_return - spy_return)*100:.1f}%!")
        else:
            print(f"❌ Underperformed SPY by {(spy_return - total_return)*100:.1f}%")
        
        # Fractional shares insights
        print(f"\n💡 FRACTIONAL SHARES ADVANTAGES:")
        print(f"   ✅ Access to ALL momentum leaders (NVDA, GOOGL, etc.)")
        print(f"   ✅ Perfect equal weighting (${final_value/10:.0f} per position)")
        print(f"   ✅ No position size constraints")
        print(f"   ✅ Exact dollar allocation possible")
        
        # Show final positions
        if holdings:
            print(f"\n📋 FINAL POSITIONS (${final_value:,.0f} total):")
            final_rebal_date = rebal_dates[-1]
            sorted_holdings = []
            for symbol, shares in holdings.items():
                if shares > 0 and symbol in data:
                    price_data = data[symbol][data[symbol].index <= final_rebal_date]
                    if not price_data.empty:
                        current_price = price_data['close'].iloc[-1]
                        position_value = shares * current_price
                        sorted_holdings.append((symbol, shares, current_price, position_value))
            
            sorted_holdings.sort(key=lambda x: x[3], reverse=True)
            for symbol, shares, price, value in sorted_holdings:
                print(f"   {symbol}: {shares:.3f} shares @ ${price:.2f} = ${value:.0f} ({value/final_value*100:.1f}%)")
        
        return results
    
    return []

if __name__ == "__main__":
    # Run $5K backtest with FRACTIONAL SHARES - game changer!
    backtest_results = backtest_5k_fractional(
        capital=5000,  # Your actual capital
        start_date="2023-01-01",
        end_date="2024-08-01"
    )