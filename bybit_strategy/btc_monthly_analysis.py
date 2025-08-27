#!/usr/bin/env python3
"""
BTC Strategy Monthly Performance Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from btcusdt_1h_enhanced_strategy import BTCUSDT1HEnhancedStrategy

def run_monthly_analysis():
    """Generate monthly performance breakdown for BTC strategy"""
    
    # Test each month separately
    test_months = [
        ('2024-01-01', '2024-01-31', 'Jan 2024'),
        ('2024-02-01', '2024-02-29', 'Feb 2024'),
        ('2024-03-01', '2024-03-31', 'Mar 2024'),
        ('2024-04-01', '2024-04-30', 'Apr 2024'),
        ('2024-05-01', '2024-05-31', 'May 2024'),
        ('2024-06-01', '2024-06-30', 'Jun 2024'),
        ('2024-07-01', '2024-07-31', 'Jul 2024'),
        ('2024-08-01', '2024-08-31', 'Aug 2024'),
        ('2024-09-01', '2024-09-30', 'Sep 2024'),
        ('2024-10-01', '2024-10-31', 'Oct 2024'),
        ('2024-11-01', '2024-11-30', 'Nov 2024'),
        ('2024-12-01', '2024-12-31', 'Dec 2024'),
        ('2025-01-01', '2025-01-31', 'Jan 2025'),
        ('2025-02-01', '2025-02-28', 'Feb 2025'),
        ('2025-03-01', '2025-03-31', 'Mar 2025'),
        ('2025-04-01', '2025-04-30', 'Apr 2025'),
        ('2025-05-01', '2025-05-31', 'May 2025'),
        ('2025-06-01', '2025-06-30', 'Jun 2025'),
        ('2025-07-01', '2025-07-31', 'Jul 2025')
    ]

    print('📊 BTC STRATEGY - MONTHLY PERFORMANCE SUMMARY')
    print('=' * 65)
    print('Month        | Return   | Trades | Final Balance')
    print('-' * 65)

    monthly_results = []
    cumulative_balance = 10000

    for start, end, month_name in test_months:
        try:
            # Create fresh strategy for each month
            monthly_btc = BTCUSDT1HEnhancedStrategy(cumulative_balance, 'aggressive')
            
            # Run monthly backtest
            df = monthly_btc.run_1h_crypto_backtest(start, end)
            
            if df is not None:
                initial = monthly_btc.initial_balance
                final = monthly_btc.current_balance
                monthly_return = ((final - initial) / initial) * 100
                trades = len([t for t in monthly_btc.trades if t.get('action') == 'CLOSE'])
                
                monthly_results.append({
                    'month': month_name,
                    'return': monthly_return,
                    'trades': trades,
                    'initial': initial,
                    'final': final
                })
                
                cumulative_balance = final  # Compound for next month
                
                print(f'{month_name:<12} | {monthly_return:+6.1f}% | {trades:<6} | ${final:,.0f}')
            else:
                print(f'{month_name:<12} | No Data  | 0      | ${cumulative_balance:,.0f}')
                
        except Exception as e:
            print(f'{month_name:<12} | ERROR    | 0      | ${cumulative_balance:,.0f}')

    print('-' * 65)

    # Calculate summary statistics
    if monthly_results:
        total_months = len(monthly_results)
        profitable_months = sum(1 for r in monthly_results if r['return'] > 0)
        total_return = ((cumulative_balance - 10000) / 10000) * 100
        avg_monthly = sum(r['return'] for r in monthly_results) / total_months
        total_trades = sum(r['trades'] for r in monthly_results)
        
        best_month = max(monthly_results, key=lambda x: x['return'])
        worst_month = min(monthly_results, key=lambda x: x['return'])
        
        print(f'\n📈 SUMMARY STATISTICS:')
        print(f'   Total Return: {total_return:+.1f}%')
        print(f'   Average Monthly: {avg_monthly:+.1f}%')
        print(f'   Profitable Months: {profitable_months}/{total_months} ({profitable_months/total_months*100:.1f}%)')
        print(f'   Total Trades: {total_trades}')
        print(f'   Best Month: {best_month["month"]} ({best_month["return"]:+.1f}%)')
        print(f'   Worst Month: {worst_month["month"]} ({worst_month["return"]:+.1f}%)')
        
        # Additional analysis
        print(f'\n🔍 DETAILED ANALYSIS:')
        if avg_monthly < -2:
            print('   ❌ Strategy is consistently losing money')
            print('   🔧 Recommendation: Complete strategy rebuild needed')
        elif avg_monthly < 0:
            print('   ⚠️ Strategy showing slight losses')
            print('   🔧 Recommendation: Parameter adjustment needed')
        elif avg_monthly > 5:
            print('   ✅ Strategy performing well')
            print('   📈 Recommendation: Continue current approach')
        else:
            print('   📊 Strategy showing modest performance')
            print('   🔧 Recommendation: Optimization may help')
            
        print(f'   📊 Win Rate: {profitable_months/total_months*100:.1f}%')
        print(f'   🎯 Trading Activity: {total_trades/total_months:.1f} trades/month')

if __name__ == "__main__":
    run_monthly_analysis()