#!/usr/bin/env python3
"""
Simple test of our visual backtesting system
Demonstrates the interactive chart capabilities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Test imports
try:
    from backtesting import Backtest, Strategy
    from backtesting.lib import crossover
    print("✅ backtesting.py library imported successfully")
    BACKTESTING_AVAILABLE = True
except ImportError as e:
    print(f"❌ backtesting.py import failed: {e}")
    BACKTESTING_AVAILABLE = False

try:
    import plotly.graph_objects as go
    print("✅ Plotly imported successfully")
    PLOTLY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Plotly import failed: {e}")
    PLOTLY_AVAILABLE = False

try:
    import dash
    print("✅ Dash imported successfully")
    DASH_AVAILABLE = True
except ImportError as e:
    print(f"❌ Dash import failed: {e}")
    DASH_AVAILABLE = False

# Simple test strategy
class SimpleTestStrategy(Strategy):
    """Simple SMA crossover strategy for testing"""
    
    def init(self):
        # Calculate simple moving averages
        close = self.data.Close
        self.sma_fast = self.I(lambda x: pd.Series(x).rolling(10).mean(), close)
        self.sma_slow = self.I(lambda x: pd.Series(x).rolling(20).mean(), close)
    
    def next(self):
        # Simple crossover strategy
        if crossover(self.sma_fast, self.sma_slow):
            self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            self.sell()

def create_sample_data():
    """Create sample OHLCV data for testing"""
    print("📊 Creating sample BTCUSDT data...")
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end='2024-02-01', freq='1H')
    
    # Simulate price movement
    price_base = 42000
    np.random.seed(42)  # For reproducible results
    
    # Generate realistic OHLCV data
    data = []
    current_price = price_base
    
    for date in dates:
        # Random walk with drift
        price_change = np.random.normal(0, 0.002)  # 0.2% average volatility
        current_price *= (1 + price_change)
        
        # Generate OHLC around current price
        volatility = np.random.uniform(0.001, 0.003)  # 0.1-0.3% intrabar volatility
        
        open_price = current_price
        high_price = current_price * (1 + volatility)
        low_price = current_price * (1 - volatility)
        close_price = current_price * (1 + np.random.uniform(-volatility/2, volatility/2))
        
        # Ensure OHLC relationships are valid
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Random volume
        volume = np.random.uniform(100, 1000)
        
        data.append({
            'Open': round(open_price, 2),
            'High': round(high_price, 2),
            'Low': round(low_price, 2), 
            'Close': round(close_price, 2),
            'Volume': round(volume, 0)
        })
        
        current_price = close_price
    
    df = pd.DataFrame(data, index=dates)
    print(f"✅ Created {len(df)} data points from {df.index[0]} to {df.index[-1]}")
    
    return df

def test_visual_backtest():
    """Test the visual backtesting system"""
    print(f"\n🧪 TESTING VISUAL BACKTESTING SYSTEM")
    print("=" * 50)
    
    if not BACKTESTING_AVAILABLE:
        print("❌ Cannot test - backtesting.py not available")
        return
    
    # Create sample data
    df = create_sample_data()
    
    try:
        print("🚀 Running backtest with interactive visualization...")
        
        # Create backtest
        bt = Backtest(
            df,
            SimpleTestStrategy,
            cash=10000,
            commission=0.001
        )
        
        # Run backtest
        results = bt.run()
        
        # Print results
        print(f"\n📊 BACKTEST RESULTS:")
        print(f"Return: {results['Return [%]']:.2f}%")
        print(f"Win Rate: {results['Win Rate [%]']:.1f}%")
        print(f"# Trades: {results['# Trades']}")
        print(f"Max Drawdown: {results['Max. Drawdown [%]']:.2f}%")
        
        # Generate interactive plot
        print(f"\n🎨 Generating interactive chart...")
        plot_filename = f"test_visual_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Create the plot (this will open in browser)
        bt.plot(filename=plot_filename, open_browser=False)  # Don't auto-open for test
        
        print(f"✅ Visual backtest completed!")
        print(f"📁 Interactive chart saved: {plot_filename}")
        print(f"🌐 Open this file in your browser to see the interactive charts!")
        
        return True
        
    except Exception as e:
        print(f"❌ Visual backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plotly_charts():
    """Test Plotly chart generation"""
    print(f"\n📈 TESTING PLOTLY CHARTS")
    print("=" * 30)
    
    if not PLOTLY_AVAILABLE:
        print("❌ Cannot test - Plotly not available")
        return
    
    try:
        # Create sample data
        df = create_sample_data()
        
        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="BTCUSDT Test"
        ))
        
        fig.update_layout(
            title="🧪 Test BTCUSDT Candlestick Chart",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False
        )
        
        # Save chart
        chart_filename = f"test_plotly_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_filename)
        
        print(f"✅ Plotly chart created successfully!")
        print(f"📁 Chart saved: {chart_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Plotly chart failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎨 VISUAL BACKTESTING SYSTEM TEST")
    print("=" * 40)
    
    # Test component availability
    print(f"📊 System Components:")
    print(f"   backtesting.py: {'✅' if BACKTESTING_AVAILABLE else '❌'}")
    print(f"   Plotly:         {'✅' if PLOTLY_AVAILABLE else '❌'}")
    print(f"   Dash:           {'✅' if DASH_AVAILABLE else '❌'}")
    
    # Run tests
    success_count = 0
    total_tests = 2
    
    # Test 1: Visual backtesting
    if test_visual_backtest():
        success_count += 1
    
    # Test 2: Plotly charts
    if test_plotly_charts():
        success_count += 1
    
    # Summary
    print(f"\n🏆 TEST SUMMARY")
    print("=" * 20)
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.0f}%")
    
    if success_count == total_tests:
        print("✅ All tests passed! Visual system is ready.")
        print("\n🎯 Next Steps:")
        print("   1. Run 'python visual_backtest_runner.py' for full backtesting")
        print("   2. Run 'python dashboard_app.py' for interactive dashboard")
        print("   3. Open generated HTML files in browser for charts")
    else:
        print("❌ Some tests failed. Check error messages above.")

if __name__ == "__main__":
    main()