"""
Basic Framework Usage Examples

Demonstrates how to use the Universal Backtesting Framework
for different types of strategies and assets.
"""

import sys
from pathlib import Path

# Add framework to path
sys.path.append(str(Path(__file__).parent.parent))

from core.backtest_engine import BacktestEngine
from strategies.simple_ma_strategy import create_simple_ma_strategy
from strategies.bitcoin_ftmo_strategy import create_bitcoin_ftmo_strategy
from core.universal_strategy import AssetType
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


def basic_crypto_backtest():
    """Example: Basic Bitcoin strategy backtest"""
    print("\\n=== Basic Crypto Backtest Example ===")
    
    # Create strategy
    strategy = create_simple_ma_strategy(
        asset_type=AssetType.CRYPTO,
        fast_period=20,
        slow_period=50,
        risk_profile='moderate'
    )
    
    # Initialize engine
    engine = BacktestEngine(initial_cash=100000)
    
    # Run backtest
    results = engine.run_single_backtest(
        strategy=strategy,
        symbol='BTC-USD',
        start_date='2024-01-01',
        end_date='2024-06-01',
        interval='1h'
    )
    
    # Print key metrics
    performance = results['performance']
    print(f"Total Return: {performance['total_return']:.2f}%")
    print(f"Max Drawdown: {performance['max_drawdown']:.2f}%")
    print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"Win Rate: {performance['win_rate']:.1f}%")
    
    return results


def ftmo_bitcoin_backtest():
    """Example: FTMO-compliant Bitcoin strategy"""
    print("\\n=== FTMO Bitcoin Strategy Example ===")
    
    # Create FTMO strategy
    strategy = create_bitcoin_ftmo_strategy(
        risk_profile='conservative',
        ftmo_phase='challenge'
    )
    
    # Initialize engine
    engine = BacktestEngine(initial_cash=100000)
    
    # Run backtest
    results = engine.run_single_backtest(
        strategy=strategy,
        symbol='BTC-USD', 
        start_date='2023-08-01',
        end_date='2025-07-31',  # 24-month period as specified
        interval='1h'
    )
    
    # Print results
    performance = results['performance']
    print(f"Strategy: {results['strategy']['name']}")
    print(f"Total Return: {performance['total_return']:.2f}%")
    print(f"Max Drawdown: {performance['max_drawdown']:.2f}%")
    print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"Total Trades: {performance['total_trades']}")
    
    # Print monthly summaries
    print("\\nMonthly Performance:")
    for month in results['monthly_summaries'][:6]:  # First 6 months
        print(f"{month['month']}: {month['pnl_pct']:+.2f}% ({month['trades']} trades)")
    
    return results


def multi_asset_backtest():
    """Example: Multi-asset portfolio backtest"""
    print("\\n=== Multi-Asset Portfolio Example ===")
    
    # Create strategy
    strategy = create_simple_ma_strategy(
        asset_type=AssetType.CRYPTO,
        risk_profile='moderate'
    )
    
    # Initialize engine
    engine = BacktestEngine(initial_cash=100000)
    
    # Define portfolio
    symbols = ['BTC-USD', 'ETH-USD']
    allocation = {'BTC-USD': 0.6, 'ETH-USD': 0.4}
    
    # Run multi-asset backtest
    results = engine.run_multi_asset_backtest(
        strategy=strategy,
        symbols=symbols,
        start_date='2024-01-01',
        end_date='2024-06-01',
        portfolio_allocation=allocation
    )
    
    # Print results
    performance = results['performance']
    print(f"Portfolio Return: {performance['total_return']:.2f}%")
    print(f"Portfolio Sharpe: {performance['sharpe_ratio']:.2f}")
    
    # Individual asset performance
    print("\\nIndividual Assets:")
    for symbol, perf in results['individual_performance'].items():
        print(f"{symbol}: {perf['total_return']:.2f}% return")
    
    return results


def parameter_optimization_example():
    """Example: Parameter optimization"""
    print("\\n=== Parameter Optimization Example ===")
    
    # Import strategy class
    from strategies.simple_ma_strategy import SimpleMAStrategy
    
    # Initialize engine
    engine = BacktestEngine(initial_cash=100000)
    
    # Define parameter ranges
    param_ranges = {
        'fast_period': [10, 15, 20, 25],
        'slow_period': [40, 50, 60, 70],
        'rsi_period': [12, 14, 16, 18]
    }
    
    # Run optimization
    results = engine.run_parameter_optimization(
        strategy_class=SimpleMAStrategy,
        symbol='BTC-USD',
        start_date='2024-01-01',
        end_date='2024-06-01',
        param_ranges=param_ranges,
        optimization_metric='sharpe_ratio',
        max_combinations=50
    )
    
    # Print best results
    print(f"Best Parameters: {results['best_parameters']}")
    print(f"Best Sharpe Ratio: {results['best_metric_value']:.3f}")
    print(f"Tested {results['successful_combinations']} combinations")
    
    return results


def generate_comprehensive_report():
    """Example: Generate comprehensive report"""
    print("\\n=== Comprehensive Report Generation ===")
    
    # Run basic backtest
    results = basic_crypto_backtest()
    
    # Generate report
    from reporting.report_generator import ReportGenerator
    
    reporter = ReportGenerator(output_dir="framework_test_reports")
    report_path = reporter.generate_single_strategy_report(results)
    
    print(f"Comprehensive report generated: {report_path}")
    
    return report_path


def compare_strategies():
    """Example: Compare multiple strategies"""
    print("\\n=== Strategy Comparison Example ===")
    
    # Create different strategies
    conservative_strategy = create_simple_ma_strategy(risk_profile='conservative')
    moderate_strategy = create_simple_ma_strategy(risk_profile='moderate')
    aggressive_strategy = create_simple_ma_strategy(risk_profile='aggressive')
    
    # Initialize engine
    engine = BacktestEngine(initial_cash=100000)
    
    # Run backtests
    strategies = [
        (conservative_strategy, "Conservative"),
        (moderate_strategy, "Moderate"),
        (aggressive_strategy, "Aggressive")
    ]
    
    results_list = []
    for strategy, name in strategies:
        strategy.config.name = f"SimpleMA_{name}"
        result = engine.run_single_backtest(
            strategy=strategy,
            symbol='BTC-USD',
            start_date='2024-01-01',
            end_date='2024-06-01'
        )
        results_list.append(result)
    
    # Generate comparison report
    from reporting.report_generator import ReportGenerator
    
    reporter = ReportGenerator(output_dir="framework_test_reports")
    comparison_path = reporter.generate_comparison_report(
        results_list, 
        "Risk Profile Comparison"
    )
    
    print(f"Comparison report generated: {comparison_path}")
    
    return results_list


if __name__ == "__main__":
    """Run all examples"""
    print("IB Trading Universal Backtesting Framework - Examples")
    print("=" * 60)
    
    try:
        # Basic examples
        basic_crypto_backtest()
        ftmo_bitcoin_backtest() 
        multi_asset_backtest()
        
        # Advanced examples
        parameter_optimization_example()
        generate_comprehensive_report()
        compare_strategies()
        
        print("\\n" + "=" * 60)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")
        logging.error(f"Example error: {str(e)}", exc_info=True)