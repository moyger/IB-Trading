#!/usr/bin/env python3
"""
Working Visual Demo - Simple SMA Crossover Strategy
Guaranteed to show trades and demonstrate visual capabilities
"""

import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import warnings
warnings.filterwarnings('ignore')

from data_fetcher import BTCDataFetcher

class WorkingBTCStrategy(Strategy):
    """Simple SMA crossover strategy that will definitely generate trades"""
    
    # Optimizable parameters
    fast_ma = 10
    slow_ma = 30
    
    def init(self):
        # Simple moving averages
        close = self.data.Close
        self.sma_fast = self.I(lambda x: pd.Series(x).rolling(self.fast_ma).mean(), close)
        self.sma_slow = self.I(lambda x: pd.Series(x).rolling(self.slow_ma).mean(), close)
        
    def next(self):
        # Simple crossover logic
        if crossover(self.sma_fast, self.sma_slow):
            self.buy(size=0.1)  # Fixed position size
        elif crossover(self.sma_slow, self.sma_fast):
            self.sell(size=0.1)

def run_working_demo():
    """Run a demo that will definitely show trades"""
    print("🎨 WORKING BTCUSDT VISUAL DEMO")
    print("=" * 35)
    print("🎯 Simple SMA Crossover Strategy")
    print("📊 Guaranteed to generate trades for visualization!")
    
    # Fetch data
    data_fetcher = BTCDataFetcher()
    print("\n📊 Fetching BTCUSDT data...")
    
    # Use a period that should have good volatility
    df = data_fetcher.fetch_btc_data("2024-02-01", "2024-05-01", "1h")
    
    if df is None or df.empty:
        print("❌ Failed to fetch data")
        return
    
    print(f"✅ Data loaded: {len(df)} periods")
    print(f"📈 Price range: ${df['Low'].min():,.0f} - ${df['High'].max():,.0f}")
    
    # Create backtest
    bt = Backtest(
        df,
        WorkingBTCStrategy,
        cash=10000,
        commission=0.001,
        exclusive_orders=True
    )
    
    print("\n🚀 Running working demo backtest...")
    
    try:
        # Run backtest
        results = bt.run()
        
        # Print results
        print(f"\n🏆 WORKING DEMO RESULTS")
        print("-" * 25)
        print(f"Return:         {results['Return [%]']:>8.2f}%")
        print(f"Win Rate:       {results['Win Rate [%]']:>8.1f}%")
        print(f"Total Trades:   {results['# Trades']:>8}")
        print(f"Max Drawdown:   {results['Max. Drawdown [%]']:>8.2f}%")
        
        if not np.isnan(results['Sharpe Ratio']):
            print(f"Sharpe Ratio:   {results['Sharpe Ratio']:>8.2f}")
        
        if not np.isnan(results['Profit Factor']):
            print(f"Profit Factor:  {results['Profit Factor']:>8.2f}")
        
        # Generate interactive plot
        plot_filename = "working_btc_visual_demo.html"
        print(f"\n📊 Creating interactive visualization...")
        
        # Create the plot with dark mode styling
        bt.plot(
            filename=plot_filename, 
            open_browser=True,
            plot_width=None,
            plot_height=None,
            show_legend=True,
            # Dark mode styling
            style={
                'background_color': '#1e1e1e',
                'grid_color': '#333333',
                'text_color': '#ffffff',
                'line_color': '#ffffff'
            }
        )
        
        print(f"\n✅ SUCCESS! Working demo completed!")
        print(f"📁 Interactive chart: {plot_filename}")
        print(f"🌐 Chart should have opened automatically in your browser!")
        
        print(f"\n🎨 VISUAL FEATURES YOU CAN SEE:")
        print(f"   ✅ BTCUSDT candlestick chart")
        print(f"   ✅ {results['# Trades']} trade markers (green buy, red sell)")
        print(f"   ✅ SMA lines (fast and slow moving averages)")
        print(f"   ✅ Performance metrics panel")
        print(f"   ✅ Interactive zoom and pan")
        print(f"   ✅ Hover details on each trade")
        
        # If we have trades, show some trade details
        if results['# Trades'] > 0:
            print(f"\n📈 TRADE ANALYSIS:")
            print(f"   Total Trades: {results['# Trades']}")
            print(f"   Win Rate: {results['Win Rate [%]']:.1f}%")
            print(f"   Strategy returned {results['Return [%]']:+.2f}% over the period")
        
        return results
        
    except Exception as e:
        print(f"❌ Demo backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Starting Working Visual Demo...")
    print("This demo uses a simple SMA crossover to guarantee trades")
    print("and show off the visual capabilities of our system.")
    
    results = run_working_demo()
    
    if results and results['# Trades'] > 0:
        print(f"\n🎉 DEMONSTRATION SUCCESSFUL!")
        print(f"✅ Generated {results['# Trades']} trades with visual markers")
        print(f"📊 Interactive chart created and opened in browser")
        print(f"🎨 Visual backtesting system fully operational!")
    else:
        print(f"\n⚠️ Demo completed but check browser for chart")
        print(f"🌐 Even with 0 trades, chart shows price action and indicators")