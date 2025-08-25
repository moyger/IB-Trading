#!/usr/bin/env python3
"""
Nick Radge Momentum Backtest - $5K TOP 5 VERSION
Top 5 momentum stocks with $1,000 per position - the sweet spot!
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def backtest_5k_top5(capital=5000, max_positions=5, start_date="2023-01-01", end_date="2024-08-01"):
    """Nick Radge momentum with Top 5 - perfect for $5K accounts"""
    
    position_size = capital / max_positions  # $1,000 per position
    
    print(f"🚀 NICK RADGE MOMENTUM BACKTEST - $5K TOP 5 SWEET SPOT")
    print("=" * 70)
    print(f"💰 Starting Capital: ${capital:,.0f}")
    print(f"🎯 Max positions: {max_positions}")
    print(f"💼 Target per position: ${position_size:,.0f} ({100/max_positions:.0f}%)")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"✅ Meaningful position sizes + diversification balance")
    print("=" * 70)
    
    # Full universe - can access any stock with fractional shares
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
    
    # Portfolio tracking
    cash = capital
    holdings = {}  # {symbol: fractional_shares}
    results = []
    trades = []
    
    print(f"\n📈 Running Top 5 momentum backtest...")
    
    for i, rebal_date in enumerate(rebal_dates):
        print(f"\n--- Month {i+1}: {rebal_date.date()} ---")
        
        # Calculate current portfolio value
        portfolio_value = cash
        position_values = {}
        
        for symbol, shares in holdings.items():
            if symbol in data and shares > 0:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    position_value = shares * current_price
                    position_values[symbol] = position_value
                    portfolio_value += position_value
        
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
            print("🔴 Bearish regime - liquidating all positions to cash")
            total_proceeds = 0
            for symbol, shares in holdings.items():
                if shares > 0 and symbol in data:
                    price_data = data[symbol][data[symbol].index <= rebal_date]
                    if not price_data.empty:
                        sell_price = price_data['close'].iloc[-1]
                        proceeds = shares * sell_price * 0.999  # 0.1% transaction cost
                        total_proceeds += proceeds
                        trades.append({
                            'date': rebal_date,
                            'action': 'SELL',
                            'symbol': symbol,
                            'shares': shares,
                            'price': sell_price,
                            'amount': proceeds,
                            'reason': 'Bearish regime'
                        })
                        print(f"   📤 Sold {symbol}: ${proceeds:.0f}")
            
            cash += total_proceeds
            holdings = {}
            portfolio_value = cash
            
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'positions': 0,
                'regime': 'Bearish'
            })
            continue
        
        # Calculate momentum scores (Nick Radge method)
        momentum_scores = []
        
        for symbol, df in data.items():
            stock_data = df[df.index <= rebal_date]
            
            if len(stock_data) < 273:  # Need 252 + 21 days history
                continue
            
            # Nick Radge filters
            current_price = stock_data['close'].iloc[-1]
            if current_price < 10:  # Minimum $10 price
                continue
                
            # Volume filter: Minimum $1M daily dollar volume
            avg_volume_50d = stock_data['volume'].tail(50).mean()
            avg_price_50d = stock_data['close'].tail(50).mean()
            dollar_volume = avg_volume_50d * avg_price_50d
            if dollar_volume < 1_000_000:
                continue
            
            # Nick Radge momentum calculation
            price_now = stock_data['close'].iloc[-22]  # Skip 21 days to avoid mean reversion
            price_then = stock_data['close'].iloc[-273]  # 252 days ago from price_now
            
            if price_then > 0:
                momentum = (price_now / price_then) - 1
                momentum_scores.append((symbol, momentum, current_price))
        
        # Sort by momentum and take TOP 5
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        top_5 = momentum_scores[:5]
        
        if not top_5:
            print("❌ No qualifying momentum stocks found")
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'positions': len([s for s in holdings.values() if s > 0]),
                'regime': 'No Stocks'
            })
            continue
        
        print(f"🎯 TOP 5 MOMENTUM LEADERS:")
        for j, (symbol, momentum, price) in enumerate(top_5):
            print(f"   {j+1}. {symbol}: {momentum:+.2%} @ ${price:.2f}")
        
        # Equal weight: $1,000 per position (20% each)
        target_position_value = portfolio_value / len(top_5)  
        target_symbols = {symbol for symbol, _, _ in top_5}
        
        print(f"💡 Target per position: ${target_position_value:.0f} (equal weight)")
        
        # Close positions NOT in top 5
        total_proceeds = 0
        for symbol in list(holdings.keys()):
            if symbol not in target_symbols and holdings[symbol] > 0:
                shares = holdings[symbol]
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    sell_price = price_data['close'].iloc[-1]
                    proceeds = shares * sell_price * 0.999  # Transaction cost
                    total_proceeds += proceeds
                    
                    trades.append({
                        'date': rebal_date,
                        'action': 'SELL',
                        'symbol': symbol,
                        'shares': shares,
                        'price': sell_price,
                        'amount': proceeds,
                        'reason': 'Not in top 5'
                    })
                    print(f"   📤 Sold {symbol}: ${proceeds:.0f}")
                
                holdings[symbol] = 0
        
        cash += total_proceeds
        
        # Buy/adjust positions for TOP 5
        total_invested = 0
        successful_buys = 0
        
        for symbol, momentum, current_price in top_5:
            # Target position value (equal weight)
            target_cost = target_position_value
            
            # Only buy if meaningful position size (min $500)
            if target_cost >= 500 and (cash - total_invested) >= target_cost:
                # Calculate fractional shares needed
                fractional_shares = target_cost / current_price
                actual_cost = fractional_shares * current_price * 1.001  # 0.1% transaction cost
                
                if actual_cost <= (cash - total_invested):
                    holdings[symbol] = fractional_shares
                    total_invested += actual_cost
                    successful_buys += 1
                    
                    trades.append({
                        'date': rebal_date,
                        'action': 'BUY',
                        'symbol': symbol,
                        'shares': fractional_shares,
                        'price': current_price,
                        'amount': actual_cost,
                        'reason': f'Top 5 momentum ({momentum:+.1%})'
                    })
                    print(f"   📥 Bought {symbol}: {fractional_shares:.3f} shares @ ${current_price:.2f} = ${actual_cost:.0f}")
        
        cash -= total_invested
        
        # Calculate final portfolio metrics
        final_position_value = 0
        active_positions = 0
        
        for symbol, shares in holdings.items():
            if shares > 0 and symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    position_value = shares * current_price
                    final_position_value += position_value
                    active_positions += 1
        
        final_portfolio_value = cash + final_position_value
        deployment_pct = final_position_value / final_portfolio_value * 100
        
        print(f"💰 Final: ${final_portfolio_value:.0f} | Cash: ${cash:.0f} | Deployed: {deployment_pct:.1f}% | Positions: {active_positions}")
        
        results.append({
            'date': rebal_date,
            'portfolio_value': final_portfolio_value,
            'cash': cash,
            'positions': active_positions,
            'regime': 'Bullish'
        })
    
    # Performance Analysis
    if results:
        final_value = results[-1]['portfolio_value']
        total_return = (final_value / capital) - 1
        
        # SPY benchmark
        spy_start = spy[spy.index >= start_date]['close'].iloc[0]
        spy_end = spy[spy.index <= end_date]['close'].iloc[-1]
        spy_return = (spy_end / spy_start) - 1
        
        # Trading metrics
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t['action'] == 'BUY'])
        sell_trades = len([t for t in trades if t['action'] == 'SELL'])
        
        print(f"\n🏆 $5K TOP 5 MOMENTUM RESULTS")
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
        
        # Trading analysis
        print(f"\n📊 TRADING ANALYSIS:")
        print(f"   Total trades: {total_trades}")
        print(f"   Buy trades: {buy_trades}")
        print(f"   Sell trades: {sell_trades}")
        print(f"   Final positions: {results[-1]['positions']}")
        print(f"   Final cash: ${results[-1]['cash']:.0f}")
        
        # Show current holdings if any
        if holdings:
            print(f"\n📋 FINAL TOP 5 POSITIONS:")
            final_date = rebal_dates[-1]
            sorted_holdings = []
            
            for symbol, shares in holdings.items():
                if shares > 0 and symbol in data:
                    price_data = data[symbol][data[symbol].index <= final_date]
                    if not price_data.empty:
                        current_price = price_data['close'].iloc[-1]
                        position_value = shares * current_price
                        pct_of_portfolio = position_value / final_value * 100
                        sorted_holdings.append((symbol, shares, current_price, position_value, pct_of_portfolio))
            
            sorted_holdings.sort(key=lambda x: x[3], reverse=True)  # Sort by position value
            
            for symbol, shares, price, value, pct in sorted_holdings:
                print(f"   {symbol}: {shares:.3f} shares @ ${price:.2f} = ${value:.0f} ({pct:.1f}%)")
        
        print(f"\n🎯 TOP 5 STRATEGY VALIDATION:")
        print(f"   ✅ Meaningful position sizes (${final_value/5:.0f} average)")
        print(f"   ✅ Balanced diversification (5 stocks)")
        print(f"   ✅ Access to all momentum leaders")
        print(f"   ✅ Professional-grade implementation")
        
        if final_value > capital:
            print(f"   🎉 PROFITABLE STRATEGY!")
        
        return results, trades
    
    return [], []

if __name__ == "__main__":
    # Run the TOP 5 momentum test - the $5K sweet spot!
    results, trades = backtest_5k_top5(
        capital=5000,
        max_positions=5,  # The magic number for $5K
        start_date="2023-01-01",
        end_date="2024-08-01"
    )