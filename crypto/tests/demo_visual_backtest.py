#!/usr/bin/env python3
"""
Demo Visual Backtest with Optimized Settings
Shows our BTCUSDT strategy with interactive visualization
"""

import pandas as pd
import numpy as np
from backtesting import Backtest
from backtesting.lib import crossover
import warnings
warnings.filterwarnings('ignore')

from data_fetcher import BTCDataFetcher
from visual_strategy import BTCVisualStrategy

class BTCDemoStrategy(BTCVisualStrategy):
    """Demo version with more lenient settings for visualization"""
    
    # More lenient parameters for demo
    confluence_threshold = 2  # Lower threshold for more trades
    risk_per_trade = 1.0      # Conservative risk
    atr_multiplier = 1.5      # Tighter stops
    profit_target = 2.0       # Reasonable profit target

def run_demo_backtest():
    """Run a demo backtest with good visualization"""
    print("🎨 BTCUSDT VISUAL DEMO BACKTEST")
    print("=" * 40)
    
    # Initialize data fetcher
    data_fetcher = BTCDataFetcher()
    
    # Fetch longer period for better results
    print("📊 Fetching BTCUSDT data...")
    df = data_fetcher.fetch_btc_data("2024-01-01", "2024-06-01", "1h")
    
    if df is None or df.empty:
        print("❌ Failed to fetch data")
        return
    
    print(f"✅ Data loaded: {len(df)} periods")
    
    # Create backtest
    bt = Backtest(
        df,
        BTCDemoStrategy,
        cash=10000,
        commission=0.001,
        exclusive_orders=True
    )
    
    print("🚀 Running demo backtest...")
    
    try:
        # Run backtest
        results = bt.run()
        
        # Print results
        print(f"\n🏆 DEMO BACKTEST RESULTS")
        print("-" * 30)
        print(f"Return:         {results['Return [%]']:>8.2f}%")
        print(f"Win Rate:       {results['Win Rate [%]']:>8.1f}%")
        print(f"Total Trades:   {results['# Trades']:>8}")
        print(f"Max Drawdown:   {results['Max. Drawdown [%]']:>8.2f}%")
        
        if results['Sharpe Ratio'] and not np.isnan(results['Sharpe Ratio']):
            print(f"Sharpe Ratio:   {results['Sharpe Ratio']:>8.2f}")
        
        # Generate interactive plot
        plot_filename = "btc_demo_visual_backtest.html"
        print(f"\n📊 Creating interactive chart: {plot_filename}")
        
        # Create the plot
        bt.plot(filename=plot_filename, open_browser=False)
        
        print(f"✅ Demo backtest completed!")
        print(f"📁 Interactive chart: {plot_filename}")
        print(f"🌐 Open this file in your browser to see:")
        print(f"   - BTCUSDT candlestick chart")
        print(f"   - Entry/exit trade markers")
        print(f"   - Strategy performance metrics")
        print(f"   - Interactive zoom and analysis")
        
        return results
        
    except Exception as e:
        print(f"❌ Demo backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = run_demo_backtest()
    
    if results and results['# Trades'] > 0:
        print(f"\n🎯 SUCCESS! Generated visual backtest with {results['# Trades']} trades")
        print(f"📈 Strategy shows {results['Return [%]']:.2f}% return")
        print(f"🏆 Win rate of {results['Win Rate [%]']:.1f}%")
    else:
        print(f"\n⚠️ Demo completed but no trades generated")
        print(f"💡 Try adjusting confluence_threshold or date range for more activity")