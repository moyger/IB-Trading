"""
Quick Demo of Universal Backtesting Framework

Test the framework with synthetic data to verify everything works.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add framework to path
sys.path.append(str(Path(__file__).parent))

def create_demo_data() -> pd.DataFrame:
    """Create synthetic test data"""
    dates = pd.date_range('2024-01-01', '2024-06-01', freq='H')
    n_points = len(dates)
    
    # Generate realistic crypto price movement
    np.random.seed(42)
    base_price = 45000
    
    # Random walk with trend
    returns = np.random.normal(0.0002, 0.015, n_points)  # Slight upward bias
    prices = base_price * np.cumprod(1 + returns)
    
    # Create OHLCV
    data = pd.DataFrame(index=dates)
    data['Close'] = prices
    data['Open'] = data['Close'].shift(1).fillna(data['Close'].iloc[0])
    
    # Add realistic high/low
    daily_range = np.random.uniform(0.005, 0.03, n_points)
    data['High'] = data['Close'] * (1 + daily_range/2)
    data['Low'] = data['Close'] * (1 - daily_range/2)
    data['Volume'] = np.random.uniform(1000000, 5000000, n_points)
    
    return data

def demo_simple_strategy():
    """Demo simple MA strategy"""
    print("\\n🎯 Testing Simple MA Strategy")
    print("-" * 40)
    
    try:
        from strategies.simple_ma_strategy import create_simple_ma_strategy
        from core.backtest_engine import BacktestEngine
        from core.universal_strategy import AssetType
        
        # Create test data
        data = create_demo_data()
        print(f"✅ Created {len(data)} data points")
        
        # Create strategy
        strategy = create_simple_ma_strategy(
            asset_type=AssetType.CRYPTO,
            fast_period=20,
            slow_period=50,
            risk_profile='moderate'
        )
        print(f"✅ Created strategy: {strategy.config.name}")
        
        # Test indicator calculation
        indicators = strategy.calculate_indicators(data)
        print(f"✅ Calculated indicators: {list(indicators.columns)}")
        
        # Test signal generation
        combined_data = pd.concat([data, indicators], axis=1)
        signals = strategy.generate_signals(combined_data)
        
        entry_count = signals['entries'].sum()
        exit_count = signals['exits'].sum()
        print(f"✅ Generated {entry_count} entry signals, {exit_count} exit signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_bitcoin_ftmo():
    """Demo Bitcoin FTMO strategy"""
    print("\\n🏆 Testing Bitcoin FTMO Strategy")
    print("-" * 40)
    
    try:
        from strategies.bitcoin_ftmo_strategy import create_bitcoin_ftmo_strategy
        
        # Create test data
        data = create_demo_data()
        
        # Create FTMO strategy
        strategy = create_bitcoin_ftmo_strategy(
            risk_profile='conservative',
            ftmo_phase='challenge'
        )
        print(f"✅ Created FTMO strategy: {strategy.config.name}")
        print(f"   FTMO Compliant: {strategy.config.ftmo_compliant}")
        print(f"   Risk per trade: {strategy.config.risk_per_trade:.1%}")
        
        # Test indicators
        indicators = strategy.calculate_indicators(data)
        print(f"✅ FTMO indicators: {len(indicators.columns)} calculated")
        
        # Test signals with confluence
        combined_data = pd.concat([data, indicators], axis=1)
        signals = strategy.generate_signals(combined_data)
        
        entry_count = signals['entries'].sum()
        avg_size = signals['size'][signals['entries']].mean()
        print(f"✅ Generated {entry_count} entries with avg size {avg_size:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_risk_manager():
    """Demo risk management system"""
    print("\\n🛡️ Testing Risk Management")
    print("-" * 40)
    
    try:
        from portfolio.risk_manager import RiskManager, RiskLimits
        from core.universal_strategy import StrategyConfig, AssetType
        
        # Create risk manager
        risk_manager = RiskManager()
        print("✅ Created risk manager")
        
        # Test FTMO mode
        risk_manager.set_ftmo_mode('challenge')
        print("✅ Set FTMO challenge mode")
        
        # Test risk report
        risk_report = risk_manager.get_risk_report()
        print(f"✅ Generated risk report with {len(risk_report)} sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_performance_analyzer():
    """Demo performance analysis"""
    print("\\n📊 Testing Performance Analysis")
    print("-" * 40)
    
    try:
        from reporting.performance_analyzer import PerformanceAnalyzer
        
        # Create test portfolio data
        dates = pd.date_range('2024-01-01', '2024-06-01', freq='D')
        portfolio_value = pd.Series(
            100000 * np.cumprod(1 + np.random.normal(0.001, 0.02, len(dates))),
            index=dates
        )
        
        # Analyze performance
        analyzer = PerformanceAnalyzer()
        
        # Test individual metrics
        total_return = analyzer._calculate_total_return(portfolio_value)
        sharpe = analyzer._calculate_sharpe_ratio(portfolio_value.pct_change().dropna())
        max_dd = analyzer._calculate_max_drawdown(portfolio_value)
        
        print(f"✅ Total Return: {total_return:.2f}%")
        print(f"✅ Sharpe Ratio: {sharpe:.2f}")  
        print(f"✅ Max Drawdown: {max_dd:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_data_handler():
    """Demo data handling"""
    print("\\n📊 Testing Data Handler")
    print("-" * 40)
    
    try:
        from data.data_handler import DataHandler, YFinanceSource
        from core.universal_strategy import AssetType
        
        # Create data handler
        handler = DataHandler()
        print("✅ Created data handler")
        
        # Test symbol validation
        yf_source = YFinanceSource()
        btc_valid = yf_source.validate_symbol('BTC-USD', AssetType.CRYPTO)
        aapl_valid = yf_source.validate_symbol('AAPL', AssetType.STOCKS)
        
        print(f"✅ BTC-USD validation: {btc_valid}")
        print(f"✅ AAPL validation: {aapl_valid}")
        
        # Test date validation
        start, end = handler.validate_date_range('2024-01-01', '2024-06-01')
        print(f"✅ Date validation: {start} to {end}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all demos"""
    print("🚀 IB Trading Universal Backtesting Framework Demo")
    print("=" * 60)
    
    tests = [
        demo_data_handler,
        demo_simple_strategy,
        demo_bitcoin_ftmo,
        demo_risk_manager,
        demo_performance_analyzer
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            results.append(False)
    
    # Summary
    print("\\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} demos passed! Framework ready for use.")
    else:
        print(f"⚠️  {passed}/{total} demos passed. Some components may need attention.")
    
    print("\\n📖 Next steps:")
    print("1. Install dependencies: pip install -r framework/requirements.txt")
    print("2. Run examples: python framework/examples/basic_usage.py")
    print("3. Create your own strategies using the framework")


if __name__ == "__main__":
    main()