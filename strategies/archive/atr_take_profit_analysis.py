#!/usr/bin/env python3
"""
ATR Trailing Take Profit Analysis
Test using ATR trailing stops for profit-taking instead of stop losses

Concept: Instead of using ATR to prevent losses, use it to lock in profits
- Enter position on positive trend composite
- Set ATR trailing take-profit above entry price
- Exit when price drops back to ATR level (profit-taking)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_atr_take_profit_concept():
    """
    Analyze ATR trailing stops as take-profit mechanism
    """
    
    print("🎯 ATR TRAILING STOPS as TAKE PROFIT MECHANISM")
    print("=" * 80)
    print("💡 CONCEPT: Use ATR to lock in profits, not prevent losses")
    print()
    
    print("📋 CURRENT vs TAKE-PROFIT APPROACH:")
    print("-" * 60)
    print("🔻 STOP LOSS APPROACH (what we tested):")
    print("   • ATR stop BELOW current price")
    print("   • Triggers when price falls (protects losses)")
    print("   • Problem: Bull market rarely triggered stops")
    print()
    
    print("📈 TAKE PROFIT APPROACH (new concept):")
    print("   • ATR trailing level ABOVE entry price")
    print("   • Trails higher as price rises")
    print("   • Triggers when price pulls back (locks profits)")
    print("   • Could be more effective in trending markets")
    print()
    
    print("🔧 HOW ATR TAKE PROFIT WOULD WORK:")
    print("-" * 50)
    print("1. 📊 ENTRY: Trend Composite score ≥ +3")
    print("2. 🎯 SET TAKE PROFIT: Entry + (2x ATR above entry)")
    print("3. 📈 TRAIL HIGHER: As price makes new highs")
    print("4. 💰 EXIT: When price drops back to trailing level")
    print("5. 🔄 RE-ENTER: On new trend composite signal")
    print()
    
    print("🎪 EXAMPLE SCENARIO:")
    print("-" * 30)
    print("• Stock enters at $100, ATR = $5")
    print("• Initial take-profit level: $100 + (2 × $5) = $110")
    print("• Stock rises to $120")
    print("• New take-profit level: $120 + (2 × ATR) = ~$130")
    print("• Stock pulls back to $125")
    print("• Exit at $125 (locked in $25 profit)")

def simulate_atr_take_profit_example():
    """
    Simulate ATR take profit on TSLA example
    """
    
    print(f"\n📊 ATR TAKE PROFIT SIMULATION - TSLA EXAMPLE")
    print("=" * 60)
    
    try:
        # Download TSLA data
        ticker = yf.Ticker("TSLA")
        df = ticker.history(start="2024-01-01", end="2024-12-31")
        
        if df.empty:
            print("❌ No data available")
            return
        
        # Calculate ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr_22 = true_range.rolling(22).mean()
        
        # Simulate simple take-profit strategy
        print("🎯 SIMULATING ATR TAKE PROFIT TRADES:")
        print("-" * 50)
        
        in_position = False
        entry_price = 0
        take_profit_level = 0
        highest_since_entry = 0
        trades = []
        
        # Simple simulation
        for i in range(22, min(len(df), 100)):  # First 100 days for demo
            date = df.index[i]
            price = df['Close'].iloc[i]
            atr = atr_22.iloc[i]
            
            if pd.isna(atr):
                continue
            
            if not in_position:
                # Simple entry: price up 3% from 10 days ago (momentum)
                if i >= 32:
                    past_price = df['Close'].iloc[i-10]
                    if (price / past_price - 1) > 0.03:  # 3% momentum
                        # Enter position
                        in_position = True
                        entry_price = price
                        take_profit_level = price + (2 * atr)  # 2x ATR above entry
                        highest_since_entry = price
                        
                        print(f"{date.date()}: ENTER at ${price:.2f} | Take-profit: ${take_profit_level:.2f}")
            
            else:
                # Update highest price since entry
                if price > highest_since_entry:
                    highest_since_entry = price
                    # Update trailing take-profit level
                    new_take_profit = highest_since_entry - (2 * atr)  # 2x ATR below highest
                    take_profit_level = max(take_profit_level, new_take_profit)
                
                # Check if take-profit triggered
                if price <= take_profit_level:
                    # Exit position
                    profit = price - entry_price
                    profit_pct = (profit / entry_price) * 100
                    
                    trades.append({
                        'entry': entry_price,
                        'exit': price,
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'highest': highest_since_entry,
                        'days_held': (date - df.index[i-10]).days  # Rough estimate
                    })
                    
                    print(f"{date.date()}: EXIT at ${price:.2f} | Profit: ${profit:.2f} ({profit_pct:+.1f}%)")
                    print(f"          Highest: ${highest_since_entry:.2f} | Take-profit: ${take_profit_level:.2f}")
                    
                    in_position = False
        
        # Analysis
        if trades:
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['profit'] > 0])
            avg_profit = np.mean([t['profit_pct'] for t in trades])
            
            print(f"\n📈 ATR TAKE PROFIT RESULTS:")
            print(f"   Total Trades: {total_trades}")
            print(f"   Winning Trades: {winning_trades}/{total_trades} ({winning_trades/total_trades*100:.0f}%)")
            print(f"   Average Profit: {avg_profit:+.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def compare_take_profit_approaches():
    """
    Compare different take-profit approaches
    """
    
    print(f"\n⚖️ TAKE PROFIT APPROACHES COMPARISON")
    print("=" * 70)
    
    approaches = {
        "CURRENT SYSTEM": {
            "method": "Trend Composite allocation reduction",
            "trigger": "Score drops from +4 to +2 → Reduce 100% to 60%",
            "pros": ["Gradual scaling", "Captures partial profits", "Stays in trend"],
            "cons": ["May give back profits", "No hard exit"]
        },
        "ATR TAKE PROFIT": {
            "method": "ATR trailing above entry price", 
            "trigger": "Price drops to ATR trail level → Complete exit",
            "pros": ["Locks in profits", "Clear exit signal", "Protects gains"],
            "cons": ["Binary exit", "May exit too early", "Miss continuation"]
        },
        "HYBRID APPROACH": {
            "method": "Combine both methods",
            "trigger": "Use both allocation scaling + ATR profit protection",
            "pros": ["Best of both worlds", "Flexible profit-taking"],
            "cons": ["More complex", "Potential conflicts"]
        }
    }
    
    for approach, details in approaches.items():
        print(f"\n🎯 {approach}:")
        print(f"   Method: {details['method']}")
        print(f"   Trigger: {details['trigger']}")
        print(f"   ✅ Pros: {', '.join(details['pros'])}")
        print(f"   ❌ Cons: {', '.join(details['cons'])}")

def recommend_atr_take_profit_integration():
    """
    Recommend whether to integrate ATR take profit
    """
    
    print(f"\n🏆 ATR TAKE PROFIT RECOMMENDATION")
    print("=" * 60)
    
    print("📊 ANALYSIS:")
    print("-" * 20)
    print("✅ ATR take-profit more relevant than stop-loss for bull markets")
    print("✅ Could help lock in profits during pullbacks")
    print("✅ Complements our trend composite allocation system")
    print("✅ Addresses 'giving back profits' concern")
    print()
    
    print("🎯 RECOMMENDED HYBRID APPROACH:")
    print("-" * 50)
    print("1. 📊 KEEP: Current trend composite allocation system")
    print("2. 📈 ADD: ATR take-profit as profit protection overlay")
    print("3. 🔧 RULE: When position reaches +20% profit:")
    print("   • Set ATR trailing take-profit (2x ATR below highest)")
    print("   • If triggered → Exit completely, take profits") 
    print("   • Re-enter only on fresh trend composite signal")
    print()
    
    print("💡 IMPLEMENTATION EXAMPLE:")
    print("-" * 40)
    print("• TSLA enters at $200 with 80% allocation")
    print("• TSLA rises to $240 (+20% profit)")
    print("• Set ATR take-profit: $240 - (2 × ATR) = ~$220")
    print("• TSLA rises to $260, ATR trails to ~$235") 
    print("• TSLA pulls back to $235 → EXIT, lock profit")
    print("• Wait for new trend composite entry signal")
    print()
    
    print("🚀 EXPECTED BENEFITS:")
    print("-" * 30)
    print("• Lock in profits during pullbacks")
    print("• Reduce 'giving back gains' problem")
    print("• Maintain trend-following approach")
    print("• Clear profit-taking discipline")
    print()
    
    print("🔍 NEXT STEPS:")
    print("-" * 20) 
    print("1. Backtest ATR take-profit overlay")
    print("2. Test different profit thresholds (15%, 20%, 25%)")
    print("3. Optimize ATR multiplier for take-profit (1.5x, 2x, 2.5x)")
    print("4. Compare vs pure trend composite approach")

def main():
    """
    Complete ATR take-profit analysis
    """
    
    analyze_atr_take_profit_concept()
    simulate_atr_take_profit_example()
    compare_take_profit_approaches()
    recommend_atr_take_profit_integration()
    
    print(f"\n🎯 BOTTOM LINE:")
    print("-" * 30)
    print("ATR TAKE-PROFIT makes more sense than ATR stop-loss")
    print("for our bull market trend-following strategy!")
    print("Let's backtest this approach next.")

if __name__ == "__main__":
    main()