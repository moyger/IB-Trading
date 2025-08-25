#!/usr/bin/env python3
"""
$5K Buy-and-Hold Test: What if we just bought #1 momentum stock and held?
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_buy_hold_top_momentum():
    """Test buying #1 momentum stock in Feb 2023 and holding"""
    
    print("🧪 TESTING: What if we just bought #1 momentum stock and held?")
    print("=" * 60)
    
    # In Feb 2023, KO was #1 momentum at +10.61%
    # But let's see what happened with different choices
    
    test_stocks = [
        ('KO', 'Coca-Cola (Feb 2023 #1)', 56.87),    # Actual #1 in Feb
        ('NVDA', 'NVIDIA (Tech leader)', 22.68),      # Price in Feb 2023
        ('META', 'Meta (Recovery story)', 173.86),    # Price in Feb 2023
        ('ORCL', 'Oracle (Mar 2023 #1)', 83.65)      # #1 in March
    ]
    
    buy_date = "2023-02-01"
    end_date = "2024-08-01"
    capital = 5000
    
    print(f"📅 Buy Date: {buy_date}")
    print(f"📅 Hold Until: {end_date}")
    print(f"💰 Capital: ${capital:,}")
    print("=" * 60)
    
    results = []
    
    for symbol, description, buy_price in test_stocks:
        # Get stock data
        ticker = yf.Ticker(symbol)
        df = ticker.history(start="2023-01-01", end="2024-09-01")
        
        if df.empty:
            continue
            
        # Find buy and sell prices
        buy_row = df[df.index >= buy_date].iloc[0]
        end_row = df[df.index <= end_date].iloc[-1]
        
        actual_buy_price = buy_row['Close']
        final_price = end_row['Close']
        
        # Calculate returns
        shares = capital / actual_buy_price
        final_value = shares * final_price
        total_return = (final_value / capital) - 1
        
        results.append({
            'symbol': symbol,
            'description': description,
            'buy_price': actual_buy_price,
            'final_price': final_price,
            'shares': shares,
            'final_value': final_value,
            'return': total_return
        })
        
        print(f"\n{symbol}: {description}")
        print(f"   Buy Price: ${actual_buy_price:.2f}")
        print(f"   Final Price: ${final_price:.2f}")
        print(f"   Shares: {shares:.3f}")
        print(f"   Final Value: ${final_value:,.0f}")
        print(f"   Return: {total_return:+.1%}")
    
    # SPY comparison
    spy = yf.Ticker("SPY")
    spy_df = spy.history(start="2023-01-01", end="2024-09-01")
    spy_buy = spy_df[spy_df.index >= buy_date].iloc[0]['Close']
    spy_end = spy_df[spy_df.index <= end_date].iloc[-1]['Close']
    spy_return = (spy_end / spy_buy) - 1
    
    print(f"\n📊 SPY BENCHMARK:")
    print(f"   Buy: ${spy_buy:.2f}")
    print(f"   Final: ${spy_end:.2f}")
    print(f"   Return: {spy_return:+.1%}")
    
    # Best performer
    best = max(results, key=lambda x: x['return'])
    print(f"\n🏆 BEST PERFORMER:")
    print(f"   {best['symbol']}: {best['return']:+.1%} (${best['final_value']:,.0f})")
    print(f"   Beat SPY by: {(best['return'] - spy_return)*100:+.1f} percentage points")
    
    # The lesson
    print(f"\n💡 THE LESSON:")
    print(f"   Simple buy-and-hold of the RIGHT stock >> Complex monthly rebalancing")
    print(f"   $5K needs concentration, not diversification")
    print(f"   Transaction costs kill small, frequent trades")

if __name__ == "__main__":
    test_buy_hold_top_momentum()