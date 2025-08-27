#!/usr/bin/env python3
"""
Phase 4A Diagnostic Analysis
Understand why multi-timeframe analysis isn't triggering enhancements

This diagnostic will help identify:
1. Multi-timeframe trend detection frequency
2. Trend alignment patterns during the test period  
3. Position sizing multiplier distributions
4. Signal adjustment frequencies
5. Cache hit rates and analysis effectiveness
"""

from datetime import datetime, timedelta
import pandas as pd
from xrpusdt_phase4a_enhanced_strategy import XRPUSDT_Phase4A_Strategy
import yfinance as yf

def run_phase4a_diagnostic():
    """Run comprehensive diagnostic of Phase 4A multi-timeframe analysis"""
    
    print("🔍 PHASE 4A DIAGNOSTIC ANALYSIS - Multi-Timeframe Trend Detection")
    print("=" * 80)
    print("Analyzing why Phase 4A optimization isn't showing improvements")
    print("Period: January 2024 - March 2024 (3 months for detailed analysis)")
    print()
    
    # Create diagnostic strategy
    strategy = XRPUSDT_Phase4A_Strategy(10000, 'aggressive')
    
    # Test period - shorter for detailed analysis
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    
    print("📊 Running diagnostic backtest...")
    df = strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
    
    if df is None:
        print("❌ Failed to run diagnostic backtest")
        return
    
    print("✅ Diagnostic backtest completed")
    print()
    
    # Analyze trend detection patterns
    analyze_trend_patterns(strategy, df)
    
    # Analyze position sizing impacts
    analyze_position_sizing_impacts(strategy)
    
    # Analyze signal adjustments
    analyze_signal_adjustments(strategy)
    
    # Provide improvement recommendations
    provide_improvement_recommendations(strategy)

def analyze_trend_patterns(strategy, df):
    """Analyze multi-timeframe trend detection patterns"""
    
    print("📈 MULTI-TIMEFRAME TREND ANALYSIS DIAGNOSTIC")
    print("=" * 60)
    
    # Sample trend analyses from the cache
    if hasattr(strategy, 'trend_analysis_cache') and strategy.trend_analysis_cache:
        cache_entries = list(strategy.trend_analysis_cache.values())
        
        print(f"Cache Entries: {len(cache_entries)} trend analyses")
        print()
        
        # Analyze trend alignment distribution
        alignment_counts = {}
        multiplier_distribution = []
        timeframe_trends = {'1h': {}, '4h': {}, '1d': {}}
        
        for entry in cache_entries:
            analysis = entry['analysis']
            alignment = analysis['alignment']
            multiplier = analysis['position_multiplier']
            
            # Count alignments
            if alignment in alignment_counts:
                alignment_counts[alignment] += 1
            else:
                alignment_counts[alignment] = 1
            
            # Track multipliers
            multiplier_distribution.append(multiplier)
            
            # Track individual timeframe trends
            for tf, tf_data in analysis['timeframes'].items():
                direction = tf_data['direction']
                if direction in timeframe_trends[tf]:
                    timeframe_trends[tf][direction] += 1
                else:
                    timeframe_trends[tf][direction] = 1
        
        # Print alignment distribution
        print("🎯 TREND ALIGNMENT DISTRIBUTION:")
        total_analyses = len(cache_entries)
        for alignment, count in alignment_counts.items():
            percentage = (count / total_analyses) * 100
            multiplier = strategy.trend_alignment_multipliers.get(alignment, 1.0)
            print(f"- {alignment.upper()}: {count} times ({percentage:.1f}%) -> {multiplier:.1f}x multiplier")
        
        print()
        
        # Print individual timeframe trends
        print("📊 INDIVIDUAL TIMEFRAME TREND DISTRIBUTION:")
        for tf, trends in timeframe_trends.items():
            print(f"\n{tf.upper()} Timeframe:")
            total_tf = sum(trends.values())
            for direction, count in trends.items():
                percentage = (count / total_tf) * 100 if total_tf > 0 else 0
                print(f"  - {direction.upper()}: {count} ({percentage:.1f}%)")
        
        print()
        
        # Multiplier statistics
        if multiplier_distribution:
            avg_multiplier = sum(multiplier_distribution) / len(multiplier_distribution)
            max_multiplier = max(multiplier_distribution)
            min_multiplier = min(multiplier_distribution)
            
            print("🔢 POSITION MULTIPLIER STATISTICS:")
            print(f"- Average Multiplier: {avg_multiplier:.2f}x")
            print(f"- Max Multiplier: {max_multiplier:.1f}x")
            print(f"- Min Multiplier: {min_multiplier:.1f}x")
            print(f"- Standard Deviation: {pd.Series(multiplier_distribution).std():.2f}")
        
    else:
        print("❌ No trend analysis cache found - multi-timeframe analysis may not be triggering")
    
    print()

def analyze_position_sizing_impacts(strategy):
    """Analyze position sizing impacts from Phase 4A"""
    
    print("💰 POSITION SIZING IMPACT ANALYSIS")
    print("=" * 50)
    
    # Check if we have trade logs with Phase 4A adjustments
    if hasattr(strategy, 'trade_log') and strategy.trade_log:
        phase4a_adjustments = [log for log in strategy.trade_log 
                              if 'Phase 4A Multi-Timeframe' in log]
        
        print(f"Phase 4A Position Adjustments: {len(phase4a_adjustments)}")
        
        if phase4a_adjustments:
            print("\nSample Position Adjustments:")
            for i, log in enumerate(phase4a_adjustments[:5]):  # Show first 5
                print(f"  {i+1}. {log}")
            
            if len(phase4a_adjustments) > 5:
                print(f"  ... and {len(phase4a_adjustments) - 5} more")
        else:
            print("⚠️ No position size adjustments detected")
            print("   - All trend alignments may be resulting in 1.0x multiplier")
            print("   - Multi-timeframe analysis may be defaulting to 'mixed' conditions")
    else:
        print("❌ No trade log found - cannot analyze position sizing impacts")
    
    print()

