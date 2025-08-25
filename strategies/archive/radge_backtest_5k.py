#!/usr/bin/env python3
"""
Nick Radge Momentum Backtest - $5K Capital Version
Realistic position sizing for smaller account
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def backtest_5k_capital(capital=5000, start_date="2023-01-01", end_date="2024-08-01"):
    """Nick Radge backtest with $5K starting capital"""
    
    print(f"🚀 NICK RADGE MOMENTUM BACKTEST - $5K VERSION")
    print("=" * 60)
    print(f"💰 Starting Capital: ${capital:,.0f}")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"🎯 Strategy: Top 10 momentum, equal weight")
    print("=" * 60)
    
    # Smaller test universe (affordable stocks focus)
    symbols = [
        # Affordable tech leaders ($50-200 range)
        'AMD', 'INTC', 'CSCO', 'CRM', 'ORCL', 'ADBE',
        # Financial sector 
        'JPM', 'BAC', 'V', 'MA', 'C',
        # Consumer/Industrial
        'KO', 'PG', 'JNJ', 'UNH', 'HD', 'DIS',
        # Growth tech (some expensive but fractional shares possible)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NFLX', 'META',
        # Small positions possible
        'NVDA', 'PYPL'
    ]
    
    # Download data
    print(f"📊 Downloading data for {len(symbols)} stocks...")
    
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
    
    # Get SPY for regime
    spy = yf.Ticker("SPY").history(start=extended_start, end=end_date)
    spy.columns = [col.lower() for col in spy.columns]
    
    print(f"✅ Data loaded for {len(data)} stocks")
    
    # Monthly rebalancing dates
    rebal_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    if spy.index.tz is not None:
        rebal_dates = rebal_dates.tz_localize(spy.index.tz)
    
    # Portfolio tracking
    cash = capital
    holdings = {}
    results = []
    
    print(f"\n📈 Running $5K backtest for {len(rebal_dates)} months...")
    
    for i, rebal_date in enumerate(rebal_dates):
        print(f"\n--- Month {i+1}: {rebal_date.date()} ---")
        
        # Calculate current portfolio value
        portfolio_value = cash
        for symbol, shares in holdings.items():
            if symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    portfolio_value += shares * current_price
        
        print(f"💰 Portfolio Value: ${portfolio_value:,.0f}")
        
        # Check regime
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
            for symbol in list(holdings.keys()):
                holdings[symbol] = 0
            cash = portfolio_value
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'positions': 0,
                'regime': 'Bearish'
            })
            continue
        
        # Calculate momentum scores
        momentum_scores = []
        
        for symbol, df in data.items():
            stock_data = df[df.index <= rebal_date]
            
            if len(stock_data) < 273:
                continue
            
            current_price = stock_data['close'].iloc[-1]
            
            # Filters for $5K account
            if current_price < 5:  # Skip penny stocks
                continue
            
            # Volume filter (basic)
            recent_volume = stock_data['volume'].tail(20).mean()
            if recent_volume < 100000:  # Basic liquidity
                continue
                
            # Nick Radge momentum calculation
            price_now = stock_data['close'].iloc[-22]  # Skip 21 days
            price_then = stock_data['close'].iloc[-273]  # 252 days ago
            
            if price_then > 0:
                momentum = (price_now / price_then) - 1
                
                # For $5K account, focus on affordable positions
                min_shares = max(1, int(100 / current_price))  # At least $100 position or 1 share
                if portfolio_value / 10 >= min_shares * current_price:
                    momentum_scores.append((symbol, momentum, current_price))
        
        # Sort and select top momentum stocks
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        
        # For $5K, be more selective - take top 6-8 instead of 10
        max_positions = min(8, max(5, len([s for s in momentum_scores if s[1] > 0])))
        top_stocks = momentum_scores[:max_positions]
        
        if not top_stocks:
            print("❌ No qualifying momentum stocks")
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'positions': 0,
                'regime': 'No Stocks'
            })
            continue
        
        print(f"🎯 Top {len(top_stocks)} momentum stocks for $5K portfolio:")
        for j, (symbol, momentum, price) in enumerate(top_stocks):
            print(f"   {j+1}. {symbol}: {momentum:+.2%} @ ${price:.2f}")
        
        # Position sizing for $5K account
        target_position_value = portfolio_value / len(top_stocks)
        target_symbols = {symbol for symbol, _, _ in top_stocks}
        
        # Close unwanted positions
        for symbol in list(holdings.keys()):
            if symbol not in target_symbols and holdings[symbol] > 0:
                shares = holdings[symbol]
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    sell_price = price_data['close'].iloc[-1]
                    proceeds = shares * sell_price * 0.999  # Transaction cost
                    cash += proceeds
                    print(f"   📤 Sold {symbol}: {shares} shares @ ${sell_price:.2f} = ${proceeds:.0f}")
                holdings[symbol] = 0
        
        # Buy new positions
        successful_buys = []
        total_invested = 0
        
        for symbol, momentum, current_price in top_stocks:
            # Calculate affordable position size
            max_affordable = min(target_position_value, cash - total_invested)
            
            if max_affordable < 50:  # Skip if less than $50 available
                continue
                
            # Calculate shares (minimum 1 share)
            target_shares = max(1, int(max_affordable / current_price))
            actual_cost = target_shares * current_price * 1.001  # Transaction cost
            
            if actual_cost <= (cash - total_invested) and actual_cost >= 50:
                holdings[symbol] = target_shares
                total_invested += actual_cost
                successful_buys.append((symbol, target_shares, current_price, actual_cost))
                print(f"   📥 Bought {symbol}: {target_shares} shares @ ${current_price:.2f} = ${actual_cost:.0f}")
        
        cash -= total_invested
        
        # Calculate final portfolio value
        final_value = cash
        active_positions = 0
        for symbol, shares in holdings.items():
            if shares > 0 and symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    position_value = shares * price_data['close'].iloc[-1]
                    final_value += position_value
                    active_positions += 1
        
        print(f"💰 Final: ${final_value:.0f} | Cash: ${cash:.0f} | Positions: {active_positions}")
        
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
        
        print(f"\n🏆 $5K PORTFOLIO RESULTS")
        print("=" * 50)
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
        
        # Practical insights for $5K account
        print(f"\n💡 $5K ACCOUNT INSIGHTS:")
        avg_positions = np.mean([r['positions'] for r in results if r['positions'] > 0])
        print(f"   Average positions: {avg_positions:.1f}")
        print(f"   Average per position: ${final_value/avg_positions:.0f}")
        print(f"   Final cash buffer: ${results[-1]['cash']:.0f}")
        
        return results
    
    return []

if __name__ == "__main__":
    # Run backtest with YOUR actual $5K capital
    backtest_results = backtest_5k_capital(
        capital=5000,  # Your actual capital
        start_date="2023-01-01",
        end_date="2024-08-01"
    )