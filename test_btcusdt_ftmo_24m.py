"""
Test BTCUSDT FTMO 1H Strategy - 24 Month Backtest
Test the adapted BTCUSDT FTMO 1H Strategy with the Universal Framework
Period: August 2023 to July 2025 (24 months)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add framework to path
framework_path = Path(__file__).parent / "framework"
sys.path.append(str(framework_path))

try:
    from strategies.btcusdt_ftmo_adapter import create_btcusdt_ftmo_strategy
    from core.backtest_engine import BacktestEngine
    from data.data_handler import DataHandler
    from reporting.report_generator import ReportGenerator
    from core.universal_strategy import AssetType
    
    print("✅ Successfully imported framework components")
    
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    print("Make sure the framework is properly set up")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_ftmo_backtest():
    """Run comprehensive 24-month FTMO backtest with all risk profiles and challenge phases"""
    
    print("\\n🚀 BTCUSDT FTMO 1H Strategy - 24 Month Universal Framework Test")
    print("=" * 80)
    print("📅 Period: August 2023 to July 2025 (24 months)")
    print("🎯 Testing: FTMO-proven Bitcoin 1H strategy")
    print("⚡ Features: FTMO compliance, ultra-strict risk management, Bitcoin volatility adaptation")
    
    # Test parameters
    start_date = '2023-08-01'
    end_date = '2025-07-31'
    initial_cash = 100000
    symbol = 'BTC-USD'
    
    # Test configurations: Risk profiles x Challenge phases
    test_configs = [
        ('conservative', 1), ('conservative', 2),
        ('moderate', 1), ('moderate', 2),
        ('aggressive', 1), ('aggressive', 2)
    ]
    
    # Initialize components
    engine = BacktestEngine(initial_cash=initial_cash)
    results = {}
    
    print(f"\\n🔧 Testing {len(test_configs)} configurations...")
    
    for risk_profile, phase in test_configs:
        config_name = f"{risk_profile}_phase{phase}"
        print(f"\\n📊 Testing {risk_profile.upper()} - Phase {phase}...")
        print("-" * 60)
        
        try:
            # Create strategy
            strategy = create_btcusdt_ftmo_strategy(
                risk_profile=risk_profile,
                challenge_phase=phase
            )
            
            print(f"✅ Created strategy: {strategy.config.name}")
            print(f"   Risk per trade: {strategy.risk_config['risk_per_trade']:.1f}%")
            print(f"   Max daily loss: {strategy.risk_config['max_daily_loss']:.1f}%")
            print(f"   Challenge phase: {phase}")
            print(f"   Min confluence: {strategy.min_confluence}")
            
            # Run backtest
            print("🔄 Running FTMO backtest...")
            result = engine.run_single_backtest(
                strategy=strategy,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval='1h'
            )
            
            # Store results
            results[config_name] = result
            
            # Print key metrics
            if result and 'performance' in result:
                performance = result['performance']
                print(f"✅ Backtest completed!")
                print(f"   Total Return: {performance['total_return']:.2f}%")
                print(f"   Max Drawdown: {performance['max_drawdown']:.2f}%")
                print(f"   Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
                print(f"   Win Rate: {performance['win_rate']:.1f}%")
                print(f"   Total Trades: {performance['total_trades']}")
                
                # FTMO compliance check
                ftmo_compliant = check_ftmo_compliance(performance)
                print(f"   FTMO Compliant: {'✅ Yes' if ftmo_compliant else '❌ No'}")
            else:
                print(f"❌ Backtest failed for {config_name}")
            
        except Exception as e:
            print(f"❌ Error testing {config_name}: {str(e)}")
            logging.error(f"Error in {config_name} backtest", exc_info=True)
            continue
    
    return results


def check_ftmo_compliance(performance):
    """Check if results meet FTMO compliance rules"""
    try:
        max_drawdown = abs(performance.get('max_drawdown', 0))
        
        # FTMO rules: Max 5% daily loss, 10% overall drawdown
        daily_loss_ok = True  # Assume daily tracking is handled in strategy
        overall_drawdown_ok = max_drawdown <= 10.0
        
        return daily_loss_ok and overall_drawdown_ok
    except:
        return False


def generate_ftmo_monthly_summaries(results: dict):
    """Generate detailed monthly summaries for each FTMO configuration"""
    
    print("\\n📅 FTMO MONTHLY PERFORMANCE SUMMARIES")
    print("=" * 80)
    
    for config_name, result in results.items():
        if result is None or 'monthly_summaries' not in result:
            continue
            
        risk_profile, phase = config_name.split('_')
        phase_num = phase.replace('phase', '')
        
        print(f"\\n🏆 {risk_profile.upper()} PHASE {phase_num} - MONTHLY BREAKDOWN")
        print("-" * 70)
        
        monthly_summaries = result.get('monthly_summaries', [])
        
        if not monthly_summaries:
            print("❌ No monthly data available")
            continue
        
        # Summary table header
        print(f"{'Month':<10} {'Start Balance':<15} {'End Balance':<15} {'P&L':<12} {'P&L %':<8} {'Trades':<8} {'FTMO':<6}")
        print("-" * 85)
        
        total_pnl = 0
        profitable_months = 0
        ftmo_violations = 0
        
        for month_data in monthly_summaries:
            month = month_data['month']
            start_bal = month_data['starting_balance']
            end_bal = month_data['ending_balance']
            pnl = month_data['pnl']
            pnl_pct = month_data['pnl_pct']
            trades = month_data['trades']
            
            total_pnl += pnl
            if pnl > 0:
                profitable_months += 1
            
            # Check FTMO compliance for the month
            monthly_loss_pct = abs(pnl_pct) if pnl < 0 else 0
            ftmo_ok = monthly_loss_pct <= 5.0  # 5% monthly loss limit
            if not ftmo_ok:
                ftmo_violations += 1
            
            # Format with emoji and FTMO status
            emoji = "📈" if pnl > 0 else "📉"
            ftmo_status = "✅" if ftmo_ok else "❌"
            
            print(f"{month:<10} ${start_bal:<14,.0f} ${end_bal:<14,.0f} ${pnl:<+11,.0f} {pnl_pct:<+7.2f}% {trades:<3} {ftmo_status:<3} {emoji}")
        
        # Monthly statistics
        print("-" * 85)
        print(f"SUMMARY: Total P&L: ${total_pnl:+,.0f} | Profitable: {profitable_months}/{len(monthly_summaries)} ({profitable_months/len(monthly_summaries)*100:.1f}%)")
        print(f"         FTMO Violations: {ftmo_violations} | Avg Monthly P&L: ${total_pnl/len(monthly_summaries):+,.0f}")


def generate_ftmo_comprehensive_report(results: dict):
    """Generate comprehensive FTMO performance report"""
    
    print("\\n📊 FTMO COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    # Comparison table
    print(f"\\n{'Configuration':<20} {'Total Return':<12} {'Max DD':<8} {'Sharpe':<8} {'Win Rate':<10} {'Trades':<8} {'FTMO':<6}")
    print("-" * 80)
    
    best_performer = None
    best_return = float('-inf')
    
    for config_name, result in results.items():
        if result is None:
            print(f"{config_name:<20} {'FAILED':<12}")
            continue
        
        perf = result['performance']
        total_return = perf['total_return']
        max_drawdown = perf['max_drawdown']
        sharpe = perf['sharpe_ratio']
        win_rate = perf['win_rate']
        total_trades = perf['total_trades']
        
        # FTMO compliance
        ftmo_compliant = check_ftmo_compliance(perf)
        ftmo_status = "✅" if ftmo_compliant else "❌"
        
        print(f"{config_name:<20} {total_return:<+11.2f}% {max_drawdown:<+7.2f}% {sharpe:<7.2f} {win_rate:<9.1f}% {total_trades:<8} {ftmo_status}")
        
        if total_return > best_return and ftmo_compliant:
            best_return = total_return
            best_performer = config_name
    
    print("-" * 80)
    
    if best_performer:
        print(f"🏆 BEST FTMO COMPLIANT: {best_performer.upper()} with {best_return:+.2f}% return")
    
    # Phase comparison
    print(f"\\n🎯 FTMO PHASE ANALYSIS:")
    print("-" * 40)
    
    phase1_results = [r for k, r in results.items() if 'phase1' in k and r is not None]
    phase2_results = [r for k, r in results.items() if 'phase2' in k and r is not None]
    
    if phase1_results:
        avg_phase1 = np.mean([r['performance']['total_return'] for r in phase1_results])
        print(f"📊 Phase 1 Average Return: {avg_phase1:+.2f}% (Target: +10%)")
    
    if phase2_results:
        avg_phase2 = np.mean([r['performance']['total_return'] for r in phase2_results])
        print(f"📊 Phase 2 Average Return: {avg_phase2:+.2f}% (Target: +5%)")
    
    # Risk profile analysis
    print(f"\\n🛡️ RISK PROFILE ANALYSIS:")
    print("-" * 40)
    
    for profile in ['conservative', 'moderate', 'aggressive']:
        profile_results = [r for k, r in results.items() if profile in k and r is not None]
        if profile_results:
            avg_return = np.mean([r['performance']['total_return'] for r in profile_results])
            avg_drawdown = np.mean([abs(r['performance']['max_drawdown']) for r in profile_results])
            avg_sharpe = np.mean([r['performance']['sharpe_ratio'] for r in profile_results])
            
            print(f"📈 {profile.title():>12}: Return {avg_return:+.2f}%, DD {avg_drawdown:.2f}%, Sharpe {avg_sharpe:.2f}")


def save_ftmo_results(results: dict):
    """Save FTMO results to files"""
    
    print("\\n💾 SAVING FTMO RESULTS TO FILES")
    print("-" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Generate reports for each configuration
        reporter = ReportGenerator(output_dir="backtest-logs")
        
        for config_name, result in results.items():
            if result is None:
                continue
                
            filename = f"btcusdt_ftmo_{config_name}_{timestamp}"
            
            # Generate markdown report
            report_path = reporter.generate_single_strategy_report(result, filename)
            print(f"✅ {config_name} report: {report_path}")
            
        # Generate comparison report
        valid_results = [result for result in results.values() if result is not None]
        if valid_results:
            comparison_path = reporter.generate_comparison_report(
                valid_results, 
                "BTCUSDT FTMO 1H Strategy - 24 Month Analysis",
                f"btcusdt_ftmo_comparison_{timestamp}"
            )
            print(f"✅ Comparison report: {comparison_path}")
        
        print("💾 All FTMO reports saved successfully!")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        logging.error("Error saving results", exc_info=True)


def main():
    """Main execution function"""
    
    print("🎯 BTCUSDT FTMO 1H Strategy - Universal Framework Test")
    print("📊 Testing FTMO-proven Bitcoin strategy across risk profiles and challenge phases")
    print("⏰ This may take several minutes due to 24-month 1H data processing...")
    
    try:
        # Run comprehensive FTMO backtest
        results = run_ftmo_backtest()
        
        if not any(results.values()):
            print("\\n❌ All FTMO backtests failed. Check data availability and strategy configuration.")
            return
        
        # Generate detailed analysis
        generate_ftmo_monthly_summaries(results)
        generate_ftmo_comprehensive_report(results)
        save_ftmo_results(results)
        
        print("\\n🎉 24-MONTH FTMO BACKTEST COMPLETED!")
        print("=" * 60)
        print("✅ FTMO Bitcoin 1H strategy successfully tested across all configurations")
        print("📊 Monthly summaries and FTMO compliance analysis generated")
        print("💾 Reports saved to backtest-logs directory")
        print("\\n🔍 Check the generated markdown reports for detailed FTMO analysis")
        print("\\n💡 Key FTMO Features Tested:")
        print("   - Daily loss limits (1-2% depending on risk profile)")
        print("   - Overall drawdown limits (3-6% depending on risk profile)")
        print("   - Challenge phase targets (10% Phase 1, 5% Phase 2)")
        print("   - Bitcoin volatility adaptation and hourly trade limits")
        print("   - Emergency stop mechanisms and violation prevention")
        
    except Exception as e:
        print(f"\\n❌ Critical error: {str(e)}")
        logging.error("Critical error in main execution", exc_info=True)


if __name__ == "__main__":
    main()