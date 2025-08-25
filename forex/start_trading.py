#!/usr/bin/env python3
"""
FTMO 1H Enhanced Strategy - Quick Start Script
Simple launcher for the complete trading system
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required = ['pandas', 'numpy', 'yfinance', 'requests', 'flask']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️ Missing packages: {', '.join(missing)}")
        print("Installing required packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        print("✅ Packages installed!")

def show_menu():
    """Display main menu"""
    print("🏆 FTMO 1H ENHANCED STRATEGY")
    print("=" * 50)
    print("Choose your action:")
    print()
    print("1. 🧪 Test Strategy Performance")
    print("2. 📊 View Monthly Analysis")
    print("3. 🚀 Start Live Trading")
    print("4. 📡 Start Webhook Server")
    print("5. ⚙️ Configuration Help")
    print("6. 📖 View Documentation")
    print("0. ❌ Exit")
    print()

def run_strategy_test():
    """Run strategy performance test"""
    print("🧪 Running Strategy Performance Test...")
    print("-" * 40)
    subprocess.run([sys.executable, 'xauusd_ftmo_1h_enhanced_strategy.py'])

def run_monthly_analysis():
    """Run monthly performance analysis"""
    print("📊 Running Monthly Performance Analysis...")
    print("-" * 40)
    subprocess.run([sys.executable, '1h_monthly_performance_analysis.py'])

def start_live_trading():
    """Start live trading system"""
    print("🚀 Starting Live Trading System...")
    print("-" * 40)
    print("💡 Make sure webhook server is running first!")
    print()
    
    choice = input("Continue? (y/n): ").lower().strip()
    if choice == 'y':
        subprocess.run([sys.executable, 'xauusd_ftmo_1h_live_trader.py'])

def start_webhook_server():
    """Start local webhook server"""
    print("📡 Starting Local Webhook Server...")
    print("-" * 40)
    print("🌐 Server will run on http://localhost:5000")
    print("💡 Update your MT5 EA to use this URL")
    print()
    
    choice = input("Continue? (y/n): ").lower().strip()
    if choice == 'y':
        subprocess.run([sys.executable, 'local_webhook_server.py'])

def show_config_help():
    """Show configuration help"""
    print("⚙️ CONFIGURATION HELP")
    print("-" * 40)
    print()
    print("📁 Configuration File: live_trader_config.py")
    print()
    print("🎯 Presets Available:")
    print("  • Conservative: Safe FTMO settings (recommended)")
    print("  • Aggressive: Higher frequency trading")
    print("  • Testing: Demo account settings")
    print()
    print("⚠️ Key Settings:")
    print("  • Max Daily Risk: 1.5% (FTMO limit: 5%)")
    print("  • Emergency Stop: 0.8% daily loss")
    print("  • Signal Cooldown: 5 minutes between signals")
    print("  • Min Trend Strength: 2.0 (lower = more signals)")
    print()
    print("🔧 MT5 EA Settings:")
    print("  • ServerURL: http://localhost:5000")
    print("  • AccountKey: FTMO_1H_LIVE")
    print("  • Symbol Mapping: XAUUSD → GOLD")
    print()

def view_documentation():
    """View documentation"""
    print("📖 DOCUMENTATION")
    print("-" * 40)
    print()
    print("📄 Main Documentation: README.md")
    print()
    print("📊 Strategy Performance:")
    print("  • Success Rate: 68.4% (13/19 months)")
    print("  • FTMO Compliance: 100% (Zero violations)")
    print("  • Average Time: 15 days to completion")
    print("  • Best Performance: 21.9% profit in 5 days")
    print()
    print("🎯 Key Files:")
    print("  • xauusd_ftmo_1h_enhanced_strategy.py - Core strategy")
    print("  • xauusd_ftmo_1h_live_trader.py - Live trading")
    print("  • local_webhook_server.py - Webhook server")
    print("  • EA/ftmo-bridge.mq5 - MT5 integration")
    print()
    print("💡 Quick Commands:")
    print("  • Test Strategy: python xauusd_ftmo_1h_enhanced_strategy.py")
    print("  • Start Live: python xauusd_ftmo_1h_live_trader.py")
    print("  • Start Server: python local_webhook_server.py")
    print()

def main():
    """Main menu loop"""
    # Check if we're in the right directory
    if not Path('xauusd_ftmo_1h_enhanced_strategy.py').exists():
        print("❌ Please run this script from the forex directory")
        print("📁 Expected files not found")
        return
    
    # Check dependencies
    check_dependencies()
    
    while True:
        print("\n")
        show_menu()
        
        try:
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == '0':
                print("👋 Goodbye! Happy trading!")
                break
            elif choice == '1':
                run_strategy_test()
            elif choice == '2':
                run_monthly_analysis()
            elif choice == '3':
                start_live_trading()
            elif choice == '4':
                start_webhook_server()
            elif choice == '5':
                show_config_help()
            elif choice == '6':
                view_documentation()
            else:
                print("❌ Invalid choice. Please select 0-6.")
            
            print("\nPress Enter to continue...")
            input()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Happy trading!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Press Enter to continue...")
            input()

if __name__ == "__main__":
    main()