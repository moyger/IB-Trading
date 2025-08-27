#!/usr/bin/env python3
"""
Enhanced Base Strategy Validation Test
Test signal generation fixes and measure increased trading activity

VALIDATION FOCUS:
✅ Significantly increased trading frequency (5-10x improvement)
✅ Signal generation is working (more signals, more trades)
✅ Risk management maintained despite increased activity
✅ Performance baseline established for Phase 4 deployment

Expected Outcomes:
- Trading activity: 20-60 trades/quarter (was 4-12)
- Signal generation: 5+ signals/week (was <1)
- Risk management: <5% monthly drawdowns maintained
- Performance: Match or exceed Phase 3 baseline
"""

from datetime import datetime, timedelta
import pandas as pd
from xrpusdt_enhanced_base_strategy import XRPUSDT_Enhanced_Base_Strategy
from xrpusdt_1h_enhanced_strategy_saved import XRPUSDT1HEnhancedStrategy

def run_enhanced_base_validation():
    """Validate enhanced base strategy improvements"""
    
    print("🔧 ENHANCED BASE VALIDATION - Signal Generation Overhaul")
    print("=" * 80)
    print("Testing signal generation fixes and trading activity improvements")
    print("Focus: Measure increased trading frequency and maintained risk management")
    print()
    
    # Test periods for trading activity analysis
    test_periods = [
        ("Q1 2024 Activity Test", datetime(2024, 1, 1), datetime(2024, 3, 31)),
        ("High Vol Period Test", datetime(2024, 3, 1), datetime(2024, 5, 31)),
        ("Bull Run Activity", datetime(2024, 11, 1), datetime(2024, 12, 31))
    ]
    
    all_results = []
    
    for period_name, start_date, end_date in test_periods:
        print(f"🧪 TESTING {period_name.upper()}")
        print("-" * 60)
        
        try:
            # Original Phase 3 Strategy (baseline)
            print("1️⃣ Running Phase 3 baseline...")
            phase3_strategy = XRPUSDT1HEnhancedStrategy(10000, 'aggressive')
            phase3_df = phase3_strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
            
            phase3_final_balance = phase3_strategy.current_balance
            phase3_return = ((phase3_final_balance - 10000) / 10000) * 100
            phase3_trades = len([t for t in phase3_strategy.trades if t['action'] == 'CLOSE'])
            
            print(f"   ✅ Phase 3: {phase3_return:+.1f}% (${phase3_final_balance:,.0f}, {phase3_trades} trades)")
            
            # Enhanced Base Strategy (signal generation fixes)
            print("2️⃣ Running enhanced base strategy...")
            enhanced_strategy = XRPUSDT_Enhanced_Base_Strategy(10000, 'aggressive')
            enhanced_df = enhanced_strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
            
            enhanced_final_balance = enhanced_strategy.current_balance
            enhanced_return = ((enhanced_final_balance - 10000) / 10000) * 100
            enhanced_trades = len([t for t in enhanced_strategy.trades if t['action'] == 'CLOSE'])
            
            print(f"   ✅ Enhanced: {enhanced_return:+.1f}% (${enhanced_final_balance:,.0f}, {enhanced_trades} trades)")
            
            # Calculate improvements
            return_improvement = enhanced_return - phase3_return
            balance_improvement = enhanced_final_balance - phase3_final_balance
            trade_count_improvement = enhanced_trades - phase3_trades
            trade_activity_multiplier = enhanced_trades / max(1, phase3_trades)
            
            # Enhanced Base Strategy Diagnostics
            print(f"\n   📊 ENHANCED BASE DIAGNOSTICS:")
            print(f"      - Signals Generated: {enhanced_strategy.signals_generated_today}")
            print(f"      - Trades Attempted: {enhanced_strategy.trades_attempted_today}")
            print(f"      - Enhanced Opportunities: {enhanced_strategy.enhanced_opportunities_captured}")
            print(f"      - Signal Generation Logs: {len(enhanced_strategy.signal_generation_logs)}")
            print(f"      - ADX Thresholds: {enhanced_strategy.adx_strong_threshold}/{enhanced_strategy.adx_weak_threshold}")
            print(f"      - Volume Multiplier: {enhanced_strategy.volume_multiplier:.2f}x")
            print(f"      - Min Signals Required: {enhanced_strategy.min_signals_to_trade}")
            
            # Trading Activity Analysis
            print(f"\n   🎯 TRADING ACTIVITY ANALYSIS:")
            print(f"      - Trade Count: {phase3_trades} → {enhanced_trades} ({trade_count_improvement:+d})")
            print(f"      - Activity Multiplier: {trade_activity_multiplier:.1f}x")
            print(f"      - Return Change: {return_improvement:+.2f} percentage points")
            print(f"      - Balance Change: ${balance_improvement:+,.0f}")
            
            # Determine success level
            if trade_activity_multiplier >= 5.0:
                activity_status = "EXCELLENT - 5x+ increase achieved!"
            elif trade_activity_multiplier >= 3.0:
                activity_status = "GOOD - 3x+ increase achieved"
            elif trade_activity_multiplier >= 2.0:
                activity_status = "MODERATE - 2x+ increase achieved"
            elif trade_activity_multiplier >= 1.5:
                activity_status = "MARGINAL - 1.5x+ increase achieved"
            else:
                activity_status = "INSUFFICIENT - Needs more improvements"
            
            print(f"      - Activity Status: {activity_status}")
            
            # Performance analysis
            if return_improvement > 10:
                perf_status = "OUTSTANDING - Significant return improvement"
            elif return_improvement > 2:
                perf_status = "GOOD - Meaningful return improvement"
            elif return_improvement > -2:
                perf_status = "ACCEPTABLE - Similar performance maintained"
            else:
                perf_status = "CONCERNING - Performance declined"
            
            print(f"      - Performance Status: {perf_status}")
            
            # Risk Management Analysis
            if hasattr(enhanced_strategy, 'max_drawdown_pct'):
                max_dd = getattr(enhanced_strategy, 'max_drawdown_pct', 0)
                if max_dd < 10:
                    risk_status = "EXCELLENT - Low drawdown maintained"
                elif max_dd < 20:
                    risk_status = "GOOD - Reasonable drawdown control"
                else:
                    risk_status = "CONCERNING - High drawdown detected"
                print(f"      - Risk Management: {risk_status} (Max DD: {max_dd:.1f}%)")
            
            # Overall assessment
            print(f"\n   🚀 OVERALL ASSESSMENT:")
            if (trade_activity_multiplier >= 3.0 and return_improvement > -5):
                overall_status = "SUCCESS - Ready for Phase 4 deployment"
            elif (trade_activity_multiplier >= 2.0 and return_improvement > -10):
                overall_status = "GOOD - Minor refinements needed"
            elif trade_activity_multiplier >= 1.5:
                overall_status = "MARGINAL - More signal improvements needed"
            else:
                overall_status = "INSUFFICIENT - Major rework required"
            
            print(f"      {overall_status}")
            
            # Store results
            result = {
                'period': period_name,
                'phase3_return': phase3_return,
                'enhanced_return': enhanced_return,
                'phase3_trades': phase3_trades,
                'enhanced_trades': enhanced_trades,
                'return_improvement': return_improvement,
                'trade_multiplier': trade_activity_multiplier,
                'signals_generated': enhanced_strategy.signals_generated_today,
                'enhanced_opportunities': enhanced_strategy.enhanced_opportunities_captured,
                'activity_status': activity_status,
                'performance_status': perf_status,
                'overall_status': overall_status
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
    generate_enhanced_base_report(all_results)

def generate_enhanced_base_report(results):
    """Generate comprehensive enhanced base validation report"""
    
    print("📊 ENHANCED BASE VALIDATION REPORT")
    print("=" * 60)
    
    # Results table
    print("| Test Period | Phase 3 | Enhanced | Δ Return | Phase 3 Trades | Enhanced Trades | Activity Multiplier | Status |")
    print("|-------------|---------|-----------|-----------|----------------|-----------------|-------------------|---------|")
    
    successful_results = [r for r in results if 'status' not in r or r.get('status') != 'ERROR']
    total_return_improvement = 0
    total_activity_improvement = 0
    
    for result in results:
        if 'error' not in result:
            period = result['period'][:11]
            phase3_ret = result['phase3_return']
            enhanced_ret = result['enhanced_return']
            ret_improvement = result['return_improvement']
            phase3_trades = result['phase3_trades']
            enhanced_trades = result['enhanced_trades']
            activity_mult = result['trade_multiplier']
            status = result['overall_status'][:7]
            
            print(f"| {period:<11} | {phase3_ret:+5.1f}% | {enhanced_ret:+7.1f}% | {ret_improvement:+6.1f}% | {phase3_trades:>8} | {enhanced_trades:>9} | {activity_mult:>10.1f}x | {status} |")
            
            total_return_improvement += ret_improvement
            total_activity_improvement += activity_mult
        else:
            period = result['period'][:11]
            print(f"| {period:<11} | ERROR | ERROR | ERROR | ERROR | ERROR | ERROR | ERROR |")
    
    print()
    
    if successful_results:
        avg_return_improvement = total_return_improvement / len(successful_results)
        avg_activity_improvement = total_activity_improvement / len(successful_results)
        
        print("🎯 SIGNAL GENERATION OVERHAUL RESULTS:")
        print(f"- Average Return Improvement: {avg_return_improvement:+.2f} percentage points")
        print(f"- Average Activity Multiplier: {avg_activity_improvement:.1f}x")
        print(f"- Successful Tests: {len(successful_results)}/{len(results)}")
        
        # Analyze signal generation effectiveness
        total_signals = sum(r.get('signals_generated', 0) for r in successful_results)
        total_enhanced_opportunities = sum(r.get('enhanced_opportunities', 0) for r in successful_results)
        
        print(f"- Total Signals Generated: {total_signals}")
        print(f"- Enhanced Opportunities Captured: {total_enhanced_opportunities}")
        
        print()
        print("🔍 IMPLEMENTATION VERIFICATION:")
        
        # Trading activity assessment
        if avg_activity_improvement >= 5.0:
            print("🎉 OUTSTANDING: 5x+ trading activity increase achieved!")
            activity_grade = "A+"
        elif avg_activity_improvement >= 3.0:
            print("✅ EXCELLENT: 3x+ trading activity increase achieved!")
            activity_grade = "A"
        elif avg_activity_improvement >= 2.0:
            print("🔄 GOOD: 2x+ trading activity increase achieved")
            activity_grade = "B"
        elif avg_activity_improvement >= 1.5:
            print("⚠️ MARGINAL: Some trading activity increase")
            activity_grade = "C"
        else:
            print("❌ INSUFFICIENT: Minimal trading activity improvement")
            activity_grade = "F"
        
        # Performance assessment
        if avg_return_improvement > 10:
            print("🚀 OUTSTANDING: Significant performance improvement!")
            performance_grade = "A+"
        elif avg_return_improvement > 2:
            print("✅ GOOD: Meaningful performance improvement")
            performance_grade = "A"
        elif avg_return_improvement > -5:
            print("🔄 ACCEPTABLE: Performance maintained while increasing activity")
            performance_grade = "B"
        elif avg_return_improvement > -15:
            print("⚠️ CONCERNING: Some performance decline with increased activity")
            performance_grade = "C"
        else:
            print("❌ POOR: Significant performance decline")
            performance_grade = "F"
        
        print()
        print("🚀 PHASE 4 READINESS ASSESSMENT:")
        
        # Determine Phase 4 readiness
        if activity_grade in ["A+", "A"] and performance_grade in ["A+", "A", "B"]:
            print("🎉 **READY FOR PHASE 4 DEPLOYMENT**")
            print("   ✅ Trading activity significantly increased")
            print("   ✅ Performance maintained or improved")
            print("   ✅ Signal generation fixes successful")
            print("   → Deploy Phase 4A and 4B optimizations immediately")
            readiness = "READY"
            
        elif activity_grade in ["B"] and performance_grade in ["A+", "A", "B"]:
            print("✅ **CONDITIONALLY READY FOR PHASE 4**")
            print("   🔄 Moderate trading activity increase")
            print("   ✅ Acceptable performance maintained")
            print("   → Deploy Phase 4 with monitoring")
            readiness = "CONDITIONAL"
            
        elif activity_grade in ["A+", "A", "B"]:
            print("🔄 **NEEDS PERFORMANCE TUNING**")
            print("   ✅ Good trading activity increase")
            print("   ⚠️ Performance needs improvement")
            print("   → Fine-tune parameters before Phase 4")
            readiness = "NEEDS_TUNING"
            
        else:
            print("⚠️ **NOT READY FOR PHASE 4**")
            print("   ❌ Insufficient trading activity increase")
            print("   → Need additional signal generation improvements")
            readiness = "NOT_READY"
        
        print()
        print("🛠️ NEXT STEPS RECOMMENDATIONS:")
        
        if readiness == "READY":
            print("1. **IMMEDIATE**: Deploy Phase 4A multi-timeframe analysis")
            print("2. **IMMEDIATE**: Deploy Phase 4B volatility adaptation")
            print("3. **NEXT**: Test combined Phase 4A+4B performance")
            print("4. **FUTURE**: Consider Phase 4C momentum enhancements")
            
        elif readiness == "CONDITIONAL":
            print("1. **DEPLOY**: Phase 4A and 4B with close monitoring")
            print("2. **MONITOR**: Track optimization activation rates")
            print("3. **ADJUST**: Fine-tune if optimizations don't activate frequently")
            
        elif readiness == "NEEDS_TUNING":
            print("1. **ADJUST**: Fine-tune risk management parameters")
            print("2. **TEST**: Validate performance improvements")
            print("3. **THEN**: Deploy Phase 4 optimizations")
            
        else:
            print("1. **REVIEW**: Analyze why signal improvements didn't work")
            print("2. **ADJUST**: Consider more aggressive parameter changes")
            print("3. **RETEST**: Validate improvements before Phase 4")
    
    else:
        print("❌ No successful tests - critical implementation issues")
    
    print()
    print("=" * 80)
    print("✅ Enhanced base validation complete!")
    print("=" * 80)

if __name__ == "__main__":
    run_enhanced_base_validation()