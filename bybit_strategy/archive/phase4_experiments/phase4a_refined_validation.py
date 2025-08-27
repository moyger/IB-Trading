#!/usr/bin/env python3
"""
Phase 4A Refined Validation Test
Test the fixed multi-timeframe trend context implementation

VALIDATION FOCUS:
✅ Multi-timeframe trend detection is working
✅ Position sizing adjustments are being applied
✅ Signal threshold modifications are active
✅ Performance improvements are measurable

Expected Outcome: 5-15% improvement over Phase 3 baseline
"""

from datetime import datetime, timedelta
import pandas as pd
from xrpusdt_phase4a_refined_strategy import XRPUSDT_Phase4A_Refined_Strategy
from xrpusdt_1h_enhanced_strategy_saved import XRPUSDT1HEnhancedStrategy

def run_refined_phase4a_validation():
    """Run validation of refined Phase 4A with detailed diagnostics"""
    
    print("🔧 PHASE 4A REFINED VALIDATION - Fixed Multi-Timeframe Analysis")
    print("=" * 80)
    print("Testing fixed implementation against Phase 3 baseline")
    print("Focus: Verify trend detection and position adjustments are working")
    print()
    
    # Test on a shorter, more controlled period first
    test_periods = [
        ("Q1 2024 Focus Test", datetime(2024, 1, 1), datetime(2024, 3, 31)),
        ("Bull Run Test", datetime(2024, 10, 1), datetime(2024, 12, 31))
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
            
            # Phase 4A Refined Test  
            print("2️⃣ Running Phase 4A refined...")
            phase4a_strategy = XRPUSDT_Phase4A_Refined_Strategy(10000, 'aggressive')
            phase4a_df = phase4a_strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
            
            phase4a_final_balance = phase4a_strategy.current_balance
            phase4a_return = ((phase4a_final_balance - 10000) / 10000) * 100
            phase4a_trades = len([t for t in phase4a_strategy.trades if t['action'] == 'CLOSE'])
            
            print(f"   ✅ Phase 4A: {phase4a_return:+.1f}% (${phase4a_final_balance:,.0f}, {phase4a_trades} trades)")
            
            # Calculate improvement
            return_improvement = phase4a_return - phase3_return
            balance_improvement = phase4a_final_balance - phase3_final_balance
            
            # Diagnostic information
            print(f"\n   📊 PHASE 4A DIAGNOSTICS:")
            print(f"      - Trend Analysis Calls: {phase4a_strategy.trend_analysis_calls}")
            print(f"      - Position Adjustments: {phase4a_strategy.trend_adjustments_made}")
            print(f"      - Cache Entries: {len(phase4a_strategy.trend_analysis_cache)}")
            print(f"      - Activity Logs: {len(phase4a_strategy.phase4a_logs)}")
            
            # Trend detection analysis
            if phase4a_strategy.trend_analysis_cache:
                alignments = [entry['analysis']['alignment'] 
                            for entry in phase4a_strategy.trend_analysis_cache.values()]
                mixed_count = alignments.count('mixed')
                total_analyses = len(alignments)
                mixed_percentage = (mixed_count / total_analyses) * 100
                
                print(f"      - Mixed Conditions: {mixed_percentage:.1f}% ({mixed_count}/{total_analyses})")
                
                # Show non-mixed detections
                non_mixed = [a for a in alignments if a != 'mixed']
                if non_mixed:
                    alignment_counts = {}
                    for alignment in non_mixed:
                        alignment_counts[alignment] = alignment_counts.get(alignment, 0) + 1
                    
                    print(f"      - Trend Detections:")
                    for alignment, count in alignment_counts.items():
                        print(f"        {alignment}: {count} times")
            
            # Performance comparison
            print(f"\n   🎯 IMPROVEMENT ANALYSIS:")
            print(f"      - Return Improvement: {return_improvement:+.2f} percentage points")
            print(f"      - Balance Improvement: ${balance_improvement:+,.0f}")
            
            if return_improvement > 2:
                print(f"      ✅ MEANINGFUL IMPROVEMENT: Phase 4A shows clear gains!")
                status = "SUCCESS"
            elif return_improvement > 0.5:
                print(f"      🔄 MODEST IMPROVEMENT: Phase 4A shows some gains")
                status = "MARGINAL"  
            elif return_improvement > -0.5:
                print(f"      ⚖️ SIMILAR PERFORMANCE: No significant difference")
                status = "SIMILAR"
            else:
                print(f"      ⚠️ UNDERPERFORMANCE: Phase 4A needs further refinement")
                status = "WORSE"
            
            # Store results
            result = {
                'period': period_name,
                'phase3_return': phase3_return,
                'phase4a_return': phase4a_return,
                'improvement': return_improvement,
                'trend_calls': phase4a_strategy.trend_analysis_calls,
                'adjustments': phase4a_strategy.trend_adjustments_made,
                'status': status,
                'mixed_percentage': mixed_percentage if 'mixed_percentage' in locals() else 100
            }
            
            all_results.append(result)
            print()
            
        except Exception as e:
            print(f"   ❌ Error testing {period_name}: {str(e)[:100]}")
            result = {'period': period_name, 'status': 'ERROR', 'error': str(e)}
            all_results.append(result)
            print()
    
    # Generate comprehensive report
    print("=" * 80)
    generate_refined_validation_report(all_results)

def generate_refined_validation_report(results):
    """Generate comprehensive validation report for refined Phase 4A"""
    
    print("📊 PHASE 4A REFINED VALIDATION REPORT")
    print("=" * 60)
    
    # Results table
    print("| Test Period | Phase 3 | Phase 4A | Improvement | Trend Calls | Adjustments | Status |")
    print("|-------------|---------|-----------|-------------|-------------|-------------|---------|")
    
    successful_results = [r for r in results if r['status'] != 'ERROR']
    total_improvement = 0
    
    for result in results:
        if result['status'] != 'ERROR':
            period = result['period']
            phase3_ret = result['phase3_return']
            phase4a_ret = result['phase4a_return']
            improvement = result['improvement']
            trend_calls = result['trend_calls']
            adjustments = result['adjustments']
            status = result['status']
            
            print(f"| {period:<11} | {phase3_ret:+5.1f}% | {phase4a_ret:+6.1f}% | {improvement:+6.2f}% | {trend_calls:>6} | {adjustments:>6} | {status} |")
            total_improvement += improvement
        else:
            print(f"| {result['period']:<11} | ERROR | ERROR | ERROR | ERROR | ERROR | ERROR |")
    
    print()
    
    if successful_results:
        avg_improvement = total_improvement / len(successful_results)
        
        print("🎯 VALIDATION RESULTS:")
        print(f"- Average Improvement: {avg_improvement:+.2f} percentage points")
        print(f"- Successful Tests: {len(successful_results)}/{len(results)}")
        
        # Analyze trend detection effectiveness
        total_trend_calls = sum(r['trend_calls'] for r in successful_results)
        total_adjustments = sum(r['adjustments'] for r in successful_results)
        adjustment_rate = (total_adjustments / total_trend_calls * 100) if total_trend_calls > 0 else 0
        
        print(f"- Total Trend Analyses: {total_trend_calls:,}")
        print(f"- Total Position Adjustments: {total_adjustments}")
        print(f"- Adjustment Rate: {adjustment_rate:.1f}%")
        
        avg_mixed = sum(r.get('mixed_percentage', 100) for r in successful_results) / len(successful_results)
        print(f"- Average Mixed Conditions: {avg_mixed:.1f}%")
        
        print()
        print("🔍 IMPLEMENTATION VERIFICATION:")
        if total_trend_calls > 0:
            print("✅ Multi-timeframe analysis is working (trend calls > 0)")
        else:
            print("❌ Multi-timeframe analysis not triggering")
            
        if total_adjustments > 0:
            print("✅ Position adjustments are being applied")
        else:
            print("⚠️ No position adjustments detected")
            
        if adjustment_rate > 10:
            print("✅ Good adjustment rate - trend detection is active")
        elif adjustment_rate > 5:
            print("🔄 Moderate adjustment rate - some trend detection")
        else:
            print("⚠️ Low adjustment rate - mostly mixed conditions")
        
        print()
        print("🚀 OVERALL ASSESSMENT:")
        
        if avg_improvement > 5:
            print("🎉 **EXCELLENT**: Phase 4A refined shows significant improvement!")
            print("   → Ready for production deployment")
            print("   → Consider Phase 4B: Volatility regime adaptation")
            
        elif avg_improvement > 2:
            print("✅ **GOOD**: Phase 4A refined shows meaningful improvement!")
            print("   → Validate on additional test periods")
            print("   → Fine-tune multiplier values if needed")
            
        elif avg_improvement > 0.5:
            print("🔄 **MARGINAL**: Phase 4A refined shows modest improvement")
            print("   → Consider additional refinements")
            print("   → Test on different market conditions")
            
        elif avg_improvement > -0.5:
            print("⚖️ **SIMILAR**: No significant difference from Phase 3")
            print("   → May need more aggressive parameters")
            print("   → Consider different optimization approach")
            
        else:
            print("⚠️ **NEEDS WORK**: Phase 4A refined needs further development")
            print("   → Review trend detection logic")
            print("   → Check for implementation bugs")
        
        print()
        
        # Technical recommendations
        print("🛠️ TECHNICAL RECOMMENDATIONS:")
        
        if avg_mixed > 80:
            print("- HIGH MIXED CONDITIONS: Consider more sensitive trend thresholds")
            print("- Try strong_trend_threshold = 0.55 (currently 0.6)")
            print("- Try weak_trend_threshold = 0.45 (currently 0.4)")
            
        if adjustment_rate < 5:
            print("- LOW ADJUSTMENT RATE: Trend detection may be too conservative")
            print("- Consider more aggressive multiplier differences")
            
        if avg_improvement < 1:
            print("- MINIMAL IMPROVEMENT: May need additional features")
            print("- Consider momentum indicators (RSI, MACD)")
            print("- Consider breakout detection components")
    
    else:
        print("❌ No successful tests completed - implementation has critical issues")
    
    print()
    print("=" * 80)
    print("✅ Phase 4A refined validation complete!")
    print("=" * 80)

if __name__ == "__main__":
    run_refined_phase4a_validation()