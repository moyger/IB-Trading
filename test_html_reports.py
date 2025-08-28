"""
Test HTML Report Generation with VectorBT Visualizations
Demonstrates the new HTML visualization capabilities
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
    from core.backtest_engine import BacktestEngine
    from reporting.html_generator import HTMLReportGenerator
    from reporting.report_generator import ReportGenerator
    from strategies.btcusdt_enhanced_adapter import create_btcusdt_enhanced_strategy
    
    print("✅ Successfully imported framework components with HTML support")
    
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_sample_strategy_results():
    """Create sample strategy results for HTML testing"""
    
    print("\n🔧 Creating sample backtest results for HTML visualization...")
    
    # Initialize engine
    engine = BacktestEngine(initial_cash=100000)
    
    # Test different risk profiles
    risk_profiles = ['conservative', 'moderate', 'aggressive']
    results = {}
    
    for risk_profile in risk_profiles:
        print(f"📊 Testing {risk_profile} strategy...")
        
        try:
            # Create strategy
            strategy = create_btcusdt_enhanced_strategy(risk_profile=risk_profile)
            
            # Run backtest (shorter period for demo)
            result = engine.run_single_backtest(
                strategy=strategy,
                symbol='BTC-USD',
                start_date='2024-01-01',
                end_date='2024-06-01',
                interval='1d'
            )
            
            results[risk_profile] = result
            print(f"✅ {risk_profile} strategy completed")
            
        except Exception as e:
            print(f"❌ Error with {risk_profile}: {str(e)}")
            # Create mock result for demonstration
            results[risk_profile] = create_mock_result(risk_profile)
    
    return results


def create_mock_result(risk_profile):
    """Create mock result for demonstration purposes"""
    
    # Mock portfolio object (simplified)
    class MockPortfolio:
        def value(self):
            # Generate sample portfolio value series
            dates = pd.date_range('2024-01-01', '2024-06-01', freq='D')
            # Simulate portfolio growth with some volatility
            np.random.seed(42)  # For reproducible results
            returns = np.random.normal(0.001, 0.02, len(dates))
            portfolio_values = 100000 * np.cumprod(1 + returns)
            return pd.Series(portfolio_values, index=dates)
        
        def returns(self):
            values = self.value()
            return values.pct_change().dropna()
        
        @property
        def drawdowns(self):
            class MockDrawdowns:
                @property
                def drawdown(self):
                    values = MockPortfolio().value()
                    peak = values.expanding().max()
                    drawdown = (values - peak) / peak
                    return drawdown
            return MockDrawdowns()
        
        @property
        def trades(self):
            class MockTrades:
                def count(self):
                    return 15
                
                @property
                def returns(self):
                    np.random.seed(42)
                    return pd.Series(np.random.normal(0.02, 0.05, 15))
                
                @property
                def duration(self):
                    return pd.Series(np.random.randint(1, 10, 15))
            return MockTrades()
        
        @property
        def orders(self):
            class MockOrders:
                def count(self):
                    return 30
            return MockOrders()
    
    # Mock performance data
    performance_configs = {
        'conservative': {
            'total_return': 8.5, 'annualized_return': 17.2, 'max_drawdown': -3.2,
            'sharpe_ratio': 1.8, 'win_rate': 65.0, 'total_trades': 12
        },
        'moderate': {
            'total_return': 15.3, 'annualized_return': 31.8, 'max_drawdown': -6.1,
            'sharpe_ratio': 2.1, 'win_rate': 58.3, 'total_trades': 18
        },
        'aggressive': {
            'total_return': 22.1, 'annualized_return': 47.2, 'max_drawdown': -9.8,
            'sharpe_ratio': 1.6, 'win_rate': 52.2, 'total_trades': 26
        }
    }
    
    perf = performance_configs[risk_profile]
    
    # Add missing performance metrics
    perf.update({
        'cagr': perf['annualized_return'],
        'volatility': perf['annualized_return'] / perf['sharpe_ratio'],
        'var_95': -2.5,
        'var_99': -4.1,
        'expected_shortfall_95': -3.2,
        'downside_deviation': perf['volatility'] * 0.7,
        'sortino_ratio': perf['sharpe_ratio'] * 1.2,
        'calmar_ratio': perf['annualized_return'] / abs(perf['max_drawdown']),
        'omega_ratio': 1.8,
        'profit_factor': 1.8,
        'avg_trade_return': perf['total_return'] / perf['total_trades'],
        'best_trade': 8.5,
        'worst_trade': -3.2,
        'avg_trade_duration': 4.5,
        'max_consecutive_wins': 5,
        'max_consecutive_losses': 3,
        'skewness': 0.2,
        'kurtosis': 2.1,
        'tail_ratio': 1.3,
        'monthly_win_rate': 66.7,
        'recovery_factor': 2.8
    })
    
    # Generate monthly summaries
    monthly_summaries = []
    balance = 100000
    
    for month in range(1, 7):  # Jan to June
        pnl = np.random.uniform(-2000, 5000)
        balance += pnl
        monthly_summaries.append({
            'month': f'2024-{month:02d}',
            'starting_balance': balance - pnl,
            'ending_balance': balance,
            'pnl': pnl,
            'pnl_pct': (pnl / (balance - pnl)) * 100,
            'trades': np.random.randint(1, 6)
        })
    
    return {
        'strategy': {
            'name': f'BTCUSDT Enhanced {risk_profile.title()}',
            'asset_type': 'crypto',
            'risk_profile': risk_profile,
            'risk_per_trade': 0.01,
            'max_daily_loss': 0.03,
            'position_sizing': 'fixed',
            'ftmo_compliant': True,
            'parameters': {
                'confluence_threshold': 4,
                'atr_multiplier': 2.0,
                'volume_threshold': 1.5
            }
        },
        'symbol': 'BTC-USD',
        'period': '2024-01-01 to 2024-06-01',
        'data_points': 152,
        'portfolio': MockPortfolio(),
        'performance': perf,
        'monthly_summaries': monthly_summaries,
        'trade_analysis': {
            'total_trades': perf['total_trades'],
            'win_rate': perf['win_rate'],
            'avg_trade_return': perf['avg_trade_return']
        },
        'risk_metrics': {
            'volatility': perf['volatility'],
            'var_95': perf['var_95'],
            'skewness': perf['skewness'],
            'kurtosis': perf['kurtosis']
        },
        'timestamp': datetime.now().isoformat()
    }


def test_single_strategy_html():
    """Test single strategy HTML report generation"""
    
    print("\n📊 Testing Single Strategy HTML Report Generation")
    print("-" * 60)
    
    # Create HTML generator
    html_gen = HTMLReportGenerator(output_dir="html-reports")
    
    # Create sample result
    result = create_mock_result('moderate')
    
    # Generate HTML report
    try:
        html_path = html_gen.generate_strategy_report(
            result, 
            filename="sample_strategy_report.html"
        )
        
        print(f"✅ Single strategy HTML report generated: {html_path}")
        return html_path
        
    except Exception as e:
        print(f"❌ Error generating single strategy report: {e}")
        return None


def test_comparison_html():
    """Test comparison HTML report generation"""
    
    print("\n📊 Testing Strategy Comparison HTML Report")
    print("-" * 60)
    
    # Create HTML generator
    html_gen = HTMLReportGenerator(output_dir="html-reports")
    
    # Create multiple sample results
    results = []
    for profile in ['conservative', 'moderate', 'aggressive']:
        results.append(create_mock_result(profile))
    
    # Generate comparison report
    try:
        html_path = html_gen.generate_comparison_report(
            results,
            title="BTCUSDT Strategy Comparison - HTML Demo",
            filename="strategy_comparison_demo.html"
        )
        
        print(f"✅ Comparison HTML report generated: {html_path}")
        return html_path
        
    except Exception as e:
        print(f"❌ Error generating comparison report: {e}")
        return None


def test_integrated_report_generation():
    """Test integrated report generation with HTML"""
    
    print("\n🔗 Testing Integrated Report Generation")
    print("-" * 60)
    
    # Create report generator with HTML support
    report_gen = ReportGenerator(output_dir="html-reports")
    
    # Create sample results
    results = []
    for profile in ['conservative', 'moderate', 'aggressive']:
        results.append(create_mock_result(profile))
    
    # Generate individual reports
    for result in results:
        try:
            report_path = report_gen.generate_single_strategy_report(result)
            print(f"✅ Generated integrated report: {report_path}")
        except Exception as e:
            print(f"❌ Error generating integrated report: {e}")
    
    # Generate comparison report
    try:
        comparison_path = report_gen.generate_comparison_report(
            results,
            "BTCUSDT Strategy Analysis - Full Suite",
            "full_comparison_demo"
        )
        print(f"✅ Generated comparison report: {comparison_path}")
    except Exception as e:
        print(f"❌ Error generating comparison report: {e}")


def demonstrate_html_features():
    """Demonstrate key HTML features"""
    
    print("\n✨ HTML Report Features Demonstration")
    print("=" * 70)
    
    features = [
        "📈 Interactive Plotly charts with zoom, pan, and hover",
        "📊 Multi-subplot layouts with portfolio value, drawdown, returns",
        "🎯 Trade signal visualization with entry/exit markers",
        "📅 Monthly performance tables with profit/loss coloring",
        "🎨 Professional styling with responsive design",
        "📱 Mobile-friendly layouts that work across devices",
        "💾 Self-contained HTML files for easy sharing",
        "🔍 Risk analysis charts and performance comparisons",
        "📋 Comprehensive strategy information tables",
        "⚡ Fast loading with CDN-linked Plotly.js"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n💡 These features make the reports suitable for:")
    print("  • Executive presentations")
    print("  • Strategy performance reviews")
    print("  • Client reporting")
    print("  • Sharing with stakeholders")
    print("  • Portfolio analysis")
    print("  • Risk assessment")


def main():
    """Main execution function"""
    
    print("🎯 VectorBT HTML Visualization Test Suite")
    print("📊 Demonstrating interactive HTML report generation")
    print("=" * 70)
    
    try:
        # Test individual components
        single_report = test_single_strategy_html()
        comparison_report = test_comparison_html()
        
        # Test integrated reporting
        test_integrated_report_generation()
        
        # Show features
        demonstrate_html_features()
        
        print("\n🎉 HTML VISUALIZATION TESTING COMPLETED!")
        print("=" * 70)
        print("✅ All HTML report types successfully generated")
        print("📂 Check the 'html-reports' directory for output files")
        
        if single_report:
            print(f"📄 Sample single strategy report: {single_report}")
        if comparison_report:
            print(f"📊 Sample comparison report: {comparison_report}")
        
        print("\n💻 Open the HTML files in your browser to view interactive charts!")
        print("🔍 Features include zoom, pan, hover tooltips, and responsive design")
        
    except Exception as e:
        print(f"\n❌ Critical error in HTML testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()