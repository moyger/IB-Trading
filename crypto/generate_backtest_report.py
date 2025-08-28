#!/usr/bin/env python3
"""
Generate and save comprehensive backtest reports in multiple formats
"""

import json
from datetime import datetime
from universal_backtesting_engine import UniversalBacktestEngine
from test_enhanced_strategy_universal import BTCUSDTEnhancedAdapter

def generate_comprehensive_report():
    """Generate and save comprehensive backtest report"""
    
    print("="*80)
    print("📊 GENERATING COMPREHENSIVE BACKTEST REPORT")
    print("="*80)
    
    # Initialize engine
    engine = UniversalBacktestEngine(data_source='yfinance')
    
    # Test parameters
    test_params = {
        'symbol': 'BTC-USD',
        'start_date': '2024-01-01',
        'end_date': '2024-06-01',
        'initial_cash': 100000,
        'commission': 0.001
    }
    
    # Test all risk profiles
    all_results = {}
    
    for profile in ['conservative', 'moderate', 'aggressive']:
        print(f"\n🔄 Running {profile} backtest...")
        result = engine.run_backtest(
            strategy_class=BTCUSDTEnhancedAdapter,
            risk_profile=profile,
            **test_params
        )
        all_results[profile] = result
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Save JSON Report
    json_filename = f'backtest-logs/btcusdt_enhanced_universal_{timestamp}.json'
    with open(json_filename, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n✅ JSON report saved to: {json_filename}")
    
    # 2. Generate Markdown Report
    md_filename = f'backtest-logs/btcusdt_enhanced_universal_{timestamp}.md'
    
    with open(md_filename, 'w') as f:
        f.write("# BTCUSDT Enhanced Strategy - Universal Backtest Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Strategy**: BTCUSDTEnhancedAdapter\n")
        f.write(f"**Period**: {test_params['start_date']} to {test_params['end_date']}\n")
        f.write(f"**Initial Capital**: ${test_params['initial_cash']:,}\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        best_profile = max(all_results.keys(), 
                          key=lambda x: all_results[x]['performance']['total_return'])
        best_return = all_results[best_profile]['performance']['total_return']
        f.write(f"**Best Performer**: {best_profile.capitalize()} Profile with **{best_return:.2f}%** return\n\n")
        
        # Performance Comparison Table
        f.write("## Performance Comparison\n\n")
        f.write("| Risk Profile | Total Return | Max Drawdown | Win Rate | Total Trades | Sharpe Ratio |\n")
        f.write("|--------------|-------------|--------------|----------|--------------|---------------|\n")
        
        for profile, result in all_results.items():
            perf = result['performance']
            f.write(f"| **{profile.capitalize()}** | ")
            f.write(f"{perf['total_return']:+.2f}% | ")
            f.write(f"{perf['max_drawdown']:.2f}% | ")
            f.write(f"{perf['win_rate']:.2f}% | ")
            f.write(f"{perf['total_trades']} | ")
            f.write(f"{perf['sharpe_ratio']:.2f} |\n")
        
        # Detailed Results for Each Profile
        for profile, result in all_results.items():
            f.write(f"\n---\n\n")
            f.write(f"## {profile.capitalize()} Profile Results\n\n")
            
            # Performance metrics
            f.write("### Performance Metrics\n\n")
            perf = result['performance']
            f.write(f"- **Total Return**: {perf['total_return']:+.2f}%\n")
            f.write(f"- **Buy & Hold Return**: {perf['buy_hold_return']:+.2f}%\n")
            f.write(f"- **Maximum Drawdown**: {perf['max_drawdown']:.2f}%\n")
            f.write(f"- **Win Rate**: {perf['win_rate']:.2f}%\n")
            f.write(f"- **Total Trades**: {perf['total_trades']}\n")
            f.write(f"- **Sharpe Ratio**: {perf['sharpe_ratio']:.2f}\n")
            f.write(f"- **Sortino Ratio**: {perf['sortino_ratio']:.2f}\n")
            f.write(f"- **Calmar Ratio**: {perf['calmar_ratio']:.2f}\n\n")
            
            # Trade Analysis
            f.write("### Trade Analysis\n\n")
            trade = result['trade_analysis']
            f.write(f"- **Average Trade**: {trade['avg_trade']:.2f}%\n")
            f.write(f"- **Best Trade**: {trade['best_trade']:.2f}%\n")
            f.write(f"- **Worst Trade**: {trade['worst_trade']:.2f}%\n")
            f.write(f"- **Average Duration**: {trade['avg_trade_duration']}\n")
            f.write(f"- **Profit Factor**: {trade['profit_factor']:.2f}\n\n")
            
            # Monthly Performance
            if result.get('monthly_summaries'):
                f.write("### Monthly Performance\n\n")
                f.write("| Month | Starting Balance | Ending Balance | P&L Amount | P&L % | Trades |\n")
                f.write("|-------|------------------|----------------|------------|-------|--------|\n")
                
                for month in result['monthly_summaries']:
                    emoji = "📈" if month['pnl'] >= 0 else "📉"
                    f.write(f"| {month['month']} | ")
                    f.write(f"${month['starting_balance']:,.0f} | ")
                    f.write(f"${month['ending_balance']:,.0f} | ")
                    f.write(f"${month['pnl']:+,.2f} | ")
                    f.write(f"{month['pnl_pct']:+.2f}% | ")
                    f.write(f"{month['trades']} {emoji} |\n")
                
                # Monthly statistics
                total_pnl = sum(m['pnl'] for m in result['monthly_summaries'])
                avg_monthly = total_pnl / len(result['monthly_summaries']) if result['monthly_summaries'] else 0
                profitable_months = sum(1 for m in result['monthly_summaries'] if m['pnl'] >= 0)
                
                f.write(f"\n**Monthly Statistics:**\n")
                f.write(f"- Total P&L: ${total_pnl:+,.2f}\n")
                f.write(f"- Average Monthly P&L: ${avg_monthly:+,.2f}\n")
                f.write(f"- Profitable Months: {profitable_months}/{len(result['monthly_summaries'])}\n")
        
        # Footer
        f.write("\n---\n\n")
        f.write("## Strategy Configuration\n\n")
        f.write("### Risk Profiles\n\n")
        f.write("| Profile | Risk/Trade | Daily Loss Limit | Confluence Threshold | Position Size |\n")
        f.write("|---------|------------|------------------|---------------------|---------------|\n")
        f.write("| Conservative | 1% | 3% | 5 | 10% |\n")
        f.write("| Moderate | 2% | 5% | 4 | 15% |\n")
        f.write("| Aggressive | 3% | 7% | 3 | 25% |\n\n")
        
        f.write("### Technical Indicators Used\n\n")
        f.write("- **EMAs**: 8, 21, 50, 100, 200 periods\n")
        f.write("- **RSI**: 14 and 21 periods\n")
        f.write("- **MACD**: 12/26/9 configuration\n")
        f.write("- **ADX**: 14-period for trend strength\n")
        f.write("- **Bollinger Bands**: 20-period, 2 standard deviations\n")
        f.write("- **Volume Analysis**: 20-period moving average\n\n")
        
        f.write("---\n\n")
        f.write(f"*Report generated using Universal Backtesting Engine with backtesting.py*\n")
    
    print(f"✅ Markdown report saved to: {md_filename}")
    
    # 3. Display summary in terminal
    print("\n" + "="*80)
    print("📊 BACKTEST SUMMARY")
    print("="*80)
    print(f"\n🏆 Best Performer: {best_profile.capitalize()} with {best_return:.2f}% return\n")
    
    print("Performance by Risk Profile:")
    for profile, result in all_results.items():
        perf = result['performance']
        print(f"  {profile.capitalize():12} → Return: {perf['total_return']:+7.2f}% | "
              f"Drawdown: {perf['max_drawdown']:6.2f}% | "
              f"Trades: {perf['total_trades']:3}")
    
    print("\n📁 Reports saved to:")
    print(f"  • JSON: {json_filename}")
    print(f"  • Markdown: {md_filename}")
    print("="*80)
    
    return all_results, json_filename, md_filename

if __name__ == "__main__":
    results, json_file, md_file = generate_comprehensive_report()
    print(f"\n✅ Reports generated successfully!")