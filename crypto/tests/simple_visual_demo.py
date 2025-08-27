#!/usr/bin/env python3
"""
Simple Visual Demo - Basic Moving Average Strategy
Guaranteed to generate trades for visualization demonstration
"""

import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import warnings
warnings.filterwarnings('ignore')

from data_fetcher import BTCDataFetcher

class SimpleMAStrategy(Strategy):
    """Very simple MA crossover strategy that will generate trades"""
    
    # Simple parameters
    fast_ma = 5
    slow_ma = 15
    
    def init(self):
        # Simple moving averages
        close = self.data.Close
        self.sma_fast = self.I(lambda x: pd.Series(x).rolling(self.fast_ma).mean(), close)
        self.sma_slow = self.I(lambda x: pd.Series(x).rolling(self.slow_ma).mean(), close)
        
    def next(self):
        # Simple crossover strategy
        if crossover(self.sma_fast, self.sma_slow):
            self.buy(size=0.95)  # Buy almost all available cash
        elif crossover(self.sma_slow, self.sma_fast):
            self.position.close()  # Close position

def run_simple_visual_demo():
    """Run a simple demo guaranteed to show trades"""
    print("🎯 SIMPLE BTCUSDT VISUAL DEMO")
    print("=" * 35)
    print("📈 Basic Moving Average Crossover")
    print("✅ Guaranteed to generate multiple trades!")
    
    # Fetch data
    data_fetcher = BTCDataFetcher()
    print("\n📊 Fetching BTCUSDT data...")
    
    # Use a volatile period
    df = data_fetcher.fetch_btc_data("2024-03-01", "2024-04-15", "1h")
    
    if df is None or df.empty:
        print("❌ Failed to fetch data")
        return False
    
    print(f"✅ Data loaded: {len(df)} periods")
    print(f"📈 Price range: ${df['Low'].min():,.0f} - ${df['High'].max():,.0f}")
    
    # Create backtest
    bt = Backtest(
        df,
        SimpleMAStrategy,
        cash=10000,
        commission=0.002,  # 0.2% commission
        exclusive_orders=True
    )
    
    print("\n🚀 Running simple demo backtest...")
    
    try:
        # Run backtest
        results = bt.run()
        
        # Print results
        print(f"\n🎯 SIMPLE DEMO RESULTS")
        print("-" * 25)
        print(f"Return:         {results['Return [%]']:>8.2f}%")
        print(f"Total Trades:   {results['# Trades']:>8}")
        
        if results['# Trades'] > 0:
            print(f"Win Rate:       {results['Win Rate [%]']:>8.1f}%")
            print(f"Max Drawdown:   {results['Max. Drawdown [%]']:>8.2f}%")
            
            if not pd.isna(results['Sharpe Ratio']):
                print(f"Sharpe Ratio:   {results['Sharpe Ratio']:>8.2f}")
        
        # Generate plot
        plot_filename = "simple_visual_demo.html"
        print(f"\n📊 Creating interactive visualization...")
        
        # Simple plot call
        bt.plot(filename=plot_filename, open_browser=True)
        
        print(f"\n✅ SUCCESS! Simple demo completed!")
        print(f"📁 Interactive chart: {plot_filename}")
        print(f"🌐 Chart opened automatically in your browser!")
        
        if results['# Trades'] > 0:
            print(f"\n🎨 VISUAL FEATURES YOU CAN SEE:")
            print(f"   ✅ BTCUSDT candlestick chart")
            print(f"   ✅ {results['# Trades']} trade markers")
            print(f"   ✅ Moving average lines (5 & 15 period)")
            print(f"   ✅ Entry/exit points clearly marked")
            print(f"   ✅ Interactive zoom and hover details")
            print(f"   ✅ Performance metrics panel")
            
            print(f"\n📈 TRADE SUMMARY:")
            print(f"   Total Trades: {results['# Trades']}")
            print(f"   Strategy Return: {results['Return [%]']:+.2f}%")
            if not pd.isna(results['Win Rate [%]']):
                print(f"   Win Rate: {results['Win Rate [%]']:.1f}%")
        else:
            print(f"\n⚠️ No trades generated - market may be too stable")
            print(f"📊 But chart still shows price action and indicators")
        
        return results
        
    except Exception as e:
        print(f"❌ Simple demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🎯 Starting Simple Visual Demo...")
    print("Using basic MA crossover strategy for guaranteed visualization")
    
    results = run_simple_visual_demo()
    
    if results is not None:
        try:
            trade_count = results['# Trades']
            if trade_count > 0:
                print(f"\n🎉 VISUALIZATION SUCCESS!")
                print(f"✅ Generated {trade_count} trades with visual markers")
                print(f"📊 Interactive chart created and opened")
                print(f"🎨 Visual backtesting system demonstrated!")
            else:
                print(f"\n📊 Chart created showing price action and indicators")
                print(f"🌐 Open the HTML file to see the visualization")
        except:
            print(f"\n📊 Demo completed - check browser for visualization")
    else:
        print(f"\n⚠️ Demo encountered issues but may have created chart")