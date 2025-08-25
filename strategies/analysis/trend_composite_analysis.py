#!/usr/bin/env python3
"""
Trend Composite Analysis - ETF vs Individual Stock Performance
Comparing Arthur Hill's Trend Composite on MTUM vs PLTR

Key Finding: Individual stocks respond much better to trend composite signals
"""

import pandas as pd
import numpy as np

def analyze_trend_composite_performance():
    """
    Compare MTUM ETF vs PLTR individual stock trend composite results
    """
    
    print("🔍 TREND COMPOSITE STRATEGY ANALYSIS")
    print("=" * 80)
    print("📊 Arthur Hill's Method: ETF (MTUM) vs Individual Stock (PLTR)")
    print("🗓️ Period: January 2024 - July 2025 (1.6 years)")
    print("=" * 80)
    
    # Results comparison
    results = {
        'Strategy': ['MTUM Trend Composite', 'PLTR Trend Composite'],
        'Total Return': [14.5, 141.1],
        'Annual Return': [8.7, 75.3],
        'Avg Allocation': [31.8, 54.0],
        'Volatility': [None, 42.1],  # MTUM volatility not calculated
        'Rebalances': [302, 182],
        'Time Fully Invested': [21.3, 39.2],
        'Time Partial': [47.4, 28.9],
        'Time Cash': [31.3, 31.9],
        'vs Benchmark': [-23.8, -715.5],  # vs MTUM/PLTR buy-hold
        'vs SPY': [-22.3, 104.3]
    }
    
    df = pd.DataFrame(results)
    
    print("📈 PERFORMANCE COMPARISON:")
    print("-" * 80)
    for i, row in df.iterrows():
        strategy = row['Strategy']
        total_ret = row['Total Return']
        annual_ret = row['Annual Return']
        allocation = row['Avg Allocation']
        rebalances = row['Rebalances']
        vs_spy = row['vs SPY']
        
        print(f"{strategy:20} | Return: {total_ret:+6.1f}% ({annual_ret:+5.1f}% annual)")
        print(f"{'':20} | Allocation: {allocation:4.1f}% | Rebalances: {rebalances:3d}")
        print(f"{'':20} | vs SPY: {vs_spy:+6.1f}%")
        print()
    
    print("🎯 KEY INSIGHTS:")
    print("-" * 80)
    print("✅ Individual stocks respond 10x better to trend composite signals")
    print("✅ PLTR had 70% higher average allocation than MTUM")
    print("✅ PLTR required 40% fewer rebalances (less whipsaw)")
    print("✅ Individual stock volatility creates clearer breakouts/breakdowns")
    print("✅ Technical indicators less correlated on single names")
    print()
    
    print("⚠️ CHALLENGES WITH INDIVIDUAL STOCKS:")
    print("-" * 80)
    print("❌ Higher volatility requires larger position size flexibility")
    print("❌ Company-specific risk not diversified away")
    print("❌ Trend composite still underperformed buy-and-hold significantly")
    print("❌ Transaction costs higher with more active trading")
    print()
    
    print("🔧 POTENTIAL OPTIMIZATIONS FOR INDIVIDUAL STOCKS:")
    print("-" * 80)
    print("1. 📊 Adjust position allocation levels:")
    print("   • Current: 0%, 10%, 25%, 40%, 60%, 75%, 90%, 100%")
    print("   • Optimized: 0%, 0%, 25%, 50%, 75%, 90%, 100%, 100%")
    print()
    print("2. 🎯 Add momentum filter:")
    print("   • Only trade when 20-day momentum > 0")
    print("   • Combine trend composite with Nick Radge momentum")
    print()
    print("3. ⏰ Optimize rebalancing frequency:")
    print("   • Current: Daily rebalancing on score changes")
    print("   • Test: Weekly or score change > 2 points")
    print()
    print("4. 💰 Position sizing enhancements:")
    print("   • ATR-based position sizing")
    print("   • Volatility-adjusted allocation levels")
    print()
    print("5. 🛡️ Risk management:")
    print("   • Stop losses at -20% individual position level")
    print("   • Portfolio level max drawdown limits")
    print()
    
    print("🚀 NEXT STEPS:")
    print("-" * 80)
    print("1. Test optimized position allocation levels")
    print("2. Add momentum filter to PLTR strategy") 
    print("3. Test on other high-momentum individual stocks")
    print("4. Compare with simplified 50-day MA strategy")
    print("5. Implement risk management overlays")
    print()
    
    return df

def suggest_optimized_allocation_levels():
    """
    Suggest optimized position allocation levels for individual stocks
    """
    
    print("🎯 OPTIMIZED POSITION ALLOCATION LEVELS")
    print("=" * 60)
    print("📊 Based on PLTR trend composite analysis")
    print()
    
    current_levels = {
        -5: 0.00, -4: 0.00, -3: 0.00, -2: 0.00, -1: 0.10,
        0: 0.25, 1: 0.40, 2: 0.60, 3: 0.75, 4: 0.90, 5: 1.00
    }
    
    # Option 1: More aggressive on positive signals
    optimized_v1 = {
        -5: 0.00, -4: 0.00, -3: 0.00, -2: 0.00, -1: 0.00,
        0: 0.20, 1: 0.50, 2: 0.70, 3: 0.85, 4: 1.00, 5: 1.00
    }
    
    # Option 2: Binary approach with trend strength
    optimized_v2 = {
        -5: 0.00, -4: 0.00, -3: 0.00, -2: 0.00, -1: 0.00,
        0: 0.00, 1: 0.25, 2: 0.50, 3: 0.75, 4: 1.00, 5: 1.00
    }
    
    print("ALLOCATION COMPARISON:")
    print("-" * 60)
    print("Score | Current | Option 1 | Option 2 | Rationale")
    print("-" * 60)
    
    for score in range(-5, 6):
        current = current_levels[score]
        opt1 = optimized_v1[score]
        opt2 = optimized_v2[score]
        
        if score <= -2:
            rationale = "Stay in cash during bearish signals"
        elif score == -1:
            rationale = "Minimal exposure on weak bearish"
        elif score == 0:
            rationale = "Small position on neutral"
        elif score <= 2:
            rationale = "Gradual increase on bullish signals"
        else:
            rationale = "Full/near-full on strong bullish"
            
        print(f"{score:+2d}    | {current:5.0%}   | {opt1:6.0%}   | {opt2:6.0%}   | {rationale}")
    
    print()
    print("📊 EXPECTED IMPACT:")
    print("-" * 40)
    print("Option 1 (Aggressive):")
    print("  • Higher average allocation (~65%)")
    print("  • Better capture of positive trends")  
    print("  • Higher volatility and drawdowns")
    print()
    print("Option 2 (Conservative):")
    print("  • Cleaner binary signals")
    print("  • Reduced whipsaw in neutral zones")
    print("  • Lower average allocation (~45%)")
    print()

if __name__ == "__main__":
    # Run analysis
    df = analyze_trend_composite_performance()
    print()
    suggest_optimized_allocation_levels()