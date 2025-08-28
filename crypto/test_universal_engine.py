#!/usr/bin/env python3
"""
Test the Universal Backtesting Engine with different strategies
"""

from universal_backtesting_engine import (
    UniversalBacktestEngine,
    UniversalStrategy,
    SimpleMAStrategy,
    FTMOBitcoinStrategy
)

def test_universal_engine():
    """Test the universal backtesting engine"""
    
    # Initialize the engine
    engine = UniversalBacktestEngine(data_source='yfinance')
    
    print("="*80)
    print("🚀 TESTING UNIVERSAL BACKTESTING ENGINE")
    print("="*80)
    
    # Test 1: Simple Moving Average Strategy
    print("\n📊 Test 1: Simple MA Crossover Strategy")
    print("-"*40)
    ma_results = engine.run_backtest(
        strategy_class=SimpleMAStrategy,
        symbol='BTC-USD',
        start_date='2024-03-01',
        end_date='2024-06-01',
        initial_cash=100000,
        commission=0.001,
        # Strategy parameters
        fast_ma=10,
        slow_ma=30
    )
    
    # Test 2: Complex FTMO Bitcoin Strategy  
    print("\n📊 Test 2: FTMO Bitcoin Strategy")
    print("-"*40)
    ftmo_results = engine.run_backtest(
        strategy_class=FTMOBitcoinStrategy,
        symbol='BTC-USD',
        start_date='2024-03-01',
        end_date='2024-06-01',
        initial_cash=100000,
        commission=0.001,
        # FTMO parameters
        profit_target=0.10,  # 10% profit target
        max_daily_loss=0.05,  # 5% daily limit
        daily_loss_emergency=0.008,  # 0.8% emergency
        overall_loss_emergency=0.05  # 5% overall emergency
    )
    
    print("\n" + "="*80)
    print("✅ Universal Backtesting Engine Test Complete!")
    print("="*80)
    
    # Compare results
    print("\n📈 STRATEGY COMPARISON:")
    print("-"*40)
    print(f"Simple MA Return:  {ma_results['performance']['total_return']:.2f}%")
    print(f"FTMO Return:       {ftmo_results['performance']['total_return']:.2f}%")
    print(f"Simple MA Trades:  {ma_results['performance']['total_trades']}")
    print(f"FTMO Trades:       {ftmo_results['performance']['total_trades']}")
    
    return ma_results, ftmo_results

if __name__ == "__main__":
    test_universal_engine()