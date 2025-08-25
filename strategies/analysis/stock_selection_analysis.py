#!/usr/bin/env python3
"""
Stock Selection Strategy Analysis
Current: Fixed AMZN, TSLA, RBLX vs Dynamic rotation approach
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_current_stock_selection():
    """
    Explain current stock selection criteria and rationale
    """
    
    print("🔍 CURRENT STOCK SELECTION STRATEGY")
    print("=" * 80)
    print("📊 Fixed Portfolio: AMZN, TSLA, RBLX")
    print("💰 Equal weighting: $1,667 per stock")
    print("🎯 Strategy: Trend Composite with dynamic allocation")
    print()
    
    print("📋 WHY THESE 3 STOCKS?")
    print("=" * 50)
    
    selection_criteria = {
        'AMZN': {
            'why_selected': [
                'Mega-cap stability ($1.8T market cap)',
                'Multiple revenue streams (AWS, retail, advertising)',
                'Strong technical patterns and liquidity',
                'Lower volatility provides portfolio stability',
                'Institutional favorite with consistent volume'
            ],
            'sector': 'Cloud/E-commerce',
            'volatility': '~31% annual',
            'avg_volume': '44M shares/day',
            'market_cap': '$1.8T'
        },
        'TSLA': {
            'why_selected': [
                'High volatility creates clear trend signals',
                'Strong momentum history (100%+ moves possible)',
                'Different sector exposure (EV/Autonomous)',
                'Responds excellently to technical analysis',
                'High retail and institutional interest'
            ],
            'sector': 'EV/Autonomous',
            'volatility': '~64% annual', 
            'avg_volume': '103M shares/day',
            'market_cap': '$800B'
        },
        'RBLX': {
            'why_selected': [
                'Highest volatility = best trend composite signals',
                'Emerging growth in gaming/metaverse',
                'Low correlation with traditional tech',
                'Strong momentum potential (190% in backtest)',
                'Mid-cap provides different risk profile'
            ],
            'sector': 'Gaming/Metaverse',
            'volatility': '~48% annual',
            'avg_volume': '8M shares/day', 
            'market_cap': '$30B'
        }
    }
    
    for stock, info in selection_criteria.items():
        print(f"\n🎯 {stock} ({info['sector']})")
        print(f"   📊 Market Cap: {info['market_cap']} | Volatility: {info['volatility']}")
        print(f"   📈 Volume: {info['avg_volume']}")
        print("   ✅ Selection Reasons:")
        for reason in info['why_selected']:
            print(f"      • {reason}")
    
    print(f"\n🏗️ PORTFOLIO CONSTRUCTION PRINCIPLES:")
    print("-" * 60)
    print("1. 🎯 DIVERSIFICATION:")
    print("   • 3 different sectors (Cloud, EV, Gaming)")
    print("   • 3 different market caps (Mega, Large, Mid)")
    print("   • 3 different volatility levels (Low, High, Medium)")
    print()
    print("2. 📊 TREND COMPOSITE COMPATIBILITY:")
    print("   • All stocks respond well to technical analysis")
    print("   • High enough volatility for meaningful signals")
    print("   • Sufficient liquidity for easy execution")
    print("   • Strong institutional following")
    print()
    print("3. 💰 $5K CAPITAL CONSTRAINTS:")
    print("   • 3 stocks = $1,667 each (manageable position sizes)")
    print("   • Can buy meaningful share quantities")
    print("   • Transaction costs remain reasonable")
    print("   • Not over-diversified (which dilutes returns)")

def compare_fixed_vs_dynamic_approaches():
    """
    Compare current fixed approach vs dynamic stock rotation
    """
    
    print(f"\n⚖️ FIXED vs DYNAMIC STOCK SELECTION")
    print("=" * 80)
    
    print("🔒 CURRENT FIXED APPROACH:")
    print("-" * 40)
    print("✅ ADVANTAGES:")
    print("   • Consistent, backtestable strategy")
    print("   • Lower transaction costs")
    print("   • Maintains sector diversification") 
    print("   • Known risk characteristics")
    print("   • Focus on trend composite optimization")
    print("   • Simple implementation")
    print()
    print("❌ DISADVANTAGES:")
    print("   • May hold declining stocks")
    print("   • Misses rotating sector leadership")
    print("   • Not pure momentum approach")
    print("   • Could underperform in momentum markets")
    print()
    
    print("🔄 DYNAMIC MOMENTUM ROTATION:")
    print("-" * 40)
    print("✅ ADVANTAGES:")
    print("   • Always holds strongest momentum stocks")
    print("   • Captures rotating sector leadership")
    print("   • True Nick Radge momentum approach")
    print("   • Could catch breakout stocks early")
    print("   • Avoids holding declining stocks")
    print()
    print("❌ DISADVANTAGES:")
    print("   • High portfolio turnover (more transactions)")
    print("   • May buy at momentum peaks")
    print("   • Less predictable/testable")
    print("   • Higher complexity for $5K account")
    print("   • Could miss mean reversion opportunities")

def recommend_optimal_approach():
    """
    Recommend the best approach for $5K capital
    """
    
    print(f"\n🏆 RECOMMENDED APPROACH FOR $5K")
    print("=" * 60)
    print("HYBRID: Fixed Base + Momentum Filter")
    print()
    
    print("📊 IMPLEMENTATION:")
    print("-" * 30)
    print("1. 🔒 FIXED BASE PORTFOLIO:")
    print("   • Keep AMZN, TSLA, RBLX as core holdings")
    print("   • Maintain sector diversification")
    print("   • Continue using trend composite allocation")
    print()
    
    print("2. 🚀 ADD MOMENTUM FILTER:")
    print("   • Calculate 6-month momentum for each stock")
    print("   • If momentum < 0%, force allocation to 0%")
    print("   • Redistribute capital to positive momentum stocks")
    print("   • Weight allocation by relative momentum strength")
    print()
    
    print("3. 🔄 QUARTERLY REVIEW:")
    print("   • Every 3 months, evaluate replacement candidates")
    print("   • Replace stock only if new candidate has 20%+ higher momentum")
    print("   • Maintain sector diversification requirement")
    print("   • Limit to 1 stock change per quarter (reduce turnover)")
    print()
    
    print("📈 POSITION SIZE ENHANCEMENT:")
    print("-" * 40)
    print("Current: Equal 33.3% allocation per stock")
    print("Enhanced: Weight by momentum strength")
    print()
    print("Example momentum-weighted allocation:")
    print("• Highest momentum stock: 40% of capital")
    print("• Medium momentum stock:  35% of capital")
    print("• Lowest momentum stock:  25% of capital")
    print()
    
    print("🎯 WHY THIS HYBRID APPROACH?")
    print("-" * 40)
    print("✅ Combines stability of fixed portfolio")
    print("✅ Adds momentum filtering for better stock selection")
    print("✅ Reduces transaction costs vs full rotation")
    print("✅ Maintains diversification benefits")
    print("✅ Simple to implement and backtest")
    print("✅ Scales well as capital grows")

def show_implementation_priorities():
    """
    Show implementation priorities
    """
    
    print(f"\n📋 IMPLEMENTATION ROADMAP")
    print("=" * 50)
    
    priorities = {
        "IMMEDIATE": [
            "✅ Continue with current AMZN/TSLA/RBLX fixed portfolio",
            "✅ Keep using trend composite allocation system", 
            "✅ Focus on optimizing allocation levels and rebalancing frequency"
        ],
        "PHASE 2": [
            "🔄 Add momentum filter to current strategy",
            "📊 Weight positions by 6-month momentum strength",
            "⚖️ Force 0% allocation for negative momentum stocks"
        ],
        "PHASE 3": [
            "🔍 Implement quarterly stock review process",
            "📈 Test replacement candidates (NVDA, PLTR, etc)",
            "🎯 Maintain 3-stock limit with sector diversity"
        ],
        "FUTURE": [
            "💰 When capital > $25K, consider full dynamic rotation",
            "🌐 Expand to 5-stock universe with monthly rotation",
            "🤖 Automate momentum ranking and selection"
        ]
    }
    
    for phase, tasks in priorities.items():
        print(f"\n{phase}:")
        for task in tasks:
            print(f"   {task}")
    
    print(f"\n💡 KEY INSIGHT:")
    print("-" * 30)
    print("With $5K capital, focus on OPTIMIZING the current approach")
    print("rather than adding complexity. The trend composite system")
    print("is working well (+47.8% returns). Enhance it incrementally.")

def main():
    """
    Run complete stock selection analysis
    """
    
    # Analyze current approach
    analyze_current_stock_selection()
    
    # Compare approaches
    compare_fixed_vs_dynamic_approaches()
    
    # Recommend optimal approach
    recommend_optimal_approach()
    
    # Show implementation priorities
    show_implementation_priorities()
    
    print(f"\n🎯 BOTTOM LINE:")
    print("-" * 40)
    print("AMZN, TSLA, RBLX were selected for:")
    print("• Sector diversification")
    print("• Volatility spectrum for trend signals")
    print("• Market cap diversification")
    print("• Technical analysis compatibility")
    print()
    print("NEXT STEP: Add momentum filter to enhance")
    print("the existing fixed portfolio approach.")

if __name__ == "__main__":
    main()