#!/usr/bin/env python3
"""
Nick Radge Momentum Backtest - $5K CONCENTRATED VERSION
Top 3-5 momentum stocks with meaningful position sizes
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def backtest_5k_concentrated(capital=5000, max_positions=3, start_date="2023-01-01", end_date="2024-08-01"):
    """Nick Radge momentum with concentrated positions for small accounts"""
    
    position_size = capital / max_positions  # Equal weight
    
    print(f"🚀 NICK RADGE MOMENTUM BACKTEST - $5K CONCENTRATED")
    print("=" * 70)
    print(f"💰 Starting Capital: ${capital:,.0f}")
    print(f"🎯 Max positions: {max_positions}")
    print(f"💼 Position size: ${position_size:,.0f} each ({100/max_positions:.1f}%)")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"⚠️  Higher concentration = Higher risk/reward")
    print("=" * 70)
    
    # Same universe
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'NVDA', 'META', 'NFLX', 'AMD', 'CRM',
        'PYPL', 'ADBE', 'INTC', 'CSCO', 'ORCL',
        'V', 'MA', 'JPM', 'JNJ', 'PG',
        'UNH', 'HD', 'BAC', 'DIS', 'KO'
    ]
    
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
    
    # Portfolio tracking
    cash = capital
    holdings = {}
    results = []
    
    print(f"\n📈 Running concentrated $5K backtest...")
    
    for i, rebal_date in enumerate(rebal_dates):
        print(f"\n--- Month {i+1}: {rebal_date.date()} ---")
        
        # Calculate portfolio value
        portfolio_value = cash
        for symbol, shares in holdings.items():
            if symbol in data and shares > 0:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    portfolio_value += shares * price_data['close'].iloc[-1]
        
        print(f"💰 Portfolio Value: ${portfolio_value:,.0f}")
        
        # Check regime
        spy_data = spy[spy.index <= rebal_date]
        if len(spy_data) >= 200:
            current_spy = spy_data['close'].iloc[-1]
            spy_ma200 = spy_data['close'].tail(200).mean()
            bullish = current_spy > spy_ma200
            print(f"📊 SPY Regime: {'🟢 Bullish' if bullish else '🔴 Bearish'}")
        else:
            bullish = True
        
        if not bullish:
            print("🔴 Bearish - liquidating to cash")
            for symbol in list(holdings.keys()):
                if holdings[symbol] > 0:
                    shares = holdings[symbol]
                    price_data = data[symbol][data[symbol].index <= rebal_date]
                    if not price_data.empty:
                        proceeds = shares * price_data['close'].iloc[-1] * 0.999
                        cash += proceeds
            holdings = {}
            
            results.append({
                'date': rebal_date,
                'portfolio_value': cash,
                'positions': 0,
                'regime': 'Bearish'
            })
            continue
        
        # Get momentum scores
        momentum_scores = []
        for symbol, df in data.items():
            stock_data = df[df.index <= rebal_date]
            if len(stock_data) < 273:
                continue
            
            current_price = stock_data['close'].iloc[-1]
            if current_price < 10:
                continue
                
            # Volume filter
            avg_volume = stock_data['volume'].tail(50).mean()
            avg_price = stock_data['close'].tail(50).mean()
            if avg_volume * avg_price < 1_000_000:
                continue
            
            # Momentum calculation
            price_now = stock_data['close'].iloc[-22]
            price_then = stock_data['close'].iloc[-273]
            if price_then > 0:
                momentum = (price_now / price_then) - 1
                momentum_scores.append((symbol, momentum, current_price))
        
        # Take top N (concentrated approach)
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        top_stocks = momentum_scores[:max_positions]
        
        if not top_stocks:
            print("❌ No qualifying stocks")
            continue
        
        print(f"🎯 Top {len(top_stocks)} momentum leaders (concentrated):")
        for j, (symbol, momentum, price) in enumerate(top_stocks):
            print(f"   {j+1}. {symbol}: {momentum:+.2%} @ ${price:.2f}")
        
        # CONCENTRATED APPROACH: Meaningful position sizes
        target_position_value = portfolio_value / len(top_stocks)
        target_symbols = {symbol for symbol, _, _ in top_stocks}
        
        print(f"💡 Target per position: ${target_position_value:,.0f}")
        
        # Close unwanted positions
        total_proceeds = 0
        for symbol in list(holdings.keys()):
            if symbol not in target_symbols and holdings[symbol] > 0:
                shares = holdings[symbol]
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    proceeds = shares * price_data['close'].iloc[-1] * 0.999
                    total_proceeds += proceeds
                    print(f"   📤 Sold {symbol}: ${proceeds:.0f}")
                holdings[symbol] = 0
        
        cash += total_proceeds
        
        # Buy concentrated positions
        total_invested = 0
        for symbol, momentum, current_price in top_stocks:
            target_cost = min(target_position_value, cash - total_invested)
            
            if target_cost >= 500:  # Minimum $500 per position
                fractional_shares = target_cost / current_price
                actual_cost = fractional_shares * current_price * 1.001
                
                if actual_cost <= (cash - total_invested):
                    holdings[symbol] = fractional_shares
                    total_invested += actual_cost
                    print(f"   📥 Bought {symbol}: ${actual_cost:.0f}")
        
        cash -= total_invested
        
        # Final calculations
        final_portfolio_value = cash
        active_positions = 0
        for symbol, shares in holdings.items():
            if shares > 0 and symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    final_portfolio_value += shares * price_data['close'].iloc[-1]
                    active_positions += 1
        
        print(f"💰 Final: ${final_portfolio_value:.0f} | Positions: {active_positions}")
        
        results.append({
            'date': rebal_date,
            'portfolio_value': final_portfolio_value,
            'positions': active_positions,
            'regime': 'Bullish'
        })
    
    # Results
    if results:
        final_value = results[-1]['portfolio_value']
        total_return = (final_value / capital) - 1
        
        spy_start = spy[spy.index >= start_date]['close'].iloc[0]
        spy_end = spy[spy.index <= end_date]['close'].iloc[-1]
        spy_return = (spy_end / spy_start) - 1
        
        print(f"\n🏆 $5K CONCENTRATED RESULTS")
        print("=" * 50)
        print(f"💰 Starting: ${capital:,.0f}")
        print(f"💰 Final: ${final_value:,.0f}")
        print(f"📈 Return: {total_return:+.1%}")
        print(f"📊 SPY: {spy_return:+.1%}")
        print(f"🎯 Excess: {total_return - spy_return:+.1%}")
        print(f"💵 Gain: ${final_value - capital:+,.0f}")
        
        if total_return > spy_return:
            print(f"✅ BEAT SPY by {(total_return - spy_return)*100:.1f}%!")
        else:
            print(f"❌ Lost to SPY by {(spy_return - total_return)*100:.1f}%")
        
        return results
    
    return []

if __name__ == "__main__":
    # Test different concentration levels
    print("Testing concentrated approach for $5K account:\n")
    
    # Test with 3 positions (most concentrated)
    backtest_5k_concentrated(
        capital=5000,
        max_positions=3,
        start_date="2023-01-01",
        end_date="2024-08-01"
    )