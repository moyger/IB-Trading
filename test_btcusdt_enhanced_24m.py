"""
Test BTCUSDT Enhanced Strategy - 24 Month Backtest

Test the adapted BTCUSDT Enhanced Strategy with the new Universal Framework
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
    from strategies.btcusdt_enhanced_adapter import create_btcusdt_enhanced_strategy
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


def run_btcusdt_enhanced_backtest():
    """Run comprehensive 24-month backtest with all risk profiles"""
    
    print("\n🚀 BTCUSDT Enhanced Strategy - 24 Month Universal Framework Test")
    print("=" * 80)
    print("📅 Period: August 2023 to July 2025 (24 months)")
    print("🎯 Testing: Multi-confluence enhanced strategy")
    
    # Test parameters
    start_date = '2023-08-01'
    end_date = '2025-07-31'
    initial_cash = 100000
    symbol = 'BTC-USD'
    
    # Risk profiles to test
    risk_profiles = ['conservative', 'moderate', 'aggressive']
    
    # Initialize components
    engine = BacktestEngine(initial_cash=initial_cash)
    results = {}
    
    print(f"\n🔧 Testing {len(risk_profiles)} risk profiles...")
    
    for risk_profile in risk_profiles:
        print(f"\n📊 Testing {risk_profile.upper()} profile...")
        print("-" * 50)
        
        try:
            # Create strategy
            strategy = create_btcusdt_enhanced_strategy(
                risk_profile=risk_profile,
                confluence_threshold=4 if risk_profile == 'moderate' else (5 if risk_profile == 'conservative' else 3)
            )
            
            print(f"✅ Created strategy: {strategy.config.name}")
            print(f"   Risk per trade: {strategy.config.risk_per_trade:.1%}")
            print(f"   Max daily loss: {strategy.config.max_daily_loss:.1%}")
            print(f"   Confluence threshold: {strategy.min_confluence}")
            
            # Run backtest
            print("🔄 Running backtest...")
            result = engine.run_single_backtest(
                strategy=strategy,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval='1h'
            )
            
            # Store results
            results[risk_profile] = result
            
            # Print key metrics
            performance = result['performance']
            print(f"✅ Backtest completed!")
            print(f"   Total Return: {performance['total_return']:.2f}%")
            print(f"   Max Drawdown: {performance['max_drawdown']:.2f}%")
            print(f"   Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
            print(f"   Win Rate: {performance['win_rate']:.1f}%")
            print(f"   Total Trades: {performance['total_trades']}")
            
        except Exception as e:
            print(f"❌ Error testing {risk_profile}: {str(e)}")
            logging.error(f"Error in {risk_profile} backtest", exc_info=True)
            continue
    
    return results


def generate_monthly_summaries(results: dict):
    """Generate detailed monthly summaries for each risk profile"""
    
    print("\n📅 MONTHLY PERFORMANCE SUMMARIES")
    print("=" * 80)
    
    for risk_profile, result in results.items():
        if result is None:
            continue
            
        print(f"\n🏆 {risk_profile.upper()} PROFILE - MONTHLY BREAKDOWN")
        print("-" * 60)
        
        monthly_summaries = result.get('monthly_summaries', [])
        
        if not monthly_summaries:
            print("❌ No monthly data available")
            continue
        
        # Summary table header
        print(f"{'Month':<10} {'Start Balance':<15} {'End Balance':<15} {'P&L':<12} {'P&L %':<8} {'Trades':<8}")
        print("-" * 75)
        
        total_pnl = 0
        profitable_months = 0
        
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
            
            # Format with emoji
            emoji = "📈" if pnl > 0 else "📉"
            
            print(f"{month:<10} ${start_bal:<14,.0f} ${end_bal:<14,.0f} ${pnl:<+11,.0f} {pnl_pct:<+7.2f}% {trades:<3} {emoji}")
        
        # Monthly statistics
        print("-" * 75)
        print(f"SUMMARY: Total P&L: ${total_pnl:+,.0f} | Profitable Months: {profitable_months}/{len(monthly_summaries)} ({profitable_months/len(monthly_summaries)*100:.1f}%)")
        
        if monthly_summaries:
            avg_monthly_pnl = total_pnl / len(monthly_summaries)
            print(f"         Average Monthly P&L: ${avg_monthly_pnl:+,.0f}")


def generate_comprehensive_report(results: dict):
    """Generate comprehensive performance report"""
    
    print("\n📊 COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    # Comparison table
    print(f"\n{'Risk Profile':<15} {'Total Return':<12} {'Max Drawdown':<13} {'Sharpe':<8} {'Win Rate':<10} {'Trades':<8}")
    print("-" * 70)
    
    best_performer = None
    best_return = float('-inf')
    
    for risk_profile, result in results.items():
        if result is None:
            print(f"{risk_profile.title():<15} {'FAILED':<12}")
            continue
        
        perf = result['performance']
        total_return = perf['total_return']
        max_drawdown = perf['max_drawdown']
        sharpe = perf['sharpe_ratio']
        win_rate = perf['win_rate']
        total_trades = perf['total_trades']
        
        print(f"{risk_profile.title():<15} {total_return:<+11.2f}% {max_drawdown:<+12.2f}% {sharpe:<7.2f} {win_rate:<9.1f}% {total_trades:<8}")
        
        if total_return > best_return:
            best_return = total_return
            best_performer = risk_profile
    
    print("-" * 70)
    
    if best_performer:
        print(f"🏆 BEST PERFORMER: {best_performer.upper()} with {best_return:+.2f}% return")
    
    # Detailed analysis for best performer
    if best_performer and results[best_performer]:
        print(f"\n🔍 DETAILED ANALYSIS - {best_performer.upper()} PROFILE")
        print("-" * 50)
        
        result = results[best_performer]
        perf = result['performance']
        
        print(f"📈 Return Metrics:")
        print(f"   Total Return: {perf['total_return']:+.2f}%")
        print(f"   Annualized Return: {perf['annualized_return']:+.2f}%")
        print(f"   CAGR: {perf['cagr']:+.2f}%")
        
        print(f"\n🛡️ Risk Metrics:")
        print(f"   Max Drawdown: {perf['max_drawdown']:.2f}%")
        print(f"   Volatility: {perf['volatility']:.2f}%")
        print(f"   VaR (95%): {perf['var_95']:.2f}%")
        
        print(f"\n⚖️ Risk-Adjusted Metrics:")
        print(f"   Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
        print(f"   Sortino Ratio: {perf['sortino_ratio']:.2f}")
        print(f"   Calmar Ratio: {perf['calmar_ratio']:.2f}")
        
        print(f"\n💰 Trade Metrics:")
        print(f"   Win Rate: {perf['win_rate']:.1f}%")
        print(f"   Total Trades: {perf['total_trades']}")
        print(f"   Profit Factor: {perf['profit_factor']:.2f}")
        print(f"   Avg Trade: {perf['avg_trade_return']:+.2f}%")
        print(f"   Best Trade: {perf['best_trade']:+.2f}%")
        print(f"   Worst Trade: {perf['worst_trade']:+.2f}%")


def save_results(results: dict):
    """Save results to files"""
    
    print("\n💾 SAVING RESULTS TO FILES")
    print("-" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Generate reports for each profile
        reporter = ReportGenerator(output_dir="backtest-logs")
        
        for risk_profile, result in results.items():
            if result is None:
                continue
                
            filename = f"btcusdt_enhanced_{risk_profile}_{timestamp}"
            
            # Generate markdown report
            report_path = reporter.generate_single_strategy_report(result, filename)
            print(f"✅ {risk_profile.title()} report: {report_path}")
            
        # Generate comparison report
        valid_results = [result for result in results.values() if result is not None]
        if valid_results:
            comparison_path = reporter.generate_comparison_report(
                valid_results, 
                "BTCUSDT Enhanced Strategy - 24 Month Analysis",
                f"btcusdt_enhanced_comparison_{timestamp}"
            )
            print(f"✅ Comparison report: {comparison_path}")
        
        print("💾 All reports saved successfully!")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        logging.error("Error saving results", exc_info=True)


def main():
    """Main execution function"""
    
    print("🎯 BTCUSDT Enhanced Strategy - Universal Framework Test")
    print("📊 Testing adapted multi-confluence strategy with new framework")
    print("⏰ This may take several minutes due to 24-month data processing...")
    
    try:
        # Run comprehensive backtest
        results = run_btcusdt_enhanced_backtest()
        
        if not any(results.values()):
            print("\n❌ All backtests failed. Check data availability and strategy configuration.")
            return
        
        # Generate detailed analysis
        generate_monthly_summaries(results)
        generate_comprehensive_report(results)
        save_results(results)
        
        print("\n🎉 24-MONTH BACKTEST COMPLETED!")
        print("=" * 50)
        print("✅ Enhanced BTCUSDT strategy successfully tested")
        print("📊 Monthly summaries and detailed analysis generated")
        print("💾 Reports saved to backtest-logs directory")
        print("\n🔍 Check the generated markdown reports for detailed analysis")
        
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        logging.error("Critical error in main execution", exc_info=True)


if __name__ == "__main__":
    main()