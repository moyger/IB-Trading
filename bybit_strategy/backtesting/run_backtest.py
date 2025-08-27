#!/usr/bin/env python3
"""
Run Backtest for Bybit 1H Trend Composite Strategy
Period: January 2024 to July 2025
"""

import sys
import os
from datetime import datetime
import pandas as pd
import json

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backtesting.backtest_engine import BacktestEngine, BacktestResults
from config.settings import Config

def print_results(results: BacktestResults):
    """Print formatted backtest results"""
    
    print("\n" + "=" * 70)
    print("📊 BACKTEST RESULTS - BYBIT 1H TREND COMPOSITE STRATEGY")
    print("=" * 70)
    
    print(f"\n📅 PERIOD: {results.start_date} to {results.end_date}")
    print(f"💰 Initial Capital: ${results.initial_capital:,.2f}")
    print(f"💸 Final Capital: ${results.final_capital:,.2f}")
    print(f"📈 Total Return: ${results.total_return:,.2f} ({results.total_return_pct:+.2f}%)")
    
    print("\n" + "-" * 70)
    print("📊 TRADE STATISTICS")
    print("-" * 70)
    print(f"Total Trades: {results.total_trades}")
    print(f"Winning Trades: {results.winning_trades}")
    print(f"Losing Trades: {results.losing_trades}")
    print(f"Win Rate: {results.win_rate:.1%}")
    print(f"Profit Factor: {results.profit_factor:.2f}")
    
    print("\n" + "-" * 70)
    print("💰 PROFIT/LOSS ANALYSIS")
    print("-" * 70)
    print(f"Average Win: ${results.avg_win:.2f} ({results.avg_win_pct:+.2f}%)")
    print(f"Average Loss: ${results.avg_loss:.2f} ({results.avg_loss_pct:.2f}%)")
    print(f"Risk/Reward Ratio: {results.risk_reward_ratio:.2f}:1")
    
    print("\n" + "-" * 70)
    print("📈 PERFORMANCE METRICS")
    print("-" * 70)
    print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"Sortino Ratio: {results.sortino_ratio:.2f}")
    print(f"Calmar Ratio: {results.calmar_ratio:.2f}")
    print(f"Max Drawdown: -{results.max_drawdown:.2f}%")
    
    # Monthly returns
    print("\n" + "-" * 70)
    print("📅 MONTHLY RETURNS")
    print("-" * 70)
    
    if results.monthly_returns:
        months = sorted(results.monthly_returns.keys())
        for month in months:
            pnl = results.monthly_returns[month]
            print(f"{month}: ${pnl:+,.2f}")
        
        # Calculate monthly statistics
        monthly_values = list(results.monthly_returns.values())
        positive_months = sum(1 for v in monthly_values if v > 0)
        negative_months = sum(1 for v in monthly_values if v < 0)
        print(f"\nPositive Months: {positive_months}")
        print(f"Negative Months: {negative_months}")
        print(f"Best Month: ${max(monthly_values):,.2f}")
        print(f"Worst Month: ${min(monthly_values):,.2f}")
        print(f"Average Monthly Return: ${sum(monthly_values)/len(monthly_values):,.2f}")
    
    # Symbol performance
    print("\n" + "-" * 70)
    print("🪙 SYMBOL PERFORMANCE")
    print("-" * 70)
    
    if results.symbol_performance:
        for symbol, perf in results.symbol_performance.items():
            print(f"\n{symbol}:")
            print(f"  Trades: {perf['total_trades']}")
            print(f"  Win Rate: {perf['win_rate']:.1%}")
            print(f"  Total P&L: ${perf['total_pnl']:,.2f}")
            print(f"  Avg P&L: ${perf['avg_pnl']:.2f}")
            print(f"  Best Trade: ${perf['best_trade']:.2f}")
            print(f"  Worst Trade: ${perf['worst_trade']:.2f}")
    
    # Trade analysis
    print("\n" + "-" * 70)
    print("🎯 EXIT REASON ANALYSIS")
    print("-" * 70)
    
    exit_reasons = {}
    for trade in results.trades:
        reason = trade.exit_reason
        if reason not in exit_reasons:
            exit_reasons[reason] = {'count': 0, 'pnl': 0}
        exit_reasons[reason]['count'] += 1
        exit_reasons[reason]['pnl'] += trade.pnl
    
    for reason, data in exit_reasons.items():
        pct = (data['count'] / results.total_trades) * 100
        print(f"{reason.upper()}: {data['count']} trades ({pct:.1f}%), P&L: ${data['pnl']:,.2f}")
    
    # Best and worst trades
    print("\n" + "-" * 70)
    print("🏆 BEST & WORST TRADES")
    print("-" * 70)
    
    best_trades = sorted(results.trades, key=lambda x: x.pnl, reverse=True)[:3]
    worst_trades = sorted(results.trades, key=lambda x: x.pnl)[:3]
    
    print("\n📈 Best Trades:")
    for i, trade in enumerate(best_trades, 1):
        print(f"{i}. {trade.symbol} ({trade.side}) - ${trade.pnl:.2f} ({trade.pnl_pct:+.2f}%)")
        print(f"   Entry: {trade.entry_time.strftime('%Y-%m-%d')} @ ${trade.entry_price:.4f}")
        print(f"   Exit: {trade.exit_time.strftime('%Y-%m-%d')} @ ${trade.exit_price:.4f}")
    
    print("\n📉 Worst Trades:")
    for i, trade in enumerate(worst_trades, 1):
        print(f"{i}. {trade.symbol} ({trade.side}) - ${trade.pnl:.2f} ({trade.pnl_pct:.2f}%)")
        print(f"   Entry: {trade.entry_time.strftime('%Y-%m-%d')} @ ${trade.entry_price:.4f}")
        print(f"   Exit: {trade.exit_time.strftime('%Y-%m-%d')} @ ${trade.exit_price:.4f}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    # Calculate annualized return
    days = (pd.Timestamp(results.end_date) - pd.Timestamp(results.start_date)).days
    years = days / 365
    annual_return = (((results.final_capital / results.initial_capital) ** (1/years)) - 1) * 100
    
    print(f"Annualized Return: {annual_return:.2f}%")
    print(f"Average Trade Duration: {sum((t.exit_time - t.entry_time).total_seconds()/3600 for t in results.trades)/len(results.trades):.1f} hours")
    
    # Success assessment
    print("\n🎯 STRATEGY ASSESSMENT:")
    if results.win_rate >= 0.60:
        print("✅ Win rate meets target (60%+)")
    else:
        print(f"⚠️ Win rate below target: {results.win_rate:.1%} < 60%")
    
    if results.sharpe_ratio >= 1.0:
        print("✅ Good risk-adjusted returns (Sharpe >= 1.0)")
    else:
        print(f"⚠️ Sharpe ratio below threshold: {results.sharpe_ratio:.2f}")
    
    if results.max_drawdown <= 20:
        print("✅ Acceptable drawdown (<= 20%)")
    else:
        print(f"⚠️ High drawdown: {results.max_drawdown:.1f}%")
    
    if results.profit_factor >= 1.5:
        print("✅ Strong profit factor (>= 1.5)")
    else:
        print(f"⚠️ Low profit factor: {results.profit_factor:.2f}")

def save_results(results: BacktestResults, filename: str = None):
    """Save backtest results to file"""
    
    if filename is None:
        filename = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Convert trades to dict format
    results_dict = {
        'summary': {
            'start_date': results.start_date,
            'end_date': results.end_date,
            'initial_capital': results.initial_capital,
            'final_capital': results.final_capital,
            'total_return': results.total_return,
            'total_return_pct': results.total_return_pct,
            'total_trades': results.total_trades,
            'win_rate': results.win_rate,
            'sharpe_ratio': results.sharpe_ratio,
            'max_drawdown': results.max_drawdown,
            'profit_factor': results.profit_factor
        },
        'monthly_returns': results.monthly_returns,
        'symbol_performance': results.symbol_performance,
        'trades': [
            {
                'entry_time': t.entry_time.isoformat(),
                'exit_time': t.exit_time.isoformat(),
                'symbol': t.symbol,
                'side': t.side,
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'pnl': t.pnl,
                'pnl_pct': t.pnl_pct,
                'exit_reason': t.exit_reason
            }
            for t in results.trades
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"\n✅ Results saved to {filename}")

def main():
    """Main backtest execution"""
    
    print("\n" + "=" * 70)
    print("🚀 BYBIT 1H TREND COMPOSITE STRATEGY - BACKTEST")
    print("=" * 70)
    print("📅 Testing Period: January 2024 to July 2025")
    print("🎯 Based on FTMO 68.4% Win Rate Strategy")
    print("=" * 70)
    
    # Configuration
    config = Config()
    
    # Initialize backtest engine
    engine = BacktestEngine(config)
    
    # Set backtest period
    engine.start_date = '2024-01-01'
    engine.end_date = '2025-07-31'
    engine.initial_capital = 10000
    
    # Symbols to test
    symbols = [
        'BTC/USDT:USDT',
        'ETH/USDT:USDT',
        'SOL/USDT:USDT',
        'ADA/USDT:USDT',
        'DOT/USDT:USDT'
    ]
    
    print(f"\n📊 Testing symbols: {', '.join([s.split('/')[0] for s in symbols])}")
    print(f"💰 Initial Capital: ${engine.initial_capital:,.2f}")
    print(f"⚠️ Risk per Trade: {engine.risk_per_trade}%")
    print(f"📊 Max Positions: {engine.max_positions}")
    print(f"🎯 Min Risk/Reward: {engine.min_rr_ratio}:1")
    
    # Run backtest
    try:
        results = engine.run_backtest(symbols)
        
        if results:
            # Print results
            print_results(results)
            
            # Save results
            save_results(results, 'bybit_strategy/backtesting/results/backtest_2024_2025.json')
            
            # Create performance chart data
            print("\n📊 Generating performance data...")
            
            # Equity curve
            equity_data = []
            running_capital = engine.initial_capital
            
            for trade in results.trades:
                running_capital += trade.pnl
                equity_data.append({
                    'date': trade.exit_time.strftime('%Y-%m-%d'),
                    'capital': running_capital,
                    'pnl': trade.pnl
                })
            
            # Save equity curve
            equity_df = pd.DataFrame(equity_data)
            equity_df.to_csv('bybit_strategy/backtesting/results/equity_curve.csv', index=False)
            print("✅ Equity curve saved to equity_curve.csv")
            
        else:
            print("❌ Backtest failed - no results generated")
            
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ BACKTEST COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    # Create results directory
    os.makedirs('bybit_strategy/backtesting/results', exist_ok=True)
    main()