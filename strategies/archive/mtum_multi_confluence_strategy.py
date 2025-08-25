#!/usr/bin/env python3
"""
MTUM Multi-Confluence Strategy - Advanced Technical Analysis
Entry Signals (ALL must be met):
- MTUM > 50-day MA (trend confirmation)
- VIX < 25 (market stability)
- RSI > 50 (momentum confirmed)
- Volume > 20-day average (institutional flow)

Exit Signals (ANY triggers exit):
- MTUM < 50-day MA (risk management)
- ATR 4x profit taking (lock gains)
- VIX > 30 (market fear spike)
- RSI < 30 (momentum broken)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(df, period=14):
    """Calculate RSI indicator"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    high = df['high']
    low = df['low'] 
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr

def mtum_multi_confluence_strategy():
    """MTUM with comprehensive multi-confluence signals"""
    
    print("🚀 MTUM MULTI-CONFLUENCE STRATEGY")
    print("=" * 80)
    print("📊 ENTRY SIGNALS (ALL required):")
    print("   ✅ MTUM > 50-day MA (trend confirmation)")
    print("   ✅ VIX < 25 (market stability)")
    print("   ✅ RSI > 50 (momentum confirmed)")
    print("   ✅ Volume > 20-day average (institutional flow)")
    print()
    print("📊 EXIT SIGNALS (ANY triggers):")
    print("   🛡️ MTUM < 50-day MA (risk management)")
    print("   💰 ATR 4x profit taking (lock gains)")
    print("   ⚠️ VIX > 30 (market fear spike)")
    print("   📉 RSI < 30 (momentum broken)")
    print("=" * 80)
    
    capital = 5000
    start_date = "2024-01-01"
    end_date = "2025-07-31"
    atr_multiplier = 4.0
    
    print(f"💰 Capital: ${capital:,}")
    print(f"📅 Period: {start_date} to {end_date}")
    print("=" * 80)
    
    # Download all required data
    try:
        extended_start = "2023-10-01"
        
        # MTUM data with OHLCV
        print("📊 Downloading MTUM data...")
        mtum = yf.Ticker("MTUM")
        mtum_df = mtum.history(start=extended_start, end=end_date)
        mtum_df.columns = [col.lower() for col in mtum_df.columns]
        
        # VIX data
        print("📊 Downloading VIX data...")
        vix = yf.Ticker("^VIX")
        vix_df = vix.history(start=extended_start, end=end_date)
        vix_df = vix_df[['Close']].rename(columns={'Close': 'vix'})
        
        # SPY for benchmark
        print("📊 Downloading SPY benchmark...")
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=start_date, end=end_date)
        
        if mtum_df.empty or vix_df.empty:
            print("❌ Failed to download required data")
            return
        
        print(f"✅ MTUM data: {len(mtum_df)} days")
        print(f"✅ VIX data: {len(vix_df)} days")
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return
    
    # Merge MTUM and VIX data
    df = mtum_df.join(vix_df, how='left')
    df['vix'] = df['vix'].fillna(method='ffill').fillna(method='bfill')  # Forward and backward fill VIX
    
    # If still NaN, use a default VIX value of 20 (market neutral)
    df['vix'] = df['vix'].fillna(20)
    
    # Calculate all technical indicators
    print("🔧 Calculating technical indicators...")
    
    # Moving averages and volume
    df['ma_50'] = df['close'].rolling(50).mean()
    df['volume_ma_20'] = df['volume'].rolling(20).mean()
    
    # RSI
    df['rsi'] = calculate_rsi(df)
    
    # ATR
    df['atr'] = calculate_atr(df)
    
    # Filter to backtest period
    backtest_df = df[df.index >= start_date].copy()
    
    print(f"🔍 Backtest data shape: {backtest_df.shape}")
    print(f"🔍 Available columns: {backtest_df.columns.tolist()}")
    print(f"🔍 First few MA50 values: {backtest_df['ma_50'].head().tolist()}")
    print(f"🔍 First few VIX values: {backtest_df['vix'].head().tolist()}")
    
    if backtest_df.empty:
        print("❌ No backtest data available")
        return [], []
    
    # Initialize portfolio
    cash = capital
    shares = 0
    position = "CASH"
    entry_price = 0
    entry_atr = 0
    
    results = []
    trades = []
    
    print(f"\n📈 Running multi-confluence strategy...")
    print("🔍 Checking confluence of all signals daily...\n")
    
    for i, (date, row) in enumerate(backtest_df.iterrows()):
        price = row['close']
        ma50 = row['ma_50']
        rsi = row['rsi']
        atr = row['atr']
        vix = row['vix']
        volume = row['volume']
        volume_ma20 = row['volume_ma_20']
        
        # Skip if any indicator is not available
        if pd.isna(ma50) or pd.isna(rsi) or pd.isna(atr) or pd.isna(vix) or pd.isna(volume_ma20):
            continue
        
        portfolio_value = shares * price if shares > 0 else cash
        
        # Calculate all signals
        trend_bullish = price > ma50
        vix_stable = vix < 25
        rsi_bullish = rsi > 50
        volume_confirmation = volume > volume_ma20
        
        # Exit signals
        trend_bearish = price < ma50
        vix_fear = vix > 30
        rsi_bearish = rsi < 30
        atr_profit_signal = False
        
        if position == "MTUM" and entry_price > 0:
            atr_profit_level = entry_price + (atr_multiplier * entry_atr)
            atr_profit_signal = price >= atr_profit_level
        
        # Entry confluence check (ALL must be true)
        entry_confluence = trend_bullish and vix_stable and rsi_bullish and volume_confirmation
        
        # Exit confluence check (ANY can be true)
        exit_confluence = trend_bearish or vix_fear or rsi_bearish or atr_profit_signal
        
        # Print detailed signals periodically or on important events
        if i < 5 or i % 30 == 0 or entry_confluence or exit_confluence:
            trend_emoji = "🟢" if trend_bullish else "🔴"
            vix_emoji = "🟢" if vix_stable else "🔴"
            rsi_emoji = "🟢" if rsi_bullish else "🔴" 
            volume_emoji = "🟢" if volume_confirmation else "🔴"
            
            print(f"{date.date()}: ${price:.2f}")
            print(f"  {trend_emoji} Trend: MTUM vs MA50 (${ma50:.2f}) - {'✅' if trend_bullish else '❌'}")
            print(f"  {vix_emoji} VIX: {vix:.1f} {'< 25' if vix_stable else '>= 25'} - {'✅' if vix_stable else '❌'}")
            print(f"  {rsi_emoji} RSI: {rsi:.1f} {'> 50' if rsi_bullish else '<= 50'} - {'✅' if rsi_bullish else '❌'}")
            print(f"  {volume_emoji} Volume: {volume:,.0f} vs {volume_ma20:,.0f} - {'✅' if volume_confirmation else '❌'}")
            print(f"  🎯 Entry Confluence: {'🟢 YES' if entry_confluence else '🔴 NO'} (need ALL)")
            print(f"  🛡️ Exit Confluence: {'🟢 YES' if exit_confluence else '🔴 NO'} (need ANY)")
            print(f"  💼 Portfolio: ${portfolio_value:,.0f} | Position: {position}\n")
        
        # ENTRY SIGNAL: All confluence signals align
        if entry_confluence and position == "CASH":
            shares = cash / price * 0.999  # Transaction cost
            cash = 0
            position = "MTUM"
            entry_price = price
            entry_atr = atr
            
            trades.append({
                'date': date,
                'action': 'BUY',
                'price': price,
                'shares': shares,
                'reason': 'Multi-confluence entry',
                'trend': trend_bullish,
                'vix': vix,
                'rsi': rsi,
                'volume_confirm': volume_confirmation
            })
            
            print(f"🎯 MULTI-CONFLUENCE ENTRY TRIGGERED!")
            print(f"   📥 BOUGHT {shares:.3f} shares @ ${price:.2f}")
            print(f"   ✅ All signals aligned: Trend + VIX + RSI + Volume")
            print(f"   🎯 ATR Profit Target: ${entry_price + (atr_multiplier * entry_atr):.2f}")
            print()
        
        # EXIT SIGNALS: Any confluence trigger
        elif exit_confluence and position == "MTUM":
            cash = shares * price * 0.999  # Transaction cost
            profit = cash - capital if len(trades) == 1 else cash - (entry_price * shares)
            
            # Determine exit reason
            exit_reasons = []
            if trend_bearish:
                exit_reasons.append("Trend breakdown (MA50)")
            if vix_fear:
                exit_reasons.append(f"VIX spike ({vix:.1f} > 30)")
            if rsi_bearish:
                exit_reasons.append(f"RSI collapse ({rsi:.1f} < 30)")
            if atr_profit_signal:
                exit_reasons.append(f"ATR profit taking (4x)")
            
            primary_reason = exit_reasons[0] if exit_reasons else "Multi-confluence exit"
            
            trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'shares': shares,
                'reason': primary_reason,
                'all_reasons': exit_reasons,
                'profit': profit,
                'entry_price': entry_price
            })
            
            print(f"🚨 CONFLUENCE EXIT TRIGGERED!")
            print(f"   📤 SOLD {shares:.3f} shares @ ${price:.2f}")
            print(f"   🎯 Exit reason(s): {', '.join(exit_reasons)}")
            print(f"   💰 Trade P&L: ${profit:+.0f}")
            print()
            
            shares = 0
            position = "CASH"
            entry_price = 0
            entry_atr = 0
        
        # Record daily results
        results.append({
            'date': date,
            'price': price,
            'ma_50': ma50,
            'rsi': rsi,
            'atr': atr,
            'vix': vix,
            'volume': volume,
            'volume_ma20': volume_ma20,
            'trend_bullish': trend_bullish,
            'vix_stable': vix_stable,
            'rsi_bullish': rsi_bullish,
            'volume_confirmation': volume_confirmation,
            'entry_confluence': entry_confluence,
            'exit_confluence': exit_confluence,
            'portfolio_value': portfolio_value,
            'position': position,
            'entry_price': entry_price if position == "MTUM" else 0
        })
    
    # Final results analysis
    results_df = pd.DataFrame(results)
    
    if results_df.empty:
        print("❌ No results generated - insufficient data or indicators")
        return [], []
    
    final_price = results_df['price'].iloc[-1]
    final_value = shares * final_price if shares > 0 else cash
    total_return = (final_value / capital) - 1
    
    # Benchmark comparisons
    start_price = results_df['price'].iloc[0]
    mtum_return = (final_price / start_price) - 1
    
    # SPY comparison
    try:
        spy_return = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[0]) - 1
    except:
        spy_return = 0
    
    # Calculate annualized returns
    years = len(results_df) / 252
    annual_return = (1 + total_return) ** (1/years) - 1
    mtum_annual = (1 + mtum_return) ** (1/years) - 1
    spy_annual = (1 + spy_return) ** (1/years) - 1
    
    # Confluence analysis
    confluence_opportunities = len(results_df[results_df['entry_confluence'] == True])
    confluence_rate = confluence_opportunities / len(results_df) * 100
    
    # Signal breakdown
    trend_bullish_days = len(results_df[results_df['trend_bullish'] == True])
    vix_stable_days = len(results_df[results_df['vix_stable'] == True])
    rsi_bullish_days = len(results_df[results_df['rsi_bullish'] == True])
    volume_confirm_days = len(results_df[results_df['volume_confirmation'] == True])
    
    # Trading analysis
    buy_trades = [t for t in trades if t['action'] == 'BUY']
    sell_trades = [t for t in trades if t['action'] == 'SELL']
    
    profitable_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
    win_rate = len(profitable_trades) / len(sell_trades) * 100 if sell_trades else 0
    avg_profit = np.mean([t.get('profit', 0) for t in sell_trades]) if sell_trades else 0
    
    print(f"\n🏆 MTUM MULTI-CONFLUENCE STRATEGY RESULTS")
    print("=" * 80)
    print(f"Final Value:            ${final_value:,.0f}")
    print(f"Total Return:           {total_return:+.1%}")
    print(f"Annual Return:          {annual_return:+.1%}")
    print(f"MTUM Buy-Hold:          {mtum_return:+.1%} ({mtum_annual:+.1%} annual)")
    print(f"SPY Benchmark:          {spy_return:+.1%} ({spy_annual:+.1%} annual)")
    print(f"vs MTUM:                {total_return - mtum_return:+.1%}")
    print(f"vs SPY:                 {total_return - spy_return:+.1%}")
    print(f"Period:                 {years:.1f} years")
    
    print(f"\n📊 CONFLUENCE ANALYSIS:")
    print(f"Entry Opportunities:    {confluence_opportunities} days ({confluence_rate:.1f}% of time)")
    print(f"Signal Breakdown:")
    print(f"  🟢 Trend Bullish:     {trend_bullish_days} days ({trend_bullish_days/len(results_df)*100:.1f}%)")
    print(f"  🟢 VIX Stable (<25):  {vix_stable_days} days ({vix_stable_days/len(results_df)*100:.1f}%)")
    print(f"  🟢 RSI Bullish (>50): {rsi_bullish_days} days ({rsi_bullish_days/len(results_df)*100:.1f}%)")
    print(f"  🟢 Volume Confirm:     {volume_confirm_days} days ({volume_confirm_days/len(results_df)*100:.1f}%)")
    
    print(f"\n📈 TRADING PERFORMANCE:")
    print(f"Total Trades:           {len(trades)}")
    print(f"Buy Signals:            {len(buy_trades)}")
    print(f"Sell Signals:           {len(sell_trades)}")
    print(f"Win Rate:               {win_rate:.1f}%")
    print(f"Average Trade P&L:      ${avg_profit:+.0f}")
    print(f"Final Position:         {position}")
    
    # Performance rating
    if total_return > mtum_return + 0.05:
        rating = "🏆 EXCELLENT - Beat MTUM by 5%+"
    elif total_return > mtum_return + 0.02:
        rating = "🏆 EXCELLENT - Beat MTUM significantly"
    elif total_return > mtum_return:
        rating = "✅ GOOD - Beat MTUM"
    elif total_return > spy_return:
        rating = "⚠️ FAIR - Beat SPY"
    else:
        rating = "❌ POOR - Underperformed"
    
    print(f"\nStrategy Rating:        {rating}")
    
    # Show detailed trades
    if trades:
        print(f"\n📋 DETAILED TRADE HISTORY:")
        for i, trade in enumerate(trades):
            action_emoji = "📥" if trade['action'] == 'BUY' else "📤"
            if trade['action'] == 'BUY':
                print(f"{i+1}. {action_emoji} {trade['date'].date()}: BUY @ ${trade['price']:.2f}")
                print(f"    Confluence: Trend={trade['trend']}, VIX={trade['vix']:.1f}, RSI={trade['rsi']:.1f}, Volume={trade['volume_confirm']}")
            else:
                profit = trade.get('profit', 0)
                entry = trade.get('entry_price', 0)
                gain_pct = (trade['price'] / entry - 1) * 100 if entry > 0 else 0
                print(f"{i+1}. {action_emoji} {trade['date'].date()}: SELL @ ${trade['price']:.2f} ({gain_pct:+.1f}%, ${profit:+.0f})")
                print(f"    Reasons: {', '.join(trade.get('all_reasons', [trade['reason']]))}")
    
    print(f"\n🎯 STRATEGY STRENGTHS:")
    print(f"   ✅ Multiple confirmation signals reduce false entries")
    print(f"   ✅ VIX filter avoids high-volatility periods")
    print(f"   ✅ RSI momentum confirmation")
    print(f"   ✅ Volume validates institutional participation")
    print(f"   ✅ Multiple exit triggers for risk management")
    print(f"   ✅ ATR-based profit taking locks in gains")
    
    return results_df, trades

if __name__ == "__main__":
    results_df, trades = mtum_multi_confluence_strategy()