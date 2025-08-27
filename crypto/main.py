#!/usr/bin/env python3
"""
BTCUSDT Enhanced Trading System - Main Entry Point
Organized and clean interface for all trading operations
"""

import sys
import os
from pathlib import Path

# Add subdirectories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategies'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'visualization'))

def show_menu():
    """Display main menu options"""
    print("\n🚀 BTCUSDT ENHANCED TRADING SYSTEM")
    print("=" * 45)
    print("1. 📊 Run Enhanced Strategy Backtest")
    print("2. 🌙 Dark Mode Visual Analysis") 
    print("3. 📈 Interactive Dashboard")
    print("4. 🧪 Quick Visual Demo")
    print("5. 📋 System Status")
    print("6. 🗂️  File Organization")
    print("0. ❌ Exit")
    print("=" * 45)

def run_enhanced_backtest():
    """Run the proven enhanced strategy"""
    try:
        from btcusdt_enhanced_strategy import main as run_strategy
        run_strategy()
    except ImportError:
        print("❌ Enhanced strategy not found. Check strategies/")

def run_dark_mode_visual():
    """Run dark mode visualization"""
    try:
        from enhanced_dark_visual import run_enhanced_dark_visualization
        run_enhanced_dark_visualization()
    except ImportError:
        print("❌ Dark mode visualization not found. Check visualization/")

def run_dashboard():
    """Launch interactive dashboard"""
    try:
        from dashboard_app import main as run_dashboard
        run_dashboard()
    except ImportError:
        print("❌ Dashboard not found. Check visualization/")

def run_quick_demo():
    """Run quick visual demo"""
    try:
        from working_visual_demo import run_working_demo
        run_working_demo()
    except ImportError:
        print("❌ Demo not found. Check tests/")

def show_system_status():
    """Show organized file structure"""
    print("\n📁 ORGANIZED FILE STRUCTURE")
    print("=" * 35)
    
    base_path = Path(__file__).parent
    folders = ['core', 'strategies', 'visualization', 'outputs', 'docs', 'tests']
    
    for folder in folders:
        folder_path = base_path / folder
        if folder_path.exists():
            files = list(folder_path.glob('*.py'))
            if folder == 'outputs':
                files = list(folder_path.glob('*.html'))
            elif folder == 'docs':
                files = list(folder_path.glob('*.md'))
            
            print(f"\n📂 {folder.upper()}/")
            for file in sorted(files):
                print(f"   📄 {file.name}")
        else:
            print(f"\n📂 {folder.upper()}/ (empty)")

def show_file_organization():
    """Display file organization information"""
    print("\n🗂️  FILE ORGANIZATION")
    print("=" * 30)
    print("📂 core/           - Data fetcher, risk manager, backtest engine")
    print("📂 strategies/     - Main BTCUSDT enhanced strategy")  
    print("📂 visualization/  - All visual backtesting and charts")
    print("📂 outputs/        - Generated HTML charts and results")
    print("📂 docs/          - Documentation and guides")
    print("📂 tests/         - Demo files and test scripts")
    print("📄 main.py        - This organized entry point")

def main():
    """Main application loop"""
    print("🎯 BTCUSDT Enhanced Trading System - Organized & Ready!")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n👉 Select option (0-6): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye! Happy trading!")
                break
            elif choice == "1":
                run_enhanced_backtest()
            elif choice == "2":
                run_dark_mode_visual()
            elif choice == "3":
                run_dashboard()
            elif choice == "4":
                run_quick_demo()
            elif choice == "5":
                show_system_status()
            elif choice == "6":
                show_file_organization()
            else:
                print("❌ Invalid choice. Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()