def analyze_signal_adjustments(strategy):
    """Analyze signal threshold adjustments from Phase 4A"""
    
    print("📶 SIGNAL ADJUSTMENT ANALYSIS")
    print("=" * 40)
    
    # Check for signal adjustment logs
    if hasattr(strategy, 'trade_log') and strategy.trade_log:
        signal_adjustments = [log for log in strategy.trade_log 
                             if 'Phase 4A Signal Adjustment' in log]
        
        print(f"Signal Threshold Adjustments: {len(signal_adjustments)}")
        
        if signal_adjustments:
            print("\nSample Signal Adjustments:")
            for i, log in enumerate(signal_adjustments[:5]):  # Show first 5
                print(f"  {i+1}. {log}")
            
            if len(signal_adjustments) > 5:
                print(f"  ... and {len(signal_adjustments) - 5} more")
        else:
            print("⚠️ No signal threshold adjustments detected")
            print("   - All trend alignments may be resulting in 0 adjustment")
            print("   - Signal generation may not be benefiting from trend context")
    else:
        print("❌ No trade log found - cannot analyze signal adjustments")
    
    print()

def provide_improvement_recommendations(strategy):
    """Provide specific recommendations for Phase 4A improvement"""
    
    print("🛠️ PHASE 4A IMPROVEMENT RECOMMENDATIONS")
    print("=" * 50)
    
    # Analyze what we learned
    has_cache = hasattr(strategy, 'trend_analysis_cache') and strategy.trend_analysis_cache
    
    if has_cache:
        cache_entries = list(strategy.trend_analysis_cache.values())
        alignments = [entry['analysis']['alignment'] for entry in cache_entries]
        mixed_percentage = (alignments.count('mixed') / len(alignments)) * 100
        
        print("🔍 ROOT CAUSE ANALYSIS:")
        print(f"- Mixed/Neutral conditions: {mixed_percentage:.1f}% of the time")
        
        if mixed_percentage > 70:
            print("❗ HIGH MIXED CONDITIONS - This explains why Phase 4A shows no improvement")
            print()
            print("💡 RECOMMENDED FIXES:")
            print("1. **LOWER TREND THRESHOLDS**: Current strong_trend_threshold (0.7) may be too strict")
            print("   - Try 0.6 instead of 0.7 for more trend detection")
            print("   - Adjust weak_trend_threshold from 0.3 to 0.4")
            print()
            print("2. **ENHANCED TREND DETECTION**: Improve trend analysis methods")
            print("   - Add momentum indicators (RSI, MACD)")
            print("   - Include volume trend analysis")
            print("   - Consider breakout detection")
            print()
            print("3. **REFINED MULTIPLIERS**: Adjust trend alignment multipliers")
            print("   - Reduce 'mixed' multiplier to 0.9x (slight reduction for neutral)")
            print("   - Increase bullish multipliers to 2.0x and 1.6x")
            print("   - Add gradient between trend strengths")
            
        elif mixed_percentage > 50:
            print("⚠️ MODERATE MIXED CONDITIONS - Partial trend detection")
            print()
            print("💡 RECOMMENDED FIXES:")
            print("1. **GRADIENT MULTIPLIERS**: Instead of discrete steps, use continuous scaling")
            print("2. **TREND STRENGTH WEIGHTING**: Weight multipliers by trend strength")
            print("3. **VOLUME CONFIRMATION**: Add volume to trend strength calculation")
            
        else:
            print("✅ GOOD TREND DETECTION - Issue may be elsewhere")
            print()
            print("💡 INVESTIGATE:")
            print("1. **SIGNAL TIMING**: Check if signals align with trend changes")
            print("2. **RISK MANAGEMENT**: Verify if risk limits are constraining benefits")
            print("3. **MARKET CONDITIONS**: XRP may have been in unusual conditions")
    else:
        print("❌ NO TREND ANALYSIS CACHE - Multi-timeframe analysis not working")
        print()
        print("💡 CRITICAL FIXES NEEDED:")
        print("1. **DEBUG TREND ANALYSIS**: Check why analyze_multi_timeframe_trend() isn't caching")
        print("2. **DATA AVAILABILITY**: Verify sufficient historical data for analysis")
        print("3. **ERROR HANDLING**: Check for silent failures in trend calculation")
    
    print()
    print("🚀 NEXT IMPLEMENTATION PHASE:")
    print("1. **Phase 4A-Refined**: Implement the fixes above")
    print("2. **Phase 4B**: Move to volatility regime adaptation")
    print("3. **Phase 4C**: Implement momentum/breakout enhancements")
    print()
    print("🎯 SUCCESS METRICS:")
    print("- Target: 5-10% improvement over Phase 3")
    print("- Trend detection rate: >40% non-mixed conditions") 
    print("- Position multiplier variance: >0.15 standard deviation")
    
    print()
    print("=" * 80)
    print("✅ Phase 4A diagnostic complete - refinements identified!")
    print("=" * 80)

if __name__ == "__main__":
    run_phase4a_diagnostic()