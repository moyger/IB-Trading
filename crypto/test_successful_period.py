#!/usr/bin/env python3
"""
Test script to show monthly summaries for the successful Peak Bull Market period
"""
import sys
import os

# Add the strategies directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'strategies'))

from btcusdt_ftmo_1h_strategy import BTCUSDTFTMO1HStrategy

def test_successful_period_monthly_summary():
    """Test the Peak Bull Market period that showed excellent results"""
    print("🚀 TESTING PEAK BULL MARKET PERIOD - MONTHLY SUMMARIES")
    print("=" * 70)
    print("📅 Period: 2024-01-01 to 2024-06-01 (Peak Bull Market)")
    print("🏆 Expected: 52 trades with +36.56% return")
    
    # Create strategy with Phase 1 parameters  
    strategy = BTCUSDTFTMO1HStrategy(100000, 1)
    
    # Run Peak Bull Market backtest
    df = strategy.run_bitcoin_backtest("2024-01-01", "2024-06-01")
    
    if df is not None:
        print(f"\n✅ Peak Bull Market backtest completed!")
        print(f"📅 Data points analyzed: {len(df):,}")
        
        # Print detailed results including monthly summaries
        strategy.print_bitcoin_results()
        
        # Show month-by-month breakdown
        if strategy.monthly_summaries:
            print(f"\n📊 PEAK BULL MARKET - MONTH BY MONTH:")
            print("=" * 80)
            for monthly_data in strategy.monthly_summaries:
                status = "📈" if monthly_data['pnl_amount'] >= 0 else "📉"
                print(f"{monthly_data['month']}: "
                      f"${monthly_data['starting_balance']:,.0f} → "
                      f"${monthly_data['ending_balance']:,.0f} | "
                      f"P&L: ${monthly_data['pnl_amount']:+,.2f} ({monthly_data['pnl_percentage']:+.2f}%) | "
                      f"Trades: {monthly_data['trade_count']} {status}")
    else:
        print("❌ Peak Bull Market backtest failed")

if __name__ == "__main__":
    test_successful_period_monthly_summary()