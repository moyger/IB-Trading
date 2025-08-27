#!/usr/bin/env python3
"""
Bybit 1H Trend Composite Strategy
Main execution script
"""

import sys
import os
import argparse
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.strategy import Bybit1HTrendStrategy
from config.settings import Config
from utils.logger import logger

def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Bybit 1H Trend Composite Strategy - Based on FTMO Success'
    )
    
    parser.add_argument(
        '--mode',
        choices=['scan', 'trade', 'monitor', 'backtest'],
        default='scan',
        help='Operation mode (default: scan)'
    )
    
    parser.add_argument(
        '--testnet',
        action='store_true',
        default=True,
        help='Use testnet (default: True)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Use live trading (overrides --testnet)'
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        help='Symbols to trade (e.g., BTC ETH SOL)'
    )
    
    parser.add_argument(
        '--risk',
        type=float,
        help='Risk per trade percentage (default: 1.5)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute trades (not just signals)'
    )
    
    args = parser.parse_args()
    
    # Determine testnet setting
    testnet = not args.live if args.live else args.testnet
    
    print("=" * 70)
    print("🚀 BYBIT 1H TREND COMPOSITE STRATEGY")
    print("   Cryptocurrency Adaptation of FTMO 68.4% Win Rate Strategy")
    print("=" * 70)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Mode: {args.mode.upper()}")
    print(f"💱 Network: {'TESTNET' if testnet else '⚠️  LIVE TRADING'}")
    print(f"🎯 Execute Trades: {'YES' if args.execute else 'NO (Signals Only)'}")
    print("=" * 70)
    
    # Load configuration
    config = Config()
    
    # Override configuration with command line arguments
    if args.symbols:
        # Convert symbol format
        formatted_symbols = []
        for symbol in args.symbols:
            symbol = symbol.upper()
            if '/' not in symbol:
                symbol = f"{symbol}/USDT:USDT"
            formatted_symbols.append(symbol)
        config.symbols.symbols = formatted_symbols
    
    if args.risk:
        config.trading.risk_per_trade = args.risk
    
    # Get API credentials from environment
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not testnet and (not api_key or not api_secret):
        print("❌ API credentials required for live trading")
        print("   Set BYBIT_API_KEY and BYBIT_API_SECRET environment variables")
        return 1
    
    # Initialize strategy
    try:
        strategy = Bybit1HTrendStrategy(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
            config=config
        )
        
        if not strategy.initialize():
            print("❌ Failed to initialize strategy")
            return 1
        
    except Exception as e:
        print(f"❌ Error initializing strategy: {e}")
        return 1
    
    # Execute based on mode
    try:
        if args.mode == 'scan':
            # One-time scan for signals
            print("\n🔍 SCANNING FOR SIGNALS...")
            signals = strategy.scan_markets()
            
            if signals:
                print(f"\n✅ Found {len(signals)} trading signals:")
                print("-" * 60)
                for i, signal in enumerate(signals, 1):
                    print(f"\n{i}. {signal.action} {signal.symbol}")
                    print(f"   Entry: ${signal.entry_price:.4f}")
                    print(f"   Stop Loss: ${signal.stop_loss:.4f}")
                    print(f"   Take Profit: ${signal.take_profit:.4f}")
                    print(f"   Risk/Reward: {signal.risk_reward:.2f}:1")
                    print(f"   Confidence: {signal.confidence:.1%}")
                    print(f"   Position Size: {signal.position_size:.6f}")
                    
                    # Log signal
                    logger.log_signal({
                        'symbol': signal.symbol,
                        'action': signal.action,
                        'entry_price': signal.entry_price,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit,
                        'confidence': signal.confidence,
                        'risk_reward': signal.risk_reward
                    })
            else:
                print("\n📊 No trading signals at this time")
            
            # Show performance summary
            performance = strategy.get_performance_summary()
            print("\n📊 PERFORMANCE METRICS")
            print("-" * 60)
            for key, value in performance.items():
                print(f"{key}: {value}")
        
        elif args.mode == 'trade':
            # Continuous trading mode
            print("\n🤖 STARTING AUTOMATED TRADING")
            print("⚠️  Press Ctrl+C to stop")
            
            if not args.execute:
                print("\n📊 SIGNAL MODE: Trades will NOT be executed")
                print("   Use --execute flag to enable live trading")
            
            strategy.start(execute_trades=args.execute)
        
        elif args.mode == 'monitor':
            # Monitor existing positions
            print("\n👁️  MONITORING POSITIONS")
            
            import time
            while True:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
                
                # Update positions
                strategy.update_positions()
                
                # Get current positions
                positions = strategy.client.get_positions()
                
                if positions:
                    print(f"\n📊 Open Positions ({len(positions)}):")
                    for pos in positions:
                        print(f"  {pos.symbol}: {pos.side} | "
                              f"Size: {pos.size} | "
                              f"Entry: ${pos.entry_price:.4f} | "
                              f"P&L: ${pos.pnl:.2f} ({pos.pnl_pct:.2f}%)")
                else:
                    print("📊 No open positions")
                
                # Show performance
                performance = strategy.get_performance_summary()
                print("\n📊 Performance:")
                print(f"  Win Rate: {performance['win_rate']}")
                print(f"  Daily P&L: {performance['daily_pnl']}")
                print(f"  Drawdown: {performance['current_drawdown']}")
                
                print("\n⏳ Next update in 60 seconds...")
                time.sleep(60)
        
        elif args.mode == 'backtest':
            print("\n📊 BACKTESTING MODE")
            print("⚠️  Backtesting module coming soon...")
            print("   Use scan or trade mode for live market analysis")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Strategy stopped by user")
        
        # Final performance report
        if strategy:
            performance = strategy.get_performance_summary()
            print("\n📊 FINAL PERFORMANCE REPORT")
            print("=" * 60)
            for key, value in performance.items():
                print(f"{key}: {value}")
            
            # Log final performance
            logger.log_performance(performance)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Strategy error: {e}")
        return 1
    
    print("\n👋 Strategy execution complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())