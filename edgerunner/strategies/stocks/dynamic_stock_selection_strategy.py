#!/usr/bin/env python3
"""
Dynamic Stock Selection Strategy Analysis
Should we rotate stocks based on momentum/trend criteria vs fixed portfolio?

Current Approach: Fixed 3 stocks (AMZN, TSLA, RBLX) with trend composite allocation
Alternative: Dynamic rotation based on momentum ranking + trend composite
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DynamicStockSelection:
    """
    Analyze current fixed vs dynamic stock selection approaches
    """
    
    def __init__(self, capital=5000, max_positions=3):
        self.capital = capital
        self.max_positions = max_positions
        
        # Current fixed portfolio
        self.fixed_stocks = ['AMZN', 'TSLA', 'RBLX']
        
        # Extended candidate universe for dynamic selection
        self.candidate_universe = [
            # Current portfolio
            'AMZN', 'TSLA', 'RBLX',
            # AI/Tech leaders
            'NVDA', 'META', 'GOOGL', 'MSFT', 'AAPL',
            # Growth stocks
            'AMD', 'PLTR', 'COIN', 'CRSP', 'MRNA',
            # Additional momentum candidates
            'NFLX', 'CRM', 'SHOP', 'SQ', 'ROKU'
        ]

    def analyze_current_fixed_approach(self):
        """
        Analyze why we selected AMZN, TSLA, RBLX specifically
        """
        
        print("🔍 CURRENT FIXED STOCK SELECTION ANALYSIS")
        print("=" * 80)
        print("📊 Fixed Portfolio: AMZN, TSLA, RBLX")
        print("💰 Allocation: $1,667 per stock (33.3% each)")
        print()
        
        selection_rationale = {
            'AMZN': {
                'sector': 'Cloud/E-commerce',
                'market_cap': '$1.8T',
                'rationale': [
                    '✅ Mega-cap stability with growth potential',
                    '✅ Strong technical trend patterns',
                    '✅ Lower volatility vs pure growth plays',
                    '✅ Institutional favorite with high liquidity',
                    '✅ Multiple business segments (AWS, retail, ads)'
                ]
            },
            'TSLA': {
                'sector': 'EV/Autonomous',
                'market_cap': '$800B',
                'rationale': [
                    '✅ High volatility creates clear trend signals',
                    '✅ Strong momentum history (capable of 100%+ moves)',
                    '✅ Responds well to technical analysis',
                    '✅ Different sector exposure vs AMZN',
                    '✅ High retail/institutional interest'
                ]
            },
            'RBLX': {
                'sector': 'Gaming/Metaverse',
                'market_cap': '$30B',
                'rationale': [
                    '✅ Highest volatility (best for trend composite)',
                    '✅ Emerging growth story in gaming/metaverse',
                    '✅ Different sector vs AMZN/TSLA',
                    '✅ Strong momentum potential (+190% in backtest)',
                    '✅ Lower correlation with traditional tech'
                ]
            }
        }
        
        print("📋 STOCK SELECTION RATIONALE:")
        print("-" * 80)
        
        for stock, info in selection_rationale.items():
            print(f"\n🎯 {stock} ({info['sector']}) - {info['market_cap']}")
            for reason in info['rationale']:
                print(f"   {reason}")
        
        print(f"\n🎯 PORTFOLIO CONSTRUCTION LOGIC:")
        print("-" * 50)
        print("1. 🏢 SECTOR DIVERSIFICATION:")
        print("   • AMZN: Cloud/E-commerce (stable growth)")
        print("   • TSLA: EV/Autonomous (cyclical growth)")  
        print("   • RBLX: Gaming/Metaverse (emerging growth)")
        print()
        print("2. 📊 VOLATILITY SPECTRUM:")
        print("   • AMZN: ~31% volatility (moderate)")
        print("   • TSLA: ~64% volatility (high)")
        print("   • RBLX: ~48% volatility (high)")
        print()
        print("3. 💰 MARKET CAP DIVERSIFICATION:")
        print("   • AMZN: Mega-cap ($1.8T)")
        print("   • TSLA: Large-cap ($800B)")
        print("   • RBLX: Mid-cap ($30B)")
        print()
        print("4. 🎯 TREND COMPOSITE COMPATIBILITY:")
        print("   • All respond well to technical analysis")
        print("   • High liquidity (>10M daily volume)")
        print("   • Clear breakout/breakdown patterns")
        print("   • Strong institutional following")

    def analyze_momentum_rotation_approach(self):
        """
        Analyze alternative: rotate stocks based on momentum ranking
        """
        
        print(f"\n🔄 DYNAMIC MOMENTUM ROTATION ANALYSIS")
        print("=" * 80)
        print("🎯 Alternative Approach: Monthly stock rotation based on momentum")
        print("📊 Universe: 15 stocks, select top 3 each month")
        print()
        
        print("📋 DYNAMIC SELECTION CRITERIA:")
        print("-" * 50)
        print("1. 🚀 MOMENTUM RANKING:")
        print("   • Calculate 6-month momentum for all candidates")
        print("   • Rank by (Price_now / Price_6mo_ago) - 1")
        print("   • Select top 3 momentum leaders")
        print()
        print("2. 📊 MINIMUM REQUIREMENTS:")
        print("   • Market cap > $10B (liquidity)")
        print("   • Average volume > 5M shares")
        print("   • Price > $20 (avoid penny stocks)")
        print("   • Positive 6-month momentum")
        print()
        print("3. 🔄 REBALANCING FREQUENCY:")
        print("   • Monthly stock selection review")
        print("   • Change stocks if new ones rank higher")
        print("   • Apply trend composite to selected stocks")
        print()
        
        print("✅ POTENTIAL ADVANTAGES:")
        print("-" * 40)
        print("• Always hold the 3 strongest momentum stocks")
        print("• Captures rotating sector leadership")
        print("• Avoids stagnant/declining stocks")
        print("• Nick Radge approach: momentum + trend following")
        print("• Could catch breakout stocks early")
        print()
        
        print("⚠️ POTENTIAL DISADVANTAGES:")
        print("-" * 40)
        print("• High portfolio turnover (transaction costs)")
        print("• May buy at momentum peaks")
        print("• Less predictable/testable")
        print("• Complexity in implementation")
        print("• Could miss mean reversion opportunities")

    def backtest_momentum_rotation_concept(self, lookback_period=126):
        """
        Simulate what momentum rotation would look like (conceptual)
        """
        
        print(f"\n📊 MOMENTUM ROTATION SIMULATION (Conceptual)")
        print("=" * 80)
        print("🗓️ Monthly selection of top 3 momentum stocks")
        print(f"📏 Momentum lookback: {lookback_period} days (6 months)")
        print()
        
        # Download data for candidate universe
        end_date = "2025-07-31"
        start_date = "2023-06-01"  # Need extra data for momentum calculation
        
        stock_data = {}
        
        print("📊 Downloading candidate stock data...")
        for stock in self.candidate_universe[:8]:  # Limit to 8 for demo
            try:
                ticker = yf.Ticker(stock)
                df = ticker.history(start=start_date, end=end_date)
                if not df.empty and len(df) > lookback_period:
                    stock_data[stock] = df['Close']
                    print(f"   ✅ {stock}: {len(df)} days")
                else:
                    print(f"   ❌ {stock}: Insufficient data")
            except Exception as e:
                print(f"   ❌ {stock}: Error - {e}")
        
        if len(stock_data) < 3:
            print("❌ Need at least 3 stocks with data")
            return
        
        # Calculate monthly momentum rankings
        monthly_selections = []
        
        # Create monthly date range for 2024-2025 period
        analysis_start = "2024-01-01"
        monthly_dates = pd.date_range(start=analysis_start, end=end_date, freq='MS')  # Month start
        
        print(f"\n📈 MONTHLY MOMENTUM RANKINGS:")
        print("-" * 80)
        
        for month_date in monthly_dates[:6]:  # Show first 6 months
            month_str = month_date.strftime('%Y-%m')
            
            # Calculate momentum for each stock on this date
            momentum_scores = {}
            
            for stock, prices in stock_data.items():
                # Find price on this date and 6 months ago
                try:
                    current_idx = prices.index[prices.index <= month_date][-1]
                    past_idx = prices.index[prices.index <= (month_date - timedelta(days=lookback_period))][-1]
                    
                    current_price = prices[current_idx]
                    past_price = prices[past_idx]
                    
                    momentum = (current_price / past_price) - 1
                    momentum_scores[stock] = momentum
                    
                except (IndexError, KeyError):
                    continue
            
            # Rank by momentum
            ranked_stocks = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)
            top_3 = ranked_stocks[:3]
            
            print(f"{month_str}:")
            print(f"   Top 3: {', '.join([f'{stock} ({score:+.1%})' for stock, score in top_3])}")
            
            monthly_selections.append({
                'month': month_str,
                'selections': [stock for stock, _ in top_3],
                'momentum_scores': dict(top_3)
            })
        
        print("   ...")
        print()
        
        # Analysis of selection stability
        all_selections = []
        for selection in monthly_selections:
            all_selections.extend(selection['selections'])
        
        from collections import Counter
        selection_frequency = Counter(all_selections)
        
        print("🔄 STOCK ROTATION FREQUENCY:")
        print("-" * 50)
        for stock, count in selection_frequency.most_common():
            pct = count / len(monthly_selections) * 100
            print(f"{stock:6}: {count}/{len(monthly_selections)} months ({pct:.0f}%)")
        
        # Compare to fixed approach
        fixed_in_rotation = sum(1 for stock in self.fixed_stocks if stock in selection_frequency)
        print(f"\nFixed portfolio overlap: {fixed_in_rotation}/3 stocks would be selected by momentum")
        
        return monthly_selections

    def recommend_approach(self):
        """
        Recommend fixed vs dynamic approach
        """
        
        print(f"\n🎯 RECOMMENDATION: FIXED vs DYNAMIC APPROACH")
        print("=" * 80)
        
        print("📊 CURRENT FIXED APPROACH STRENGTHS:")
        print("-" * 50)
        print("✅ Consistent, testable strategy")
        print("✅ Lower transaction costs")
        print("✅ Sector diversification maintained")
        print("✅ Known risk characteristics")
        print("✅ Focus on trend composite optimization")
        print("✅ Simpler implementation for $5K account")
        print()
        
        print("🔄 DYNAMIC ROTATION POTENTIAL:")
        print("-" * 50)
        print("✅ Could capture stronger momentum stocks")
        print("✅ Avoids holding declining stocks")
        print("✅ More aligned with Nick Radge philosophy")
        print("❌ Higher complexity and turnover")
        print("❌ Transaction costs with $5K account")
        print("❌ Harder to backtest reliably")
        print()
        
        print("🏆 RECOMMENDED APPROACH FOR $5K ACCOUNT:")
        print("-" * 60)
        print("HYBRID: Fixed portfolio with momentum filter")
        print()
        print("1. 📊 CORE APPROACH:")
        print("   • Keep AMZN, TSLA, RBLX as base portfolio")
        print("   • Apply trend composite allocation as current")
        print()
        print("2. 🚀 MOMENTUM FILTER:")
        print("   • Only allocate to stocks with positive 6-month momentum")
        print("   • If stock has negative momentum, force allocation to 0%")
        print("   • Redistribute capital to positive momentum stocks")
        print()
        print("3. 🔄 QUARTERLY REVIEW:")
        print("   • Every 3 months, check if any stock should be replaced")
        print("   • Replace only if new candidate has 20%+ higher momentum")
        print("   • Maintain sector diversification")
        print()
        print("4. 📈 POSITION SIZING:")
        print("   • Weight allocation by relative momentum strength")
        print("   • Strongest momentum stock gets larger base allocation")
        print()
        
        return "hybrid_momentum_filter"

def run_selection_strategy_analysis():
    """
    Run complete analysis of stock selection approaches
    """
    
    analyzer = DynamicStockSelection(capital=5000, max_positions=3)
    
    # Analyze current fixed approach
    analyzer.analyze_current_fixed_approach()
    
    # Analyze dynamic rotation
    analyzer.analyze_momentum_rotation_approach()
    
    # Simulate momentum rotation
    monthly_selections = analyzer.backtest_momentum_rotation_concept()
    
    # Get recommendation
    recommendation = analyzer.recommend_approach()
    
    print(f"\n💡 IMPLEMENTATION PRIORITY:")
    print("-" * 50)
    print("1. 🎯 IMMEDIATE: Stick with fixed AMZN/TSLA/RBLX")
    print("2. ⚡ ENHANCEMENT: Add momentum filter to current strategy")
    print("3. 📊 FUTURE: Test quarterly stock rotation with larger capital")
    print("4. 🔄 ADVANCED: Full dynamic rotation when capital > $25K")
    
    return recommendation

if __name__ == "__main__":
    recommendation = run_selection_strategy_analysis()