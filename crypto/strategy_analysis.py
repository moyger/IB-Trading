#!/usr/bin/env python3
"""
BTCUSDT Enhanced Strategy Analysis & Optimization
Identifies optimization opportunities without overfitting
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategies'))

from data_fetcher import BTCDataFetcher
from btcusdt_enhanced_strategy import BTCUSDTEnhancedStrategy

def analyze_current_performance():
    """Analyze current strategy performance across different periods"""
    print("📊 BTCUSDT ENHANCED STRATEGY - COMPREHENSIVE ANALYSIS")
    print("=" * 60)
    
    strategy = BTCUSDTEnhancedStrategy(account_size=10000, risk_profile='moderate')
    data_fetcher = BTCDataFetcher()
    
    # Test periods for robust analysis
    test_periods = [
        ("2023-08-01", "2023-11-01", "Q3 2023"),
        ("2023-11-01", "2024-02-01", "Q4 2023"),
        ("2024-02-01", "2024-05-01", "Q1 2024"),
        ("2024-05-01", "2024-08-01", "Q2 2024"),
        ("2024-08-01", "2024-11-01", "Q3 2024")
    ]
    
    results = []
    
    for start_date, end_date, period_name in test_periods:
        print(f"\n🧪 Testing Period: {period_name} ({start_date} to {end_date})")
        
        # Fetch data
        df = data_fetcher.fetch_btc_data(start_date, end_date, "1h")
        if df is None or df.empty:
            print(f"❌ Failed to fetch data for {period_name}")
            continue
        
        # Reset strategy for new period
        strategy.current_balance = strategy.initial_balance
        strategy.trades = []
        strategy.current_position = 0
        
        # Run simulation
        try:
            trades, balance_history = strategy._simulate_trading(df)
            
            if trades:
                # Calculate metrics
                win_trades = [t for t in trades if t['pnl'] > 0]
                loss_trades = [t for t in trades if t['pnl'] < 0]
                
                win_rate = len(win_trades) / len(trades) * 100 if trades else 0
                total_return = (strategy.current_balance - strategy.initial_balance) / strategy.initial_balance * 100
                avg_win = np.mean([t['pnl'] for t in win_trades]) if win_trades else 0
                avg_loss = np.mean([t['pnl'] for t in loss_trades]) if loss_trades else 0
                profit_factor = abs(sum([t['pnl'] for t in win_trades]) / sum([t['pnl'] for t in loss_trades])) if loss_trades else float('inf')
                
                # Confluence analysis
                confluence_scores = [t.get('confluence_score', 0) for t in trades]
                avg_confluence = np.mean(confluence_scores) if confluence_scores else 0
                
                result = {
                    'period': period_name,
                    'total_trades': len(trades),
                    'win_rate': win_rate,
                    'total_return': total_return,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss,
                    'profit_factor': profit_factor,
                    'avg_confluence': avg_confluence,
                    'data_points': len(df)
                }
                
                results.append(result)
                
                print(f"   📈 Trades: {len(trades)}, Win Rate: {win_rate:.1f}%, Return: {total_return:+.2f}%")
                print(f"   🎯 Avg Confluence: {avg_confluence:.2f}, PF: {profit_factor:.2f}")
            else:
                print(f"   ⚠️ No trades generated for {period_name}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing {period_name}: {e}")
    
    return results

def identify_optimization_opportunities(results):
    """Identify optimization opportunities without overfitting"""
    print(f"\n🔍 OPTIMIZATION ANALYSIS")
    print("=" * 40)
    
    if not results:
        print("❌ No results to analyze")
        return
    
    # Calculate aggregate metrics
    total_trades = sum([r['total_trades'] for r in results])
    avg_win_rate = np.mean([r['win_rate'] for r in results])
    avg_return = np.mean([r['total_return'] for r in results])
    avg_confluence = np.mean([r['avg_confluence'] for r in results])
    
    print(f"📊 AGGREGATE PERFORMANCE:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Average Win Rate: {avg_win_rate:.1f}%")
    print(f"   Average Return: {avg_return:+.2f}%")
    print(f"   Average Confluence Score: {avg_confluence:.2f}/7")
    
    # Identify optimization opportunities
    opportunities = []
    
    # 1. Win Rate Analysis
    if avg_win_rate < 50:
        opportunities.append({
            'area': 'Signal Quality',
            'issue': f'Win rate ({avg_win_rate:.1f}%) below optimal 50%+',
            'suggestion': 'Increase confluence threshold or refine entry conditions'
        })
    
    # 2. Trade Frequency Analysis
    avg_trades_per_period = total_trades / len(results)
    if avg_trades_per_period < 20:
        opportunities.append({
            'area': 'Trade Frequency',
            'issue': f'Low trade frequency ({avg_trades_per_period:.1f} per quarter)',
            'suggestion': 'Consider secondary entry conditions or multi-timeframe analysis'
        })
    
    # 3. Confluence Score Analysis
    if avg_confluence > 5.5:
        opportunities.append({
            'area': 'Entry Threshold',
            'issue': f'High confluence threshold ({avg_confluence:.2f}) may be too restrictive',
            'suggestion': 'Test lowering confluence threshold from 4 to 3.5'
        })
    elif avg_confluence < 4.5:
        opportunities.append({
            'area': 'Signal Strength',
            'issue': f'Low confluence scores ({avg_confluence:.2f}) suggest weak signals',
            'suggestion': 'Strengthen confluence scoring or add new indicators'
        })
    
    # 4. Consistency Analysis
    returns = [r['total_return'] for r in results]
    return_volatility = np.std(returns)
    if return_volatility > 15:
        opportunities.append({
            'area': 'Consistency',
            'issue': f'High return volatility ({return_volatility:.1f}%) across periods',
            'suggestion': 'Improve risk management or market regime detection'
        })
    
    # 5. Risk-Reward Analysis
    profit_factors = [r['profit_factor'] for r in results if r['profit_factor'] != float('inf')]
    if profit_factors and np.mean(profit_factors) < 2.0:
        opportunities.append({
            'area': 'Risk-Reward',
            'issue': f'Low profit factor ({np.mean(profit_factors):.2f})',
            'suggestion': 'Optimize stop-loss and take-profit levels'
        })
    
    print(f"\n🎯 OPTIMIZATION OPPORTUNITIES:")
    print("-" * 40)
    
    if not opportunities:
        print("✅ Strategy appears well-optimized across all analyzed areas")
        return []
    
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp['area']}:")
        print(f"   Issue: {opp['issue']}")
        print(f"   Suggestion: {opp['suggestion']}")
        print()
    
    return opportunities

def suggest_conservative_optimizations():
    """Suggest conservative optimizations to avoid overfitting"""
    print(f"\n🛡️ CONSERVATIVE OPTIMIZATION RECOMMENDATIONS")
    print("=" * 50)
    
    optimizations = [
        {
            'parameter': 'Confluence Threshold',
            'current': '4.0',
            'suggested': '3.5-4.5 range',
            'rationale': 'Test slight adjustment to balance trade frequency vs quality',
            'risk': 'Low - fundamental logic unchanged'
        },
        {
            'parameter': 'RSI Thresholds',
            'current': 'RSI 30-70 range',
            'suggested': 'Dynamic RSI based on volatility',
            'rationale': 'Adapt to market volatility rather than fixed levels',
            'risk': 'Medium - adds complexity but improves adaptability'
        },
        {
            'parameter': 'Volume Confirmation',
            'current': 'Volume > 1.2x average',
            'suggested': 'Volume percentile ranking (top 30%)',
            'rationale': 'More robust volume filtering in different market conditions',
            'risk': 'Low - similar concept, better implementation'
        },
        {
            'parameter': 'Market Regime Detection',
            'current': 'ADX-based trending',
            'suggested': 'Add volatility regime classification',
            'rationale': 'Better performance in high/low volatility environments',
            'risk': 'Medium - requires additional validation'
        },
        {
            'parameter': 'Exit Strategy',
            'current': 'Fixed stop-loss/take-profit',
            'suggested': 'Trailing stops for trending markets',
            'rationale': 'Capture larger moves in strong trends',
            'risk': 'Medium - changes risk profile'
        }
    ]
    
    for opt in optimizations:
        print(f"🔧 {opt['parameter']}:")
        print(f"   Current: {opt['current']}")
        print(f"   Suggested: {opt['suggested']}")
        print(f"   Rationale: {opt['rationale']}")
        print(f"   Risk Level: {opt['risk']}")
        print()
    
    return optimizations

def main():
    """Main analysis function"""
    print("🧪 Starting comprehensive strategy analysis...")
    
    # 1. Analyze current performance
    results = analyze_current_performance()
    
    # 2. Identify optimization opportunities
    opportunities = identify_optimization_opportunities(results)
    
    # 3. Suggest conservative optimizations
    optimizations = suggest_conservative_optimizations()
    
    print(f"\n📋 ANALYSIS SUMMARY:")
    print("=" * 30)
    print(f"✅ Performance Analysis: Completed across {len(results)} periods")
    print(f"🎯 Optimization Areas: {len(opportunities)} identified")
    print(f"🛡️ Conservative Suggestions: {len(optimizations)} proposed")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Implement most promising optimization (confluence threshold)")
    print("2. Test on out-of-sample data")
    print("3. Compare performance metrics")
    print("4. Validate robustness across different market conditions")
    
    return results, opportunities, optimizations

if __name__ == "__main__":
    main()