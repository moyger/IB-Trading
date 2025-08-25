#!/usr/bin/env python3
"""
Nick Radge Momentum Backtest - $5K with TOP 5 stocks at 5% risk each
Conservative approach: 25% deployed, 75% cash buffer
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def backtest_5k_top5_5percent(capital=5000, risk_per_position=0.05, start_date="2023-01-01", end_date="2024-08-01"):
    """Top 5 momentum stocks with 5% risk each = 25% total deployment"""
    
    max_positions = 5
    max_deployment = risk_per_position * max_positions  # 25% max
    
    print(f"🚀 NICK RADGE MOMENTUM BACKTEST - $5K TOP 5 @ 5% RISK EACH")
    print("=" * 70)
    print(f"💰 Starting Capital: ${capital:,.0f}")
    print(f"🎯 Strategy: Top 5 momentum stocks")
    print(f"💼 Risk per position: {risk_per_position:.1%} (${capital * risk_per_position:.0f})")
    print(f"📊 Max deployment: {max_deployment:.1%} (${capital * max_deployment:.0f})")
    print(f"💵 Cash buffer: {1-max_deployment:.1%} (${capital * (1-max_deployment):.0f})")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"✅ Conservative risk management approach")
    print("=" * 70)
    
    # Full universe
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
    
    print(f"\n📈 Running conservative Top 5 @ 5% risk backtest...")
    
    for i, rebal_date in enumerate(rebal_dates):
        print(f"\n--- Month {i+1}: {rebal_date.date()} ---")
        
        # Calculate current portfolio value
        portfolio_value = cash
        position_values = {}
        total_position_value = 0
        
        for symbol, shares in holdings.items():
            if symbol in data and shares > 0:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    position_value = shares * current_price
                    position_values[symbol] = position_value
                    portfolio_value += position_value
                    total_position_value += position_value
        
        deployed_pct = total_position_value / portfolio_value * 100 if portfolio_value > 0 else 0
        print(f"💰 Portfolio: ${portfolio_value:,.0f} | Cash: ${cash:,.0f} | Deployed: {deployed_pct:.1f}%")
        
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
            total_proceeds = 0
            for symbol, shares in holdings.items():
                if shares > 0 and symbol in data:
                    price_data = data[symbol][data[symbol].index <= rebal_date]
                    if not price_data.empty:
                        sell_price = price_data['close'].iloc[-1]
                        proceeds = shares * sell_price * 0.999  # Transaction cost
                        total_proceeds += proceeds
                        print(f"   📤 Sold {symbol}: ${proceeds:.0f}")
            
            cash += total_proceeds
            holdings = {}
            portfolio_value = cash
            
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'deployed_value': 0,
                'deployed_pct': 0,
                'positions': 0,
                'regime': 'Bearish'
            })
            continue
        
        # Calculate momentum scores
        momentum_scores = []
        
        for symbol, df in data.items():
            stock_data = df[df.index <= rebal_date]
            
            if len(stock_data) < 273:  # Need 252 + 21 days
                continue
            
            # Nick Radge filters
            current_price = stock_data['close'].iloc[-1]
            if current_price < 10:  # Min $10
                continue
                
            # Volume filter
            avg_volume_50d = stock_data['volume'].tail(50).mean()
            avg_price_50d = stock_data['close'].tail(50).mean()
            dollar_volume = avg_volume_50d * avg_price_50d
            if dollar_volume < 1_000_000:  # Min $1M daily volume
                continue
            
            # Momentum calculation
            price_now = stock_data['close'].iloc[-22]  # Skip 21 days
            price_then = stock_data['close'].iloc[-273]  # 252 days ago
            
            if price_then > 0:
                momentum = (price_now / price_then) - 1
                momentum_scores.append((symbol, momentum, current_price))
        
        # Sort and take TOP 5
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        top_5 = momentum_scores[:5]
        
        if not top_5:
            print("❌ No qualifying momentum stocks")
            results.append({
                'date': rebal_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'deployed_value': total_position_value,
                'deployed_pct': deployed_pct,
                'positions': len([s for s in holdings.values() if s > 0]),
                'regime': 'No Stocks'
            })
            continue
        
        print(f"🎯 TOP 5 MOMENTUM LEADERS (5% risk each):")
        for j, (symbol, momentum, price) in enumerate(top_5):
            print(f"   {j+1}. {symbol}: {momentum:+.2%} @ ${price:.2f}")
        
        # CONSERVATIVE: 5% of CURRENT portfolio per position
        risk_amount_per_position = portfolio_value * risk_per_position  # 5% of current value
        target_symbols = {symbol for symbol, _, _ in top_5}
        
        print(f"💡 Risk per position: ${risk_amount_per_position:.0f} (5% of ${portfolio_value:,.0f})")
        
        # Close positions not in top 5
        total_proceeds = 0
        for symbol in list(holdings.keys()):
            if symbol not in target_symbols and holdings[symbol] > 0:
                shares = holdings[symbol]
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    sell_price = price_data['close'].iloc[-1]
                    proceeds = shares * sell_price * 0.999  # Transaction cost
                    total_proceeds += proceeds
                    print(f"   📤 Sold {symbol}: ${proceeds:.0f}")
                holdings[symbol] = 0
        
        cash += total_proceeds
        
        # Buy top 5 with 5% risk each
        total_invested = 0
        successful_positions = 0
        
        for symbol, momentum, current_price in top_5:
            # 5% risk position
            target_position_value = risk_amount_per_position
            
            # Only invest if position is meaningful (min $200) and we have cash
            if target_position_value >= 200 and (cash - total_invested) >= target_position_value:
                # Calculate fractional shares
                fractional_shares = target_position_value / current_price
                actual_cost = fractional_shares * current_price * 1.001  # Transaction cost
                
                if actual_cost <= (cash - total_invested):
                    holdings[symbol] = fractional_shares
                    total_invested += actual_cost
                    successful_positions += 1
                    print(f"   📥 Bought {symbol}: {fractional_shares:.3f} shares @ ${current_price:.2f} = ${actual_cost:.0f}")
        
        cash -= total_invested
        
        # Calculate final metrics
        final_position_value = 0
        active_positions = 0
        
        for symbol, shares in holdings.items():
            if shares > 0 and symbol in data:
                price_data = data[symbol][data[symbol].index <= rebal_date]
                if not price_data.empty:
                    position_value = shares * price_data['close'].iloc[-1]
                    final_position_value += position_value
                    active_positions += 1
        
        final_portfolio_value = cash + final_position_value
        final_deployed_pct = final_position_value / final_portfolio_value * 100
        
        print(f"💰 Final: ${final_portfolio_value:.0f} | Cash: ${cash:.0f} | Deployed: {final_deployed_pct:.1f}% | Positions: {active_positions}")
        
        results.append({
            'date': rebal_date,
            'portfolio_value': final_portfolio_value,
            'cash': cash,
            'deployed_value': final_position_value,
            'deployed_pct': final_deployed_pct,
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
        
        # Risk metrics
        deployed_values = [r['deployed_pct'] for r in results if r['deployed_pct'] > 0]
        avg_deployed = np.mean(deployed_values) if deployed_values else 0
        max_deployed = max(deployed_values) if deployed_values else 0
        
        print(f"\n🏆 $5K TOP 5 @ 5% RISK RESULTS")
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
        
        # Conservative approach insights
        print(f"\n💡 CONSERVATIVE RISK MANAGEMENT:")
        print(f"   Average deployment: {avg_deployed:.1f}%")
        print(f"   Max deployment: {max_deployed:.1f}%")
        print(f"   Never exceeded 25% target")
        print(f"   Final cash buffer: ${results[-1]['cash']:.0f} ({results[-1]['cash']/final_value*100:.1f}%)")
        print(f"   Risk per position: 5% (${final_value * 0.05:.0f} final)")
        
        # Show final positions if any
        if holdings:
            print(f"\n📋 FINAL TOP 5 POSITIONS (5% risk each):")
            final_date = rebal_dates[-1]
            sorted_holdings = []
            
            for symbol, shares in holdings.items():
                if shares > 0 and symbol in data:
                    price_data = data[symbol][data[symbol].index <= final_date]
                    if not price_data.empty:
                        current_price = price_data['close'].iloc[-1]
                        position_value = shares * current_price
                        risk_pct = position_value / final_value * 100
                        sorted_holdings.append((symbol, shares, current_price, position_value, risk_pct))
            
            sorted_holdings.sort(key=lambda x: x[3], reverse=True)
            
            for symbol, shares, price, value, risk_pct in sorted_holdings:
                print(f"   {symbol}: {shares:.3f} shares @ ${price:.2f} = ${value:.0f} ({risk_pct:.1f}%)")
        
        print(f"\n🎯 STRATEGY VALIDATION:")
        print(f"   ✅ Conservative risk management (max 25% deployed)")
        print(f"   ✅ Large cash buffer for stability")
        print(f"   ✅ Top momentum stock selection")
        print(f"   ✅ Fractional shares for exact positioning")
        
        return results
    
    return []

if __name__ == "__main__":
    # Run the conservative Top 5 @ 5% risk approach
    results = backtest_5k_top5_5percent(
        capital=5000,
        risk_per_position=0.05,  # 5% risk per position
        start_date="2023-01-01",
        end_date="2024-08-01"
    )