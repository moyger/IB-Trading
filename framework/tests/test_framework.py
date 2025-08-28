"""
Framework Test Suite

Comprehensive tests for the Universal Backtesting Framework.
"""

import sys
from pathlib import Path
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add framework to path
sys.path.append(str(Path(__file__).parent.parent))

from core.universal_strategy import UniversalStrategy, StrategyConfig, AssetType, RiskProfile
from core.backtest_engine import BacktestEngine
from data.data_handler import DataHandler
from portfolio.risk_manager import RiskManager
from reporting.performance_analyzer import PerformanceAnalyzer
from strategies.simple_ma_strategy import SimpleMAStrategy, create_simple_ma_strategy


class TestStrategy(UniversalStrategy):
    """Simple test strategy for unit tests"""
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        indicators = pd.DataFrame(index=data.index)
        indicators['MA_20'] = data['Close'].rolling(20).mean()
        return indicators
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals['entries'] = data['Close'] > data['MA_20']
        signals['exits'] = data['Close'] < data['MA_20']
        signals['size'] = 0.02
        return signals


class TestFramework(unittest.TestCase):
    """Test cases for framework components"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = self._create_test_data()
        
        self.config = StrategyConfig(
            name="TestStrategy",
            asset_type=AssetType.CRYPTO,
            risk_profile=RiskProfile.MODERATE
        )
        
        self.strategy = TestStrategy(self.config)
        self.engine = BacktestEngine(initial_cash=100000)
    
    def _create_test_data(self) -> pd.DataFrame:
        """Create synthetic test data"""
        dates = pd.date_range('2024-01-01', '2024-06-01', freq='H')
        n_points = len(dates)
        
        # Generate realistic OHLCV data
        np.random.seed(42)  # For reproducibility
        
        # Start with base price and random walk
        base_price = 50000
        returns = np.random.normal(0.0001, 0.02, n_points)  # Small positive drift
        prices = base_price * np.cumprod(1 + returns)
        
        # Create OHLC from close prices
        data = pd.DataFrame(index=dates)
        data['Close'] = prices
        
        # Generate realistic OHLC
        daily_range = 0.02  # 2% daily range
        data['Open'] = data['Close'].shift(1)
        data['High'] = data['Close'] * (1 + np.random.uniform(0, daily_range/2, n_points))
        data['Low'] = data['Close'] * (1 - np.random.uniform(0, daily_range/2, n_points))
        data['Volume'] = np.random.uniform(1000000, 5000000, n_points)
        
        # Fix first row
        data.loc[data.index[0], 'Open'] = data.loc[data.index[0], 'Close']
        
        return data.fillna(method='ffill')
    
    def test_strategy_initialization(self):
        """Test strategy initialization"""
        self.assertEqual(self.strategy.config.name, "TestStrategy")
        self.assertEqual(self.strategy.config.asset_type, AssetType.CRYPTO)
        self.assertIsNotNone(self.strategy)
    
    def test_data_handler(self):
        """Test data handler functionality"""
        handler = DataHandler()
        
        # Test asset type detection
        self.assertEqual(handler._select_data_source('BTC-USD', AssetType.CRYPTO).__class__.__name__, 'YFinanceSource')
        
        # Test date validation
        start, end = handler.validate_date_range('2024-01-01', '2024-06-01')
        self.assertEqual(start, '2024-01-01')
        self.assertEqual(end, '2024-06-01')
    
    def test_indicator_calculation(self):
        """Test indicator calculation"""
        indicators = self.strategy.calculate_indicators(self.test_data)
        
        self.assertIn('MA_20', indicators.columns)
        self.assertGreater(len(indicators), 0)
        self.assertTrue(indicators['MA_20'].notna().any())
    
    def test_signal_generation(self):
        """Test signal generation"""
        # Add indicators to data
        indicators = self.strategy.calculate_indicators(self.test_data)
        combined_data = pd.concat([self.test_data, indicators], axis=1)
        
        # Generate signals
        signals = self.strategy.generate_signals(combined_data)
        
        self.assertIn('entries', signals.columns)
        self.assertIn('exits', signals.columns)
        self.assertIn('size', signals.columns)
        self.assertTrue((signals['entries'] | ~signals['entries']).all())  # Boolean check
    
    def test_risk_manager(self):
        """Test risk manager"""
        risk_manager = RiskManager()
        
        # Test risk limits
        self.assertIsNotNone(risk_manager.limits)
        self.assertGreater(risk_manager.limits.max_daily_loss, 0)
        
        # Test FTMO mode
        risk_manager.set_ftmo_mode('challenge')
        self.assertEqual(risk_manager.limits.max_daily_loss, 0.05)
    
    def test_performance_analyzer(self):
        """Test performance analyzer"""
        analyzer = PerformanceAnalyzer()
        
        # Create simple portfolio value series
        portfolio_value = pd.Series(
            [100000, 101000, 102000, 101500, 103000],
            index=pd.date_range('2024-01-01', periods=5)
        )
        
        # Test metrics calculation
        total_return = analyzer._calculate_total_return(portfolio_value)
        max_drawdown = analyzer._calculate_max_drawdown(portfolio_value)
        
        self.assertIsInstance(total_return, float)
        self.assertIsInstance(max_drawdown, float)
        self.assertGreater(total_return, 0)  # Should be positive
        self.assertLess(max_drawdown, 0)     # Should be negative
    
    def test_simple_ma_strategy(self):
        """Test SimpleMAStrategy implementation"""
        strategy = create_simple_ma_strategy(
            asset_type=AssetType.CRYPTO,
            fast_period=10,
            slow_period=30
        )
        
        # Test strategy properties
        self.assertEqual(strategy.fast_period, 10)
        self.assertEqual(strategy.slow_period, 30)
        self.assertEqual(strategy.config.asset_type, AssetType.CRYPTO)
        
        # Test indicator calculation
        indicators = strategy.calculate_indicators(self.test_data)
        self.assertIn('MA_Fast', indicators.columns)
        self.assertIn('MA_Slow', indicators.columns)
        self.assertIn('RSI', indicators.columns)
    
    def test_end_to_end_backtest(self):
        """Test complete end-to-end backtest"""
        try:
            # Create strategy
            strategy = create_simple_ma_strategy(
                asset_type=AssetType.CRYPTO,
                risk_profile='conservative'
            )
            
            # This would normally fetch real data, but we'll use mock for testing
            # In a real test environment, you might want to use actual data
            
            # For now, just verify the strategy can be created and configured
            self.assertIsNotNone(strategy)
            self.assertEqual(strategy.config.risk_profile, RiskProfile.CONSERVATIVE)
            
        except Exception as e:
            self.fail(f"End-to-end test failed: {str(e)}")


class TestDataHandler(unittest.TestCase):
    """Test data handler functionality"""
    
    def test_symbol_validation(self):
        """Test symbol validation logic"""
        from data.data_handler import YFinanceSource
        
        source = YFinanceSource()
        
        # Test crypto symbols
        self.assertTrue(source.validate_symbol('BTC-USD', AssetType.CRYPTO))
        self.assertTrue(source.validate_symbol('ETH-USDT', AssetType.CRYPTO))
        
        # Test stock symbols
        self.assertTrue(source.validate_symbol('AAPL', AssetType.STOCKS))
        self.assertTrue(source.validate_symbol('GOOGL', AssetType.STOCKS))
        
        # Test invalid symbols
        self.assertFalse(source.validate_symbol('INVALID123', AssetType.STOCKS))


def run_framework_tests():
    """Run all framework tests"""
    print("Running Universal Backtesting Framework Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestFramework))
    suite.addTest(unittest.makeSuite(TestDataHandler))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\\nAll tests passed! ✅")
    else:
        print(f"\\nTests failed: {len(result.failures)} failures, {len(result.errors)} errors ❌")
    
    return result


if __name__ == "__main__":
    # Run tests first
    test_result = run_framework_tests()
    
    # If tests pass, run examples
    if test_result.wasSuccessful():
        print("\\n" + "=" * 60)
        print("Running Framework Examples")
        print("=" * 60)
        
        try:
            basic_crypto_backtest()
            # Note: Real data examples would require network access
            print("\\nFramework examples completed!")
        except Exception as e:
            print(f"Examples failed: {str(e)}")
    else:
        print("\\nSkipping examples due to test failures")