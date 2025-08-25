#!/usr/bin/env python3
"""
Arthur Hill's ATR Trailing Stop Integration Analysis
Should we add ATR stops to our 3-stock Trend Composite strategy?

Arthur Hill's Approach:
1. Trend Composite for entry signals (trend identification)  
2. ATR Trailing Stop for exit strategy (risk management)
3. Typical: 5 x ATR(22) below highest close since entry
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_arthur_hill_methodology():
    """
    Analyze Arthur Hill's complete trading methodology
    """
    
    print("🔍 ARTHUR HILL'S COMPLETE TRADING METHODOLOGY")
    print("=" * 80)
    print("📊 Chief Technical Strategist at TrendInvestorPro.com")
    print("🎯 Senior Technical Analyst at StockCharts.com")
    print()
    
    print("📋 WHAT ARTHUR HILL TRADES:")
    print("-" * 50)
    print("✅ PRIMARY UNIVERSE:")
    print("   • 74 core ETFs (equities, bonds, commodities, crypto)")
    print("   • Individual stocks from S&P 500 and Nasdaq 100")
    print("   • Examples: XLF, XLK, SOXX, ITB, GOOGL, Home Depot")
    print()
    
    print("🎯 TWO-COMPONENT TRADING SYSTEM:")
    print("-" * 50)
    print("1. 📊 TREND COMPOSITE (Entry Signal)")
    print("   • Aggregates 5 trend-following indicators")  
    print("   • Score: -5 (very bearish) to +5 (very bullish)")
    print("   • Entry when Trend Composite turns positive (green)")
    print("   • Used for trend identification and timing")
    print()
    print("2. 🛡️ ATR TRAILING STOP (Exit Strategy)")
    print("   • 5 x ATR(22) below highest close since entry")
    print("   • Dynamic stop that trails price higher")
    print("   • Protects against outsized declines")
    print("   • Often triggers before bearish Trend Composite")
    print()
    
    print("⚡ KEY INSIGHT:")
    print("-" * 30)
    print("Arthur Hill uses Trend Composite for ENTRY and")
    print("ATR Trailing Stop for EXIT - complementary system!")

def compare_approaches():
    """
    Compare our current approach vs Arthur Hill's methodology
    """
    
    print(f"\n⚖️ OUR APPROACH vs ARTHUR HILL'S APPROACH")
    print("=" * 80)
    
    print("🔷 OUR CURRENT APPROACH:")
    print("-" * 40)
    print("• Trend Composite score → Position allocation %")
    print("• Daily rebalancing: 0%, 20%, 40%, 60%, 80%, 100%") 
    print("• Gradual scaling in/out of positions")
    print("• Risk management through allocation reduction")
    print("• No hard stop losses")
    print()
    
    print("🔶 ARTHUR HILL'S APPROACH:")
    print("-" * 40)
    print("• Trend Composite positive → Enter full position")
    print("• Binary: Full position or cash")
    print("• ATR Trailing Stop for hard exit")
    print("• Risk management through stops")
    print("• Clear entry/exit points")

def analyze_atr_integration_options():
    """
    Analyze how ATR trailing stops could integrate
    """
    
    print(f"\n🔧 ATR INTEGRATION OPTIONS")
    print("=" * 60)
    
    print("🎯 OPTION 1: HYBRID APPROACH (RECOMMENDED)")
    print("-" * 50)
    print("✅ KEEP: Current trend composite allocation system")
    print("✅ ADD: ATR trailing stop as individual stock protection")
    print()
    print("How it works:")
    print("• Continue dynamic allocation (0%-100%)")
    print("• Add ATR stop at individual stock level")  
    print("• If stock hits ATR stop → Force allocation to 0%")
    print("• Redistribute capital to remaining stocks")
    print("• Re-enter only on new trend composite signal")
    print()
    
    print("🎯 OPTION 2: FULL ARTHUR HILL SYSTEM")
    print("-" * 50)
    print("✅ REPLACE: Current allocation system")
    print("✅ USE: Binary entry/exit with ATR stops")
    print()
    print("How it works:")
    print("• Trend Composite +3 → Enter full position")
    print("• Set ATR stop immediately")
    print("• Hold until ATR stop hit")
    print("• Complete exit, wait for re-entry")

def show_atr_calculation_example():
    """
    Show ATR trailing stop calculation
    """
    
    print(f"\n📊 ATR TRAILING STOP EXAMPLE")
    print("=" * 50)
    print("🎯 Arthur Hill's Method: 5 x ATR(22)")
    print()
    
    try:
        # Download TSLA data
        ticker = yf.Ticker("TSLA") 
        df = ticker.history(period="6mo")
        
        if df.empty:
            print("❌ Could not download data")
            return
        
        # Calculate ATR(22)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr_22 = true_range.rolling(22).mean()
        
        # Recent values
        current_price = df['Close'].iloc[-1]
        current_atr = atr_22.iloc[-1]
        trailing_stop = current_price - (5 * current_atr)
        
        print(f"📈 TSLA Example:")
        print(f"   Current Price:    ${current_price:.2f}")
        print(f"   ATR(22):          ${current_atr:.2f}")
        print(f"   5 x ATR:          ${5 * current_atr:.2f}")
        print(f"   Trailing Stop:    ${trailing_stop:.2f}")
        print(f"   Stop Distance:    {((current_price - trailing_stop) / current_price) * 100:.1f}% below price")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def recommend_integration():
    """
    Final recommendation
    """
    
    print(f"\n🏆 RECOMMENDATION: HYBRID ATR INTEGRATION")
    print("=" * 60)
    
    print("📊 IMPLEMENTATION:")
    print("-" * 30)
    print("1. 🔷 KEEP current trend composite allocation system")
    print("2. 🛡️ ADD ATR trailing stops as portfolio protection")
    print("3. ⚡ Use 4x ATR(22) for more responsive stops")
    print("4. 🔄 Weekly recalculation for efficiency")
    print()
    
    print("✅ WHY HYBRID WORKS BEST:")
    print("-" * 40)
    print("• Preserves our +47.8% return system")
    print("• Adds Arthur Hill's risk management")
    print("• Reduces individual stock drawdowns") 
    print("• Maintains portfolio diversification")
    print("• Simple to implement")
    print()
    
    print("🎯 NEXT STEPS:")
    print("-" * 20)
    print("1. Backtest hybrid approach")
    print("2. Compare performance vs current system")
    print("3. Optimize ATR multiplier (3x, 4x, 5x)")
    print("4. Implement if shows improvement")

def main():
    """
    Run complete analysis
    """
    
    analyze_arthur_hill_methodology()
    compare_approaches()
    analyze_atr_integration_options()
    show_atr_calculation_example()
    recommend_integration()
    
    print(f"\n🎯 BOTTOM LINE:")
    print("-" * 30)
    print("YES - Add ATR trailing stops to our strategy")
    print("Keep our allocation system + add ATR protection")
    print("Best of both worlds approach!")

if __name__ == "__main__":
    main()