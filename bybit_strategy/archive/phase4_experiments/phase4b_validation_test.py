#!/usr/bin/env python3
"""
Phase 4B Validation Test - Volatility Regime Adaptation
Test dynamic parameter scaling based on market volatility conditions

VALIDATION FOCUS:
✅ Volatility regime detection is working (high/medium/low)
✅ Parameter scaling adjustments are being applied
✅ Signal and position sizing modifications are active  
✅ Performance improvements across different volatility periods
✅ Breakout detection during volatility regime transitions

Expected Outcome: 10-25% improvement through better volatility adaptation
"""

from datetime import datetime, timedelta
import pandas as pd
from xrpusdt_phase4b_volatility_strategy import XRPUSDT_Phase4B_Strategy
from xrpusdt_1h_enhanced_strategy_saved import XRPUSDT1HEnhancedStrategy

def run_phase4b_validation():
    """Run comprehensive Phase 4B volatility adaptation validation"""
    
    print("🌊 PHASE 4B VALIDATION - Volatility Regime Adaptation")
    print("=" * 80)
    print("Testing dynamic volatility adaptation against Phase 3 baseline")
    print("Focus: Different volatility periods and regime transitions")
    print()
    
    # Test periods chosen for different volatility characteristics
    test_periods = [
        # High volatility period (crypto volatility spike)
        ("High Volatility Period", datetime(2024, 3, 1), datetime(2024, 5, 31)),
        # Mixed volatility with transitions
        ("Mixed Volatility Period", datetime(2024, 8, 1), datetime(2024, 10, 31)),
        # Bull run volatility (should be medium-high)  
        ("Bull Run Period", datetime(2024, 11, 1), datetime(2024, 12, 31))
    ]
    
    all_results = []
    
    for period_name, start_date, end_date in test_periods:
        print(f"🧪 TESTING {period_name.upper()}")
        print("-" * 60)
        
        try:
            # Phase 3 Baseline Test
            print("1️⃣ Running Phase 3 baseline...")
            phase3_strategy = XRPUSDT1HEnhancedStrategy(10000, 'aggressive')
            phase3_df = phase3_strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
            
            phase3_final_balance = phase3_strategy.current_balance
            phase3_return = ((phase3_final_balance - 10000) / 10000) * 100
            phase3_trades = len([t for t in phase3_strategy.trades if t['action'] == 'CLOSE'])
            
            print(f"   ✅ Phase 3: {phase3_return:+.1f}% (${phase3_final_balance:,.0f}, {phase3_trades} trades)")
            
            # Phase 4B Volatility Test
            print("2️⃣ Running Phase 4B volatility adaptation...")
            phase4b_strategy = XRPUSDT_Phase4B_Strategy(10000, 'aggressive')
            phase4b_df = phase4b_strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
            
            phase4b_final_balance = phase4b_strategy.current_balance
            phase4b_return = ((phase4b_final_balance - 10000) / 10000) * 100
            phase4b_trades = len([t for t in phase4b_strategy.trades if t['action'] == 'CLOSE'])
            
            print(f"   ✅ Phase 4B: {phase4b_return:+.1f}% (${phase4b_final_balance:,.0f}, {phase4b_trades} trades)")
            
            # Calculate improvement
            return_improvement = phase4b_return - phase3_return
            balance_improvement = phase4b_final_balance - phase3_final_balance
            
            # Phase 4B Diagnostic Information
            print(f"\n   📊 PHASE 4B VOLATILITY DIAGNOSTICS:")
            print(f"      - Volatility Analysis Calls: {phase4b_strategy.volatility_analysis_calls}")
            print(f"      - Volatility Adjustments: {phase4b_strategy.volatility_adjustments_made}")
            print(f"      - Current Vol Regime: {phase4b_strategy.current_volatility_regime.upper()}")
            print(f"      - Last Vol Measurement: {phase4b_strategy.last_volatility_measurement*100:.1f}%")
            print(f"      - Activity Logs: {len(phase4b_strategy.phase4b_logs)}")
            
            # Analyze volatility regime distribution
            if phase4b_strategy.volatility_cache:
                regimes = [entry['regime'] for entry in phase4b_strategy.volatility_cache.values()]
                regime_counts = {}
                for regime in regimes:
                    regime_counts[regime] = regime_counts.get(regime, 0) + 1
                
                total_measurements = len(regimes)
                print(f"      - Volatility Measurements: {total_measurements}")
                
                if regime_counts:
                    print(f"      - Regime Distribution:")
                    for regime, count in regime_counts.items():
                        percentage = (count / total_measurements) * 100
                        print(f"        {regime.upper()}: {count} times ({percentage:.1f}%)")
            
            # Performance comparison
            print(f"\n   🎯 IMPROVEMENT ANALYSIS:")
            print(f"      - Return Improvement: {return_improvement:+.2f} percentage points")
            print(f"      - Balance Improvement: ${balance_improvement:+,.0f}")
            print(f"      - Trade Count Change: {phase4b_trades - phase3_trades:+d} trades")
            
            # Determine status
            if return_improvement > 5:
                print(f"      🚀 EXCELLENT IMPROVEMENT: Phase 4B shows strong gains!")
                status = "EXCELLENT"
            elif return_improvement > 2:
                print(f"      ✅ GOOD IMPROVEMENT: Phase 4B shows meaningful gains")
                status = "GOOD"
            elif return_improvement > 0.5:
                print(f"      🔄 MODEST IMPROVEMENT: Phase 4B shows some gains")
                status = "MODEST"
            elif return_improvement > -0.5:
                print(f"      ⚖️ SIMILAR PERFORMANCE: No significant difference")
                status = "SIMILAR"
            else:
                print(f"      ⚠️ UNDERPERFORMANCE: Phase 4B needs refinement")
                status = "WORSE"
            
            # Store results
            result = {
                'period': period_name,
                'phase3_return': phase3_return,
                'phase4b_return': phase4b_return,
                'improvement': return_improvement,
                'phase3_trades': phase3_trades,
                'phase4b_trades': phase4b_trades,
                'vol_calls': phase4b_strategy.volatility_analysis_calls,
                'vol_adjustments': phase4b_strategy.volatility_adjustments_made,
                'current_regime': phase4b_strategy.current_volatility_regime,
                'last_vol': phase4b_strategy.last_volatility_measurement,
                'status': status,
                'regime_counts': regime_counts if 'regime_counts' in locals() else {}
            }
            
            all_results.append(result)
            print()
            
        except Exception as e:
            print(f"   ❌ Error testing {period_name}: {str(e)[:100]}")
            result = {'period': period_name, 'status': 'ERROR', 'error': str(e)}
            all_results.append(result)
            print()
    
    # Generate comprehensive validation report
    print("=" * 80)
    generate_phase4b_validation_report(all_results)

def generate_phase4b_validation_report(results):
    """Generate comprehensive Phase 4B validation report"""
    
    print("📊 PHASE 4B VALIDATION REPORT - Volatility Regime Adaptation")
    print("=" * 70)
    
    # Results table
    print("| Test Period | Phase 3 | Phase 4B | Improvement | Vol Calls | Adjustments | Final Regime | Status |")
    print("|-------------|---------|----------|-------------|-----------|-------------|--------------|---------|")
    
    successful_results = [r for r in results if r['status'] != 'ERROR']
    total_improvement = 0
    
    for result in results:
        if result['status'] != 'ERROR':
            period = result['period'][:11]  # Truncate for table
            phase3_ret = result['phase3_return']
            phase4b_ret = result['phase4b_return']
            improvement = result['improvement']
            vol_calls = result['vol_calls']
            adjustments = result['vol_adjustments']
            regime = result['current_regime'][:3].upper()
            status = result['status'][:4]
            
            print(f"| {period:<11} | {phase3_ret:+5.1f}% | {phase4b_ret:+6.1f}% | {improvement:+6.2f}% | {vol_calls:>6} | {adjustments:>6} | {regime:>6} | {status} |")
            total_improvement += improvement
        else:
            period = result['period'][:11]
            print(f"| {period:<11} | ERROR | ERROR | ERROR | ERROR | ERROR | ERROR | ERROR |")
    
    print()
    
    if successful_results:
        avg_improvement = total_improvement / len(successful_results)
        
        print("🎯 VALIDATION RESULTS:")
        print(f"- Average Improvement: {avg_improvement:+.2f} percentage points")
        print(f"- Successful Tests: {len(successful_results)}/{len(results)}")
        
        # Analyze volatility detection effectiveness
        total_vol_calls = sum(r['vol_calls'] for r in successful_results)
        total_adjustments = sum(r['vol_adjustments'] for r in successful_results)
        adjustment_rate = (total_adjustments / total_vol_calls * 100) if total_vol_calls > 0 else 0
        
        print(f"- Total Volatility Analyses: {total_vol_calls:,}")
        print(f"- Total Parameter Adjustments: {total_adjustments}")
        print(f"- Adjustment Rate: {adjustment_rate:.1f}%")
        
        # Analyze regime distribution across all tests
        all_regime_counts = {}
        for result in successful_results:
            for regime, count in result.get('regime_counts', {}).items():
                all_regime_counts[regime] = all_regime_counts.get(regime, 0) + count
        
        if all_regime_counts:
            total_regime_measurements = sum(all_regime_counts.values())
            print(f"- Total Regime Measurements: {total_regime_measurements}")
            print("- Overall Regime Distribution:")
            for regime, count in all_regime_counts.items():
                percentage = (count / total_regime_measurements) * 100
                print(f"  {regime.upper()}: {count} ({percentage:.1f}%)")
        
        print()
        print("🔍 IMPLEMENTATION VERIFICATION:")
        if total_vol_calls > 0:
            print("✅ Volatility analysis is working (analysis calls > 0)")
        else:
            print("❌ Volatility analysis not triggering")
            
        if total_adjustments > 0:
            print("✅ Parameter adjustments are being applied")
        else:
            print("⚠️ No parameter adjustments detected")
            
        if adjustment_rate > 20:
            print("✅ High adjustment rate - volatility adaptation is very active")
        elif adjustment_rate > 10:
            print("✅ Good adjustment rate - volatility adaptation is active")
        elif adjustment_rate > 5:
            print("🔄 Moderate adjustment rate - some volatility adaptation")
        else:
            print("⚠️ Low adjustment rate - limited volatility response")
        
        print()
        print("🚀 OVERALL PHASE 4B ASSESSMENT:")
        
        if avg_improvement > 10:
            print("🎉 **OUTSTANDING**: Phase 4B shows exceptional improvement!")
            print("   → Volatility adaptation is highly effective")
            print("   → Ready for production deployment")
            print("   → Consider Phase 4C: Momentum enhancement")
            
        elif avg_improvement > 5:
            print("🚀 **EXCELLENT**: Phase 4B shows significant improvement!")
            print("   → Volatility regime adaptation working well")
            print("   → Validate on additional periods for confirmation")
            
        elif avg_improvement > 2:
            print("✅ **GOOD**: Phase 4B shows meaningful improvement!")
            print("   → Volatility adaptation providing benefits")
            print("   → Fine-tune regime thresholds if needed")
            
        elif avg_improvement > 0.5:
            print("🔄 **MARGINAL**: Phase 4B shows modest improvement")
            print("   → Consider more aggressive parameter differences")
            print("   → Test longer periods for better evaluation")
            
        elif avg_improvement > -0.5:
            print("⚖️ **SIMILAR**: No significant difference from Phase 3")
            print("   → Volatility adaptation may need refinement")
            print("   → Consider different volatility thresholds")
            
        else:
            print("⚠️ **NEEDS WORK**: Phase 4B underperformed Phase 3")
            print("   → Review volatility regime logic")
            print("   → Check parameter scaling effectiveness")
        
        print()
        
        # Technical recommendations
        print("🛠️ TECHNICAL RECOMMENDATIONS:")
        
        if total_adjustments == 0:
            print("- NO ADJUSTMENTS: Volatility regime detection may be too conservative")
            print("- Consider lowering volatility thresholds (currently 20%/50%)")
            print("- Try thresholds of 15%/40% for more sensitive regime detection")
            
        elif adjustment_rate < 10:
            print("- LOW ADJUSTMENT RATE: Most conditions falling in medium regime")
            print("- Consider more granular regime classification")
            print("- Add intermediate regimes (low-medium, medium-high)")
            
        if avg_improvement < 2:
            print("- LIMITED IMPROVEMENT: Parameter scaling may be too conservative")
            print("- Consider more aggressive multipliers:")
            print("  High vol: 2.0x position size (currently 1.5x)")
            print("  Low vol: 0.6x position size (currently 0.8x)")
            
        # Regime-specific analysis
        if all_regime_counts:
            high_vol_percentage = all_regime_counts.get('high', 0) / total_regime_measurements * 100
            low_vol_percentage = all_regime_counts.get('low', 0) / total_regime_measurements * 100
            
            if high_vol_percentage < 10:
                print("- LOW HIGH-VOLATILITY DETECTION: May miss aggressive opportunities")
                print("- Consider lowering high volatility threshold (currently 50%)")
                
            if low_vol_percentage < 10:
                print("- LOW LOW-VOLATILITY DETECTION: May miss conservative periods")
                print("- Consider raising low volatility threshold (currently 20%)")
    
    else:
        print("❌ No successful tests completed - implementation has critical issues")
    
    print()
    print("=" * 80)
    print("✅ Phase 4B volatility adaptation validation complete!")
    print("=" * 80)

if __name__ == "__main__":
    run_phase4b_validation()