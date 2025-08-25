#!/usr/bin/env python3
"""
MTUM ETF Backtest with 50-day MA Filter - $5K
Professional momentum management with tactical risk overlay
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def backtest_mtum_ma50_filter(capital=5000, start_date="2024-01-01", end_date="2024-12-31"):
    """MTUM ETF with 50-day MA regime filter - the smart $5K approach"""
    
    print(f"🚀 MTUM ETF BACKTEST - $5K with 50-DAY MA FILTER")
    print("=" * 70)
    print(f"💰 Starting Capital: ${capital:,.0f}")
    print(f"🎯 Strategy: MTUM ETF (iShares Momentum Factor)")
    print(f"📊 Risk Management: Stay out when MTUM < 50-day MA")
    print(f"💼 Position: Fully invested when bullish")
    print(f"💵 Cash: Hold cash when bearish")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"✅ Professional momentum + Smart risk management")
    print("=" * 70)
    
    # Download MTUM data
    print("📊 Downloading MTUM ETF data...")
    try:
        mtum = yf.Ticker("MTUM")
        # Get extended period for moving average calculation
        extended_start = (pd.to_datetime(start_date) - timedelta(days=100)).strftime('%Y-%m-%d')
        mtum_df = mtum.history(start=extended_start, end=end_date)
        
        if mtum_df.empty:
            print("❌ Failed to download MTUM data")
            return [], []
            
        mtum_df.columns = [col.lower() for col in mtum_df.columns]
        print(f"✅ MTUM data loaded: {len(mtum_df)} days")
        
    except Exception as e:
        print(f"❌ Error downloading MTUM: {e}")
        return [], []
    
    # Download SPY for benchmark
    print("📊 Downloading SPY benchmark...")
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start=extended_start, end=end_date)
        spy_df.columns = [col.lower() for col in spy_df.columns]
        print(f"✅ SPY data loaded: {len(spy_df)} days")
        
    except Exception as e:
        print(f"❌ Error downloading SPY: {e}")
        return [], []
    
    # Calculate 50-day moving average for MTUM
    mtum_df['ma_50'] = mtum_df['close'].rolling(window=50).mean()
    mtum_df['above_ma50'] = mtum_df['close'] > mtum_df['ma_50']
    
    # Filter to backtest period
    backtest_data = mtum_df[mtum_df.index >= start_date].copy()
    
    if backtest_data.empty:
        print(f"❌ No data available for period {start_date} to {end_date}")
        return [], []
    
    print(f"📈 Backtesting period: {len(backtest_data)} days")
    
    # Initialize portfolio
    cash = capital
    mtum_shares = 0
    portfolio_history = []
    trades = []
    
    # Track position status
    current_position = "CASH"  # Start in cash
    
    print(f"\n📈 Running MTUM + 50-day MA filter backtest...")
    print(f"🔄 Checking signals daily...")
    
    for i, (date, row) in enumerate(backtest_data.iterrows()):
        mtum_price = row['close']
        ma_50 = row['ma_50']
        above_ma50 = row['above_ma50']
        
        # Skip if MA not available yet
        if pd.isna(ma_50):
            continue
        
        # Current portfolio value
        if mtum_shares > 0:
            portfolio_value = mtum_shares * mtum_price
            cash_value = 0
        else:
            portfolio_value = cash
            cash_value = cash
        
        # Regime signal
        regime = "🟢 BULLISH" if above_ma50 else "🔴 BEARISH"
        distance_pct = ((mtum_price / ma_50) - 1) * 100
        
        # Print key updates only
        if i < 3 or i % 50 == 0:  # First few days and every 50 days
            print(f"{date.date()}: MTUM ${mtum_price:.2f} | MA50 ${ma_50:.2f} | {regime} ({distance_pct:+.1f}%) | Portfolio ${portfolio_value:,.0f}")
        
        # ENTRY SIGNAL: MTUM above 50-day MA and we're in cash
        if above_ma50 and current_position == "CASH":
            # Buy MTUM with full capital
            mtum_shares = cash / mtum_price * 0.999  # 0.1% transaction cost
            actual_cost = mtum_shares * mtum_price
            cash = 0
            current_position = "MTUM"
            
            trades.append({
                'date': date,
                'action': 'BUY',
                'symbol': 'MTUM',
                'shares': mtum_shares,
                'price': mtum_price,
                'amount': actual_cost,
                'reason': 'Above 50-day MA'
            })
            
            print(f"   📥 BOUGHT MTUM: {mtum_shares:.3f} shares @ ${mtum_price:.2f} = ${actual_cost:,.0f}")
        
        # EXIT SIGNAL: MTUM below 50-day MA and we own MTUM
        elif not above_ma50 and current_position == "MTUM":
            # Sell MTUM and go to cash
            proceeds = mtum_shares * mtum_price * 0.999  # 0.1% transaction cost
            cash = proceeds
            current_position = "CASH"
            
            trades.append({
                'date': date,
                'action': 'SELL',
                'symbol': 'MTUM',
                'shares': mtum_shares,
                'price': mtum_price,
                'amount': proceeds,
                'reason': 'Below 50-day MA'
            })
            
            print(f"   📤 SOLD MTUM: {mtum_shares:.3f} shares @ ${mtum_price:.2f} = ${proceeds:,.0f}")
            mtum_shares = 0
        
        # Record portfolio history
        portfolio_history.append({
            'date': date,
            'mtum_price': mtum_price,
            'ma_50': ma_50,
            'above_ma50': above_ma50,
            'distance_pct': distance_pct,
            'portfolio_value': portfolio_value,
            'cash': cash_value,
            'mtum_shares': mtum_shares,
            'position': current_position
        })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(portfolio_history)
    
    if results_df.empty:
        print("❌ No results generated")
        return [], []
    
    # Performance Analysis
    final_value = results_df['portfolio_value'].iloc[-1]
    total_return = (final_value / capital) - 1
    
    # MTUM buy-and-hold comparison
    mtum_start_price = backtest_data['close'].iloc[0]
    mtum_end_price = backtest_data['close'].iloc[-1]
    mtum_buy_hold_return = (mtum_end_price / mtum_start_price) - 1
    
    # SPY benchmark for same period
    spy_backtest = spy_df[spy_df.index >= start_date]
    if not spy_backtest.empty:
        spy_start = spy_backtest['close'].iloc[0]
        spy_end = spy_backtest['close'].iloc[-1]
        spy_return = (spy_end / spy_start) - 1
    else:
        spy_return = 0
    
    # Trading statistics
    buy_trades = [t for t in trades if t['action'] == 'BUY']
    sell_trades = [t for t in trades if t['action'] == 'SELL']
    
    # Time in market
    days_in_mtum = sum(results_df['position'] == 'MTUM')
    days_in_cash = sum(results_df['position'] == 'CASH')
    time_in_market_pct = days_in_mtum / len(results_df) * 100
    
    # Results
    print(f"\n🏆 MTUM ETF + 50-DAY MA FILTER RESULTS")
    print("=" * 70)
    print(f"💰 Starting Capital:     ${capital:,.0f}")
    print(f"💰 Final Value:          ${final_value:,.0f}")
    print(f"📈 Total Return:         {total_return:+.1%}")
    print(f"📊 MTUM Buy-Hold:        {mtum_buy_hold_return:+.1%}")
    print(f"📊 SPY Benchmark:        {spy_return:+.1%}")
    print(f"🎯 vs MTUM Buy-Hold:     {total_return - mtum_buy_hold_return:+.1%}")
    print(f"🎯 vs SPY:               {total_return - spy_return:+.1%}")
    print(f"💵 Dollar Gain:          ${final_value - capital:+,.0f}")
    print(f"📅 Period:               {len(results_df)} days")
    
    # Risk management effectiveness
    print(f"\n🛡️ RISK MANAGEMENT ANALYSIS:")
    print(f"   Time in MTUM: {time_in_market_pct:.1f}% ({days_in_mtum} days)")
    print(f"   Time in Cash: {100-time_in_market_pct:.1f}% ({days_in_cash} days)")
    print(f"   Total trades: {len(trades)}")
    print(f"   Buy signals: {len(buy_trades)}")
    print(f"   Sell signals: {len(sell_trades)}")
    
    # Performance rating
    if total_return > mtum_buy_hold_return + 0.02:  # Beat MTUM by 2%+
        rating = "🏆 EXCELLENT - Beat buy-and-hold!"
    elif total_return > mtum_buy_hold_return:
        rating = "✅ GOOD - Outperformed MTUM"
    elif total_return > spy_return:
        rating = "⚠️ FAIR - Beat SPY but not MTUM"
    elif total_return > -0.05:  # Less than 5% loss
        rating = "⚠️ OKAY - Limited losses"
    else:
        rating = "❌ POOR - Significant underperformance"
    
    print(f"\n🎖️ STRATEGY RATING: {rating}")
    
    # Show recent trades
    if trades:
        print(f"\n📋 RECENT TRADES:")
        for trade in trades[-5:]:  # Last 5 trades
            action_emoji = "📥" if trade['action'] == 'BUY' else "📤"
            print(f"   {action_emoji} {trade['date'].date()}: {trade['action']} {trade['shares']:.3f} MTUM @ ${trade['price']:.2f} - {trade['reason']}")
    
    # Current position
    final_position = results_df['position'].iloc[-1]
    final_mtum_price = results_df['mtum_price'].iloc[-1]
    final_ma50 = results_df['ma_50'].iloc[-1]
    final_distance = results_df['distance_pct'].iloc[-1]
    
    print(f"\n📊 FINAL POSITION:")
    print(f"   Current: {final_position}")
    print(f"   MTUM Price: ${final_mtum_price:.2f}")
    print(f"   50-day MA: ${final_ma50:.2f}")
    print(f"   Distance: {final_distance:+.1f}%")
    
    if final_position == "MTUM":
        print(f"   Shares: {results_df['mtum_shares'].iloc[-1]:.3f}")
    else:
        print(f"   Cash: ${results_df['cash'].iloc[-1]:,.0f}")
    
    print(f"\n🎯 STRATEGY BENEFITS:")
    print(f"   ✅ Professional momentum management (MTUM)")
    print(f"   ✅ Tactical risk management (50-day MA filter)")
    print(f"   ✅ Single ETF simplicity")
    print(f"   ✅ No individual stock risk")
    print(f"   ✅ Low costs (0.15% MTUM expense ratio)")
    
    return results_df, trades

def plot_results(results_df, trades):
    """Plot the backtest results"""
    try:
        import matplotlib.pyplot as plt
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Portfolio value over time
        ax1.plot(results_df['date'], results_df['portfolio_value'], 'b-', linewidth=2, label='MTUM + MA50 Strategy')
        ax1.axhline(y=5000, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        ax1.set_title('Portfolio Value Over Time')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # MTUM price and 50-day MA
        ax2.plot(results_df['date'], results_df['mtum_price'], 'g-', linewidth=1, label='MTUM Price')
        ax2.plot(results_df['date'], results_df['ma_50'], 'r-', linewidth=1, label='50-day MA')
        ax2.fill_between(results_df['date'], results_df['mtum_price'].min(), results_df['mtum_price'].max(), 
                        where=results_df['above_ma50'], alpha=0.2, color='green', label='Bullish')
        ax2.set_title('MTUM Price vs 50-day MA')
        ax2.set_ylabel('Price ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Position indicator
        position_numeric = results_df['position'].map({'MTUM': 1, 'CASH': 0})
        ax3.fill_between(results_df['date'], 0, position_numeric, color='blue', alpha=0.5)
        ax3.set_title('Position Status (1=MTUM, 0=Cash)')
        ax3.set_ylabel('Position')
        ax3.set_ylim(-0.1, 1.1)
        ax3.grid(True, alpha=0.3)
        
        # Distance from MA
        ax4.plot(results_df['date'], results_df['distance_pct'], 'purple', linewidth=1)
        ax4.axhline(y=0, color='red', linestyle='-', alpha=0.7)
        ax4.fill_between(results_df['date'], results_df['distance_pct'], 0, 
                        where=(results_df['distance_pct'] > 0), alpha=0.3, color='green')
        ax4.fill_between(results_df['date'], results_df['distance_pct'], 0, 
                        where=(results_df['distance_pct'] < 0), alpha=0.3, color='red')
        ax4.set_title('MTUM Distance from 50-day MA (%)')
        ax4.set_ylabel('Distance (%)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("📊 Matplotlib not available for plotting")

if __name__ == "__main__":
    # Run MTUM + 50-day MA filter backtest
    results_df, trades = backtest_mtum_ma50_filter(
        capital=5000,
        start_date="2024-01-01",
        end_date="2024-12-31"  # Available data period
    )
    
    if not results_df.empty:
        # Plot results
        plot_results(results_df, trades)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_df.to_csv(f"mtum_ma50_backtest_{timestamp}.csv", index=False)
        print(f"\n💾 Results saved to: mtum_ma50_backtest_{timestamp}.csv")
    else:
        print("❌ Backtest failed - no results to save")