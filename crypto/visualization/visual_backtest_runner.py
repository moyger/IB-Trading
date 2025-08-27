#!/usr/bin/env python3
"""
Visual Backtest Runner for BTCUSDT Strategy
Creates interactive browser-based visualizations using backtesting.py

Features:
- Interactive candlestick charts with trade markers
- Confluence score indicators
- Performance analytics dashboard
- Bokeh-powered visualizations
- Export capabilities
"""

import pandas as pd
import numpy as np
from backtesting import Backtest
from backtesting.lib import crossover
import warnings
import webbrowser
import os
from datetime import datetime

# Import our components
from data_fetcher import BTCDataFetcher  
from visual_strategy import BTCVisualStrategy, BTCOptimizedVisualStrategy

warnings.filterwarnings('ignore')

class VisualBacktestRunner:
    """Enhanced visual backtesting with interactive charts"""
    
    def __init__(self):
        """Initialize visual backtest runner"""
        self.data_fetcher = BTCDataFetcher()
        self.results = None
        self.optimization_results = None
        
        print("🎨 VISUAL BACKTEST RUNNER INITIALIZED")
        print("📊 Ready for interactive strategy visualization")
    
    def prepare_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Prepare and clean data for backtesting.py format
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame in backtesting.py format (OHLCV)
        """
        print(f"📊 Preparing data: {start_date} to {end_date}")
        
        # Fetch data using our enhanced data fetcher
        df = self.data_fetcher.fetch_btc_data(start_date, end_date, "1h")
        
        if df is None or df.empty:
            print("❌ Failed to fetch data")
            return None
        
        # Ensure required columns are present and properly named
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                print(f"❌ Missing required column: {col}")
                return None
        
        # Clean data for backtesting.py
        df = df[required_columns].copy()
        df = df.dropna()
        
        # Ensure proper data types
        for col in required_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove any remaining NaN values
        df = df.dropna()
        
        if len(df) < 100:
            print(f"⚠️ Warning: Only {len(df)} data points available")
        
        print(f"✅ Data prepared: {len(df)} periods")
        return df
    
    def run_visual_backtest(self, start_date: str, end_date: str, 
                           strategy_class=BTCVisualStrategy, 
                           cash: float = 10000) -> dict:
        """
        Run visual backtest with interactive charts
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            strategy_class: Strategy class to use
            cash: Initial cash amount
            
        Returns:
            Backtest results dictionary
        """
        print(f"\n🚀 RUNNING VISUAL BACKTEST")
        print("=" * 60)
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"💰 Initial Cash: ${cash:,}")
        print(f"🎯 Strategy: {strategy_class.__name__}")
        
        # Prepare data
        df = self.prepare_data(start_date, end_date)
        if df is None:
            return {}
        
        # Create backtest instance
        bt = Backtest(
            df, 
            strategy_class,
            cash=cash,
            commission=0.001,  # 0.1% commission (typical for crypto)
            exclusive_orders=True
        )
        
        # Run backtest
        print("📈 Running backtest...")
        try:
            results = bt.run()
            self.results = results
            
            # Print summary
            self._print_backtest_summary(results)
            
            # Generate interactive plot
            plot_filename = f"btc_visual_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            print(f"\n📊 Generating interactive plot: {plot_filename}")
            
            # Create the plot
            bt.plot(filename=plot_filename, open_browser=True)
            
            print(f"✅ Interactive plot generated and opened in browser!")
            print(f"📁 File location: {os.path.abspath(plot_filename)}")
            
            # Prepare results dictionary
            results_dict = {
                'backtest_results': results,
                'plot_file': plot_filename,
                'data': df,
                'total_return_pct': (results['Return [%]'] if 'Return [%]' in results else 0),
                'win_rate_pct': (results['Win Rate [%]'] if 'Win Rate [%]' in results else 0),
                'total_trades': (results['# Trades'] if '# Trades' in results else 0),
                'max_drawdown_pct': (results['Max. Drawdown [%]'] if 'Max. Drawdown [%]' in results else 0),
                'sharpe_ratio': (results['Sharpe Ratio'] if 'Sharpe Ratio' in results else 0)
            }
            
            return results_dict
            
        except Exception as e:
            print(f"❌ Backtest failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def run_optimization(self, start_date: str, end_date: str, 
                        cash: float = 10000, metric: str = 'Return [%]') -> dict:
        """
        Run parameter optimization with visual results
        
        Args:
            start_date: Start date for optimization
            end_date: End date for optimization  
            cash: Initial cash amount
            metric: Metric to optimize for
            
        Returns:
            Optimization results
        """
        print(f"\n🔧 RUNNING PARAMETER OPTIMIZATION")
        print("=" * 60)
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"🎯 Optimizing for: {metric}")
        
        # Prepare data
        df = self.prepare_data(start_date, end_date)
        if df is None:
            return {}
        
        # Create backtest instance with optimizable strategy
        bt = Backtest(
            df,
            BTCOptimizedVisualStrategy,
            cash=cash,
            commission=0.001
        )
        
        try:
            print("⚙️ Running optimization (this may take a few minutes)...")
            
            # Run optimization
            optimization_results = bt.optimize(
                confluence_threshold=BTCOptimizedVisualStrategy.confluence_threshold,
                risk_per_trade=BTCOptimizedVisualStrategy.risk_per_trade,
                atr_multiplier=BTCOptimizedVisualStrategy.atr_multiplier,
                profit_target=BTCOptimizedVisualStrategy.profit_target,
                maximize=metric,
                constraint=lambda p: p.confluence_threshold < 7  # Keep reasonable limits
            )
            
            self.optimization_results = optimization_results
            
            # Print optimization summary
            self._print_optimization_summary(optimization_results)
            
            # Generate optimized backtest plot
            plot_filename = f"btc_optimized_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            print(f"\n📊 Generating optimized strategy plot: {plot_filename}")
            
            bt.plot(filename=plot_filename, open_browser=True)
            
            # Prepare results
            opt_results_dict = {
                'optimization_results': optimization_results,
                'plot_file': plot_filename,
                'optimal_params': optimization_results._strategy.__dict__,
                'best_return': optimization_results['Return [%]'],
                'best_sharpe': optimization_results['Sharpe Ratio']
            }
            
            return opt_results_dict
            
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _print_backtest_summary(self, results):
        """Print formatted backtest summary"""
        print(f"\n🏆 VISUAL BACKTEST RESULTS")
        print("-" * 40)
        
        # Key metrics
        metrics = [
            ('Total Return', 'Return [%]', '%'),
            ('Win Rate', 'Win Rate [%]', '%'),
            ('Total Trades', '# Trades', ''),
            ('Max Drawdown', 'Max. Drawdown [%]', '%'),
            ('Sharpe Ratio', 'Sharpe Ratio', ''),
            ('Profit Factor', 'Profit Factor', ''),
            ('Expectancy', 'Expectancy [%]', '%')
        ]
        
        for display_name, key, unit in metrics:
            if key in results:
                value = results[key]
                if unit == '%':
                    print(f"{display_name:<15} {value:>8.2f}{unit}")
                else:
                    print(f"{display_name:<15} {value:>8}")
        
        # Trade statistics
        if 'Avg. Trade [%]' in results:
            print(f"\n📈 TRADE STATISTICS:")
            print(f"Average Trade:      {results['Avg. Trade [%]']:.2f}%")
        
        # Duration statistics  
        if 'Avg. Trade Duration' in results:
            print(f"Avg Duration:       {results['Avg. Trade Duration']}")
    
    def _print_optimization_summary(self, results):
        """Print optimization results summary"""
        print(f"\n🔧 OPTIMIZATION RESULTS")
        print("-" * 40)
        
        # Best parameters found
        print("🎯 OPTIMAL PARAMETERS:")
        strategy_params = results._strategy.__dict__
        param_names = {
            'confluence_threshold': 'Confluence Threshold',
            'risk_per_trade': 'Risk Per Trade (%)',
            'atr_multiplier': 'ATR Multiplier', 
            'profit_target': 'Profit Target (R:R)'
        }
        
        for param, value in strategy_params.items():
            if param in param_names:
                display_name = param_names[param]
                print(f"{display_name:<20} {value}")
        
        # Performance with optimal parameters
        print(f"\n🏆 OPTIMIZED PERFORMANCE:")
        print(f"Best Return:        {results['Return [%]']:.2f}%")
        print(f"Sharpe Ratio:       {results['Sharpe Ratio']:.2f}")
        print(f"Win Rate:           {results['Win Rate [%]']:.1f}%")
        print(f"Max Drawdown:       {results['Max. Drawdown [%]']:.2f}%")
    
    def compare_strategies(self, start_date: str, end_date: str) -> dict:
        """
        Compare default vs optimized strategy performance
        
        Returns:
            Comparison results
        """
        print(f"\n⚖️ STRATEGY COMPARISON")
        print("=" * 60)
        
        # Run default strategy
        print("1️⃣ Running Default Strategy...")
        default_results = self.run_visual_backtest(start_date, end_date, BTCVisualStrategy)
        
        # Run optimization
        print("\n2️⃣ Running Optimization...")
        opt_results = self.run_optimization(start_date, end_date)
        
        # Compare results
        if default_results and opt_results:
            print(f"\n📊 COMPARISON SUMMARY:")
            print("-" * 40)
            
            comparison = {
                'default': {
                    'return_pct': default_results['total_return_pct'],
                    'sharpe_ratio': default_results['sharpe_ratio'],
                    'win_rate_pct': default_results['win_rate_pct'],
                    'max_drawdown_pct': default_results['max_drawdown_pct']
                },
                'optimized': {
                    'return_pct': opt_results['best_return'],
                    'sharpe_ratio': opt_results['best_sharpe'],
                    'win_rate_pct': opt_results['optimization_results']['Win Rate [%]'],
                    'max_drawdown_pct': opt_results['optimization_results']['Max. Drawdown [%]']
                }
            }
            
            # Print comparison
            metrics = [
                ('Total Return (%)', 'return_pct'),
                ('Sharpe Ratio', 'sharpe_ratio'),
                ('Win Rate (%)', 'win_rate_pct'),
                ('Max Drawdown (%)', 'max_drawdown_pct')
            ]
            
            print(f"{'Metric':<20} {'Default':<12} {'Optimized':<12} {'Improvement'}")
            print("-" * 60)
            
            for metric_name, key in metrics:
                default_val = comparison['default'][key]
                opt_val = comparison['optimized'][key]
                
                if default_val != 0:
                    improvement = ((opt_val - default_val) / default_val) * 100
                    print(f"{metric_name:<20} {default_val:<12.2f} {opt_val:<12.2f} {improvement:+.1f}%")
                else:
                    print(f"{metric_name:<20} {default_val:<12.2f} {opt_val:<12.2f} N/A")
            
            return comparison
        
        return {}


def main():
    """Main function to run visual backtesting examples"""
    print("🎨 BTCUSDT VISUAL BACKTESTING SYSTEM")
    print("=" * 50)
    
    # Initialize runner
    runner = VisualBacktestRunner()
    
    # Test with shorter period first (for faster results)
    test_start = "2024-01-01"
    test_end = "2024-03-01"
    
    try:
        print(f"\n🧪 RUNNING TEST BACKTEST")
        print(f"Period: {test_start} to {test_end}")
        
        # Run visual backtest
        results = runner.run_visual_backtest(
            start_date=test_start,
            end_date=test_end,
            cash=10000
        )
        
        if results:
            print(f"\n✅ Visual backtest completed successfully!")
            print(f"📊 Total Return: {results['total_return_pct']:.2f}%")
            print(f"🎯 Win Rate: {results['win_rate_pct']:.1f}%") 
            print(f"📈 Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"📉 Max Drawdown: {results['max_drawdown_pct']:.2f}%")
            
            print(f"\n🌐 Interactive chart opened in your browser!")
            print(f"📁 Chart file: {results['plot_file']}")
        
        # Optional: Run optimization (takes longer)
        run_optimization = input("\n🔧 Run parameter optimization? (y/N): ").lower() == 'y'
        
        if run_optimization:
            print("\n⚙️ Running optimization...")
            opt_results = runner.run_optimization(test_start, test_end)
            
            if opt_results:
                print(f"🏆 Optimization completed!")
                print(f"Best Return: {opt_results['best_return']:.2f}%")
        
    except KeyboardInterrupt:
        print("\n⚠️ Visual backtest interrupted by user")
    except Exception as e:
        print(f"\n❌ Visual backtest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()