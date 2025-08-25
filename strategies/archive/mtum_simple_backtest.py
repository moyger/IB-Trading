#!/usr/bin/env python3
"""
Simple MTUM ETF Backtest with 50-day MA Filter
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def simple_mtum_backtest():
    """Simple MTUM backtest with 50-day MA filter"""
    
    print("🚀 MTUM ETF + 50-DAY MA FILTER BACKTEST")
    print("=" * 50)
    
    capital = 5000
    start_date = "2024-01-01"  # Your original request
    end_date = "2025-07-31"    # July 2025 as you requested
    
    print(f"💰 Capital: ${capital:,}")
    print(f"📅 Period: {start_date} to {end_date} (1.6 years)")
    
    # Download MTUM data
    try:
        extended_start = "2023-10-01"  # Extra for MA calculation
        mtum = yf.Ticker("MTUM")
        df = mtum.history(start=extended_start, end=end_date)
        
        if df.empty:
            print("❌ No MTUM data available")
            return
            
        print(f"✅ Downloaded MTUM data: {len(df)} days")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Calculate 50-day MA
    df['MA50'] = df['Close'].rolling(50).mean()
    df['Above_MA50'] = df['Close'] > df['MA50']
    
    # Filter to backtest period
    backtest_df = df[df.index >= start_date].copy()
    
    # Initialize
    cash = capital
    shares = 0
    position = "CASH"
    trades = []
    
    print(f"\n📈 Running backtest...")
    
    for date, row in backtest_df.iterrows():
        price = row['Close']
        ma50 = row['MA50']
        above_ma50 = row['Above_MA50']
        
        if pd.isna(ma50):
            continue
        
        # Current value
        portfolio_value = shares * price if shares > 0 else cash
        
        # Entry: Price above MA50 and in cash
        if above_ma50 and position == "CASH":
            shares = cash / price * 0.999  # 0.1% cost
            cash = 0
            position = "MTUM"
            trades.append({
                'date': date,
                'action': 'BUY',
                'price': price,
                'shares': shares
            })
            print(f"📥 {date.date()}: BOUGHT {shares:.3f} shares @ ${price:.2f}")
        
        # Exit: Price below MA50 and holding
        elif not above_ma50 and position == "MTUM":
            cash = shares * price * 0.999  # 0.1% cost
            trades.append({
                'date': date,
                'action': 'SELL', 
                'price': price,
                'shares': shares
            })
            print(f"📤 {date.date()}: SOLD {shares:.3f} shares @ ${price:.2f}")
            shares = 0
            position = "CASH"
    
    # Final results
    final_price = backtest_df['Close'].iloc[-1]
    final_value = shares * final_price if shares > 0 else cash
    total_return = (final_value / capital) - 1
    
    # MTUM buy-and-hold comparison
    start_price = backtest_df['Close'].iloc[0]
    mtum_return = (final_price / start_price) - 1
    
    # Calculate annualized returns
    years = len(backtest_df) / 252  # Trading days per year
    annual_return = (1 + total_return) ** (1/years) - 1
    mtum_annual = (1 + mtum_return) ** (1/years) - 1
    
    # SPY comparison
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=start_date, end=end_date)
        spy_return = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[0]) - 1
        spy_annual = (1 + spy_return) ** (1/years) - 1
    except:
        spy_return = 0
        spy_annual = 0
    
    print(f"\n🏆 MTUM BACKTEST RESULTS (Jan 2024 - Jul 2025)")
    print("=" * 50)
    print(f"Final Value:        ${final_value:,.0f}")
    print(f"Total Return:       {total_return:+.1%}")
    print(f"Annual Return:      {annual_return:+.1%}")
    print(f"MTUM Buy-Hold:      {mtum_return:+.1%} ({mtum_annual:+.1%} annual)")
    print(f"SPY Benchmark:      {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs MTUM:            {total_return - mtum_return:+.1%}")
    print(f"vs SPY:             {total_return - spy_return:+.1%}")
    print(f"Total Trades:       {len(trades)}")
    print(f"Final Position:     {position}")
    print(f"Period:             {years:.1f} years")
    
    # Performance analysis
    if total_return > mtum_return:
        print("✅ BEAT MTUM buy-and-hold!")
        rating = "🏆 EXCELLENT"
    elif total_return > spy_return:
        print("✅ Beat SPY but not MTUM")
        rating = "✅ GOOD"
    elif total_return > 0:
        print("⚠️ Positive but underperformed")
        rating = "⚠️ FAIR"
    else:
        print("❌ Negative returns")
        rating = "❌ POOR"
    
    print(f"Strategy Rating:    {rating}")
    
    # Show key trades
    if len(trades) > 0:
        print(f"\n📋 KEY TRADES SUMMARY:")
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        print(f"   Buy signals: {len(buy_trades)}")
        print(f"   Sell signals: {len(sell_trades)}")
        
        # Show first and last few trades
        print(f"   First trade: {trades[0]['action']} on {trades[0]['date'].date()}")
        if len(trades) > 1:
            print(f"   Last trade:  {trades[-1]['action']} on {trades[-1]['date'].date()}")
    
    return final_value, total_return, mtum_return

if __name__ == "__main__":
    simple_mtum_backtest()