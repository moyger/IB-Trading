#!/usr/bin/env python3
"""
Test script to demonstrate 24-month monthly summaries for Bitcoin FTMO strategy
"""
import sys
import os

# Add the strategies directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'strategies'))

from btcusdt_ftmo_1h_strategy import BTCUSDTFTMO1HStrategy

def test_24_month_monthly_summary():
    """Test 24-month monthly summary generation"""
    print("🚀 TESTING 24-MONTH BITCOIN FTMO MONTHLY SUMMARIES")
    print("=" * 70)
    
    # Create strategy with Phase 1 parameters
    strategy = BTCUSDTFTMO1HStrategy(100000, 1)
    
    print(f"\n🎯 Running 24-month backtest: August 2023 to July 2025")
    print(f"📊 This will show month-by-month P&L breakdown...")
    
    # Run full 24-month backtest
    df = strategy.run_bitcoin_backtest("2023-08-01", "2025-07-31")
    
    if df is not None:
        print(f"\n✅ Backtest completed successfully!")
        print(f"📅 Total data points analyzed: {len(df):,}")
        
        # Print detailed results including monthly summaries
        strategy.print_bitcoin_results()
        
        # Additional monthly analysis
        if strategy.monthly_summaries:
            print(f"\n📈 DETAILED MONTHLY ANALYSIS:")
            print("=" * 90)
            print(f"{'Month':<8} {'Start $':<12} {'End $':<12} {'P&L $':<12} {'P&L %':<8} {'Trades':<8}")
            print("-" * 90)
            
            total_trades = 0
            profitable_months = 0
            
            for monthly_data in strategy.monthly_summaries:
                status = "📈" if monthly_data['pnl_amount'] >= 0 else "📉"
                print(f"{monthly_data['month']:<8} "
                      f"${monthly_data['starting_balance']:>10,.0f} "
                      f"${monthly_data['ending_balance']:>10,.0f} "
                      f"${monthly_data['pnl_amount']:>+10,.2f} "
                      f"{monthly_data['pnl_percentage']:>+6.2f}% "
                      f"{monthly_data['trade_count']:>6} "
                      f"{status}")
                
                total_trades += monthly_data['trade_count']
                if monthly_data['pnl_amount'] >= 0:
                    profitable_months += 1
            
            print("-" * 90)
            print(f"\n🏆 MONTHLY STATISTICS SUMMARY:")
            print(f"📊 Total Months Analyzed: {len(strategy.monthly_summaries)}")
            print(f"✅ Profitable Months: {profitable_months}")
            print(f"❌ Loss Months: {len(strategy.monthly_summaries) - profitable_months}")
            print(f"🎯 Monthly Success Rate: {(profitable_months/len(strategy.monthly_summaries)*100):.1f}%")
            print(f"📈 Total Trades Executed: {total_trades}")
        
    else:
        print("❌ Backtest failed - unable to generate monthly summaries")

if __name__ == "__main__":
    test_24_month_monthly_summary()