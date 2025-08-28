#!/usr/bin/env python3
"""
Test Arthur Hill Strategy - Single Profile
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategies'))

from arthur_hill_trend_strategy import ArthurHillTrendStrategy

def test_single_profile():
    """Test Arthur Hill strategy with moderate profile"""
    print("🎯 Testing Arthur Hill Trend Strategy - Moderate Profile")
    print("=" * 60)
    
    strategy = ArthurHillTrendStrategy(
        account_size=10000,
        risk_profile='moderate'
    )
    
    # Run backtest on more recent data
    result = strategy.run_backtest("2024-03-01", "2024-08-01")
    
    if result is not None:
        print(f"\n✅ Test completed successfully!")
        
        # Show some sample trades if available
        if hasattr(strategy, 'trades') and strategy.trades:
            print(f"\n📋 Sample Trades (first 5):")
            for i, trade in enumerate(strategy.trades[:5]):
                if 'pnl' in trade:
                    pnl_str = f"${trade['pnl']:+.2f}"
                    ret_str = f"({trade['return_pct']:+.1f}%)"
                else:
                    pnl_str = "Open"
                    ret_str = ""
                
                print(f"   {i+1}. {trade['direction'].upper()} @ ${trade['entry_price']:,.0f} "
                      f"| Trend: {trade['trend_composite']:+1} | P&L: {pnl_str} {ret_str}")
        
        # Show ATR trailing stop statistics
        if hasattr(strategy, 'stop_history') and strategy.stop_history:
            print(f"\n🛡️ ATR Trailing Stop Analysis:")
            stops = strategy.stop_history
            if stops:
                avg_distance = sum([s['distance_pct'] for s in stops]) / len(stops)
                max_distance = max([s['distance_pct'] for s in stops])
                print(f"   Stop updates: {len(stops)}")
                print(f"   Average distance: {avg_distance:.2f}%")
                print(f"   Maximum distance: {max_distance:.2f}%")
    
    return strategy

if __name__ == "__main__":
    test_single_profile()