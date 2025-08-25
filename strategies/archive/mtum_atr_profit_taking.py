#!/usr/bin/env python3
"""
Enhanced MTUM Strategy: 50-day MA + ATR Profit Taking
Entry: MTUM > 50-day MA
Exit 1: MTUM < 50-day MA (risk management)
Exit 2: ATR profit taking (lock in gains)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    high = df['high']
    low = df['low'] 
    close = df['close']
    
    # True Range calculation
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Average True Range
    atr = true_range.rolling(window=period).mean()
    
    return atr

def mtum_atr_strategy():
    """MTUM with 50-day MA + ATR profit taking strategy"""
    
    print("🚀 ENHANCED MTUM STRATEGY - MA50 + ATR PROFIT TAKING")
    print("=" * 60)
    
    capital = 5000
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    atr_multiplier = 4.0  # ATR multiplier for profit taking
    atr_period = 14      # ATR calculation period
    
    print(f"💰 Capital: ${capital:,}")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"🎯 Entry: MTUM > 50-day MA")
    print(f"🛡️ Exit 1: MTUM < 50-day MA (risk management)")
    print(f"💰 Exit 2: ATR {atr_multiplier}x profit taking")
    print("=" * 60)
    
    # Download MTUM data with OHLC for ATR
    try:
        extended_start = "2023-10-01"
        mtum = yf.Ticker("MTUM")
        df = mtum.history(start=extended_start, end=end_date)
        
        if df.empty:
            print("❌ No MTUM data available")
            return
        
        # Clean column names
        df.columns = [col.lower() for col in df.columns]
        print(f"✅ Downloaded MTUM OHLC data: {len(df)} days")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Calculate technical indicators
    df['ma_50'] = df['close'].rolling(50).mean()
    df['above_ma50'] = df['close'] > df['ma_50']
    df['atr'] = calculate_atr(df, atr_period)
    
    # Filter to backtest period
    backtest_df = df[df.index >= start_date].copy()
    
    # Initialize portfolio
    cash = capital
    shares = 0
    position = "CASH"
    entry_price = 0
    atr_exit_level = 0
    
    results = []
    trades = []
    
    print(f"\n📈 Running enhanced MTUM strategy...")
    
    for i, (date, row) in enumerate(backtest_df.iterrows()):
        price = row['close']
        ma50 = row['ma_50']
        above_ma50 = row['above_ma50']
        atr = row['atr']
        
        if pd.isna(ma50) or pd.isna(atr):
            continue
        
        # Current portfolio value
        portfolio_value = shares * price if shares > 0 else cash
        
        # Signal logic
        ma_bullish = above_ma50
        ma_bearish = not above_ma50
        
        # ATR profit taking logic (only when holding)
        atr_profit_signal = False
        if position == "MTUM" and entry_price > 0:
            # Profit taking when price moves ATR_multiplier * ATR above entry
            atr_profit_level = entry_price + (atr_multiplier * atr)
            atr_profit_signal = price >= atr_profit_level
        
        # Print key signals
        if i < 5 or i % 50 == 0 or atr_profit_signal or (position == "CASH" and ma_bullish) or (position == "MTUM" and ma_bearish):
            regime = "🟢 BULL" if ma_bullish else "🔴 BEAR"
            atr_level = f"ATR: {atr:.2f}" if not pd.isna(atr) else "ATR: N/A"
            print(f"{date.date()}: ${price:.2f} | MA50: ${ma50:.2f} | {regime} | {atr_level} | Portfolio: ${portfolio_value:,.0f}")
        
        # ENTRY SIGNAL: MA bullish and in cash
        if ma_bullish and position == "CASH":
            shares = cash / price * 0.999  # Transaction cost
            cash = 0
            position = "MTUM"
            entry_price = price
            atr_exit_level = entry_price + (atr_multiplier * atr)
            
            trades.append({
                'date': date,
                'action': 'BUY',
                'price': price,
                'shares': shares,
                'reason': 'Above MA50',
                'atr': atr,
                'atr_exit_level': atr_exit_level
            })
            print(f"   📥 BOUGHT {shares:.3f} shares @ ${price:.2f} (Entry: ${entry_price:.2f}, ATR Exit: ${atr_exit_level:.2f})")
        
        # EXIT SIGNAL 1: MA bearish (risk management)
        elif ma_bearish and position == "MTUM":
            cash = shares * price * 0.999  # Transaction cost
            profit = cash - capital if len(trades) == 1 else cash - trades[-2]['price'] * shares if len(trades) > 1 else 0
            
            trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'shares': shares,
                'reason': 'Below MA50 (Risk Mgmt)',
                'profit': profit
            })
            print(f"   📤 SOLD {shares:.3f} shares @ ${price:.2f} - MA50 Risk Management (P&L: ${profit:+.0f})")
            shares = 0
            position = "CASH"
            entry_price = 0
        
        # EXIT SIGNAL 2: ATR profit taking
        elif atr_profit_signal and position == "MTUM":
            cash = shares * price * 0.999  # Transaction cost
            profit = cash - (entry_price * shares)
            
            trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'shares': shares,
                'reason': f'ATR {atr_multiplier}x Profit Taking',
                'profit': profit,
                'entry_price': entry_price
            })
            print(f"   💰 SOLD {shares:.3f} shares @ ${price:.2f} - ATR Profit Taking (Entry: ${entry_price:.2f}, Profit: ${profit:+.0f})")
            shares = 0
            position = "CASH"
            entry_price = 0
        
        # Record daily results
        results.append({
            'date': date,
            'price': price,
            'ma_50': ma50,
            'atr': atr,
            'above_ma50': above_ma50,
            'portfolio_value': portfolio_value,
            'position': position,
            'entry_price': entry_price if position == "MTUM" else 0
        })
    
    # Final results
    results_df = pd.DataFrame(results)
    final_price = results_df['price'].iloc[-1]
    final_value = shares * final_price if shares > 0 else cash
    total_return = (final_value / capital) - 1
    
    # Benchmark comparisons
    start_price = results_df['price'].iloc[0]
    mtum_return = (final_price / start_price) - 1
    
    # SPY comparison
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=start_date, end=end_date)
        spy_return = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[0]) - 1
    except:
        spy_return = 0
    
    # Calculate annualized returns
    years = len(results_df) / 252
    annual_return = (1 + total_return) ** (1/years) - 1
    mtum_annual = (1 + mtum_return) ** (1/years) - 1
    spy_annual = (1 + spy_return) ** (1/years) - 1
    
    # Trading analysis
    buy_trades = [t for t in trades if t['action'] == 'BUY']
    sell_trades = [t for t in trades if t['action'] == 'SELL']
    ma_exits = [t for t in sell_trades if 'MA50' in t['reason']]
    atr_exits = [t for t in sell_trades if 'ATR' in t['reason']]
    
    # Calculate win rate and average profit
    profitable_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
    win_rate = len(profitable_trades) / len(sell_trades) * 100 if sell_trades else 0
    avg_profit = np.mean([t.get('profit', 0) for t in sell_trades]) if sell_trades else 0
    
    print(f"\n🏆 ENHANCED MTUM STRATEGY RESULTS")
    print("=" * 60)
    print(f"Final Value:         ${final_value:,.0f}")
    print(f"Total Return:        {total_return:+.1%}")
    print(f"Annual Return:       {annual_return:+.1%}")
    print(f"MTUM Buy-Hold:       {mtum_return:+.1%} ({mtum_annual:+.1%} annual)")
    print(f"SPY Benchmark:       {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs MTUM:             {total_return - mtum_return:+.1%}")
    print(f"vs SPY:              {total_return - spy_return:+.1%}")
    print(f"Period:              {years:.1f} years")
    
    print(f"\n📊 TRADING ANALYSIS:")
    print(f"Total Trades:        {len(trades)}")
    print(f"Buy Signals:         {len(buy_trades)}")
    print(f"Sell Signals:        {len(sell_trades)}")
    print(f"MA50 Risk Exits:     {len(ma_exits)}")
    print(f"ATR Profit Exits:    {len(atr_exits)}")
    print(f"Win Rate:            {win_rate:.1f}%")
    print(f"Avg Trade P&L:       ${avg_profit:+.0f}")
    print(f"Final Position:      {position}")
    
    # Performance rating
    if total_return > mtum_return + 0.02:
        rating = "🏆 EXCELLENT - Beat MTUM!"
    elif total_return > mtum_return:
        rating = "✅ GOOD - Beat MTUM"
    elif total_return > spy_return:
        rating = "⚠️ FAIR - Beat SPY"
    else:
        rating = "❌ POOR - Underperformed"
    
    print(f"\nStrategy Rating:     {rating}")
    
    # Show ATR profit taking effectiveness
    if atr_exits:
        print(f"\n💰 ATR PROFIT TAKING ANALYSIS:")
        for trade in atr_exits:
            entry = trade.get('entry_price', 0)
            exit_price = trade['price']
            profit = trade.get('profit', 0)
            gain_pct = (exit_price / entry - 1) * 100 if entry > 0 else 0
            print(f"   {trade['date'].date()}: Entry ${entry:.2f} → Exit ${exit_price:.2f} (+{gain_pct:.1f}%, ${profit:+.0f})")
    
    # Suggest other confluences
    print(f"\n🎯 OTHER POTENTIAL CONFLUENCES TO TEST:")
    print(f"   • RSI overbought/oversold (RSI > 70/< 30)")
    print(f"   • Volume confirmation (above average volume)")
    print(f"   • Bollinger Band squeeze/expansion")
    print(f"   • MACD signal line crossovers") 
    print(f"   • Support/resistance levels")
    print(f"   • VIX regime filter (low/high volatility)")
    print(f"   • Sector rotation signals")
    
    return results_df, trades

if __name__ == "__main__":
    results_df, trades = mtum_atr_strategy()