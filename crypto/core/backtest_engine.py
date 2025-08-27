#!/usr/bin/env python3
"""
Comprehensive Backtesting Engine for BTCUSDT Enhanced Strategy
Integrates with the backtesting.py library for professional-grade analysis

Features:
- Integration with backtesting.py framework
- Custom performance metrics
- Risk-adjusted returns analysis
- Monte Carlo simulation
- Walk-forward analysis
- Comprehensive reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from data_fetcher import BTCDataFetcher
from btcusdt_enhanced_strategy import BTCUSDTEnhancedStrategy
from risk_manager import CryptoRiskManager

# Try to import backtesting library
try:
    from backtesting import Backtest, Strategy as BacktestStrategy
    from backtesting.lib import crossover
    BACKTESTING_AVAILABLE = True
except ImportError:
    BACKTESTING_AVAILABLE = False
    print("⚠️ backtesting library not available. Using custom backtest engine.")

class PerformanceAnalyzer:
    """Advanced performance analysis for crypto strategies"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_metrics(self, trades: List[Dict], equity_curve: List[float], 
                         initial_balance: float) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not trades:
            return {}
        
        closed_trades = [t for t in trades if t['action'] == 'CLOSE']
        if not closed_trades:
            return {}
        
        # Basic metrics
        total_return = (equity_curve[-1] - initial_balance) / initial_balance
        
        # Trade-level analysis
        profitable_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] <= 0]
        
        win_rate = len(profitable_trades) / len(closed_trades) if closed_trades else 0
        
        # Risk metrics
        returns = pd.Series(equity_curve).pct_change().dropna()
        volatility = returns.std() * np.sqrt(365 * 24)  # Annualized for hourly data
        
        # Sharpe ratio
        excess_returns = returns.mean() * 365 * 24 - self.risk_free_rate
        sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(365 * 24)
        sortino_ratio = excess_returns / downside_volatility if downside_volatility > 0 else 0
        
        # Maximum drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        max_drawdown = np.max(drawdown)
        
        # Calmar ratio
        cagr = (equity_curve[-1] / initial_balance) ** (1/1) - 1  # Assume 1 year
        calmar_ratio = cagr / max_drawdown if max_drawdown > 0 else 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in profitable_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        avg_win = gross_profit / len(profitable_trades) if profitable_trades else 0
        avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Recovery factor
        recovery_factor = total_return / max_drawdown if max_drawdown > 0 else 0
        
        # Consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for trade in closed_trades:
            if trade['pnl'] > 0:
                current_win_streak += 1
                current_loss_streak = 0
                max_consecutive_wins = max(max_consecutive_wins, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                max_consecutive_losses = max(max_consecutive_losses, current_loss_streak)
        
        return {
            'total_return': total_return,
            'cagr': cagr,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'recovery_factor': recovery_factor,
            'win_rate': win_rate,
            'total_trades': len(closed_trades),
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_win': max(t['pnl'] for t in profitable_trades) if profitable_trades else 0,
            'max_loss': min(t['pnl'] for t in losing_trades) if losing_trades else 0,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss
        }

class BTCBacktestEngine:
    """Comprehensive backtesting engine for BTCUSDT strategy"""
    
    def __init__(self, account_size: float = 10000, risk_profile: str = 'moderate'):
        """
        Initialize backtest engine
        
        Args:
            account_size: Initial trading capital
            risk_profile: Risk profile for the strategy
        """
        self.account_size = account_size
        self.risk_profile = risk_profile
        self.analyzer = PerformanceAnalyzer()
        
        # Initialize components
        self.data_fetcher = BTCDataFetcher()
        self.strategy = BTCUSDTEnhancedStrategy(account_size, risk_profile)
        self.risk_manager = CryptoRiskManager(account_size, risk_profile)
        
        print(f"🚀 BTC BACKTEST ENGINE INITIALIZED")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"⚙️ Risk Profile: {risk_profile.upper()}")
    
    def run_single_backtest(self, start_date: str, end_date: str, 
                           symbol: str = 'BTC-USD') -> Dict:
        """
        Run single backtest on specified period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            symbol: Trading symbol
            
        Returns:
            Backtest results dictionary
        """
        print(f"\n🎯 SINGLE BACKTEST: {start_date} to {end_date}")
        print("=" * 60)
        
        # Run strategy backtest
        df = self.strategy.run_backtest(start_date, end_date)
        
        if df is None:
            print("❌ Backtest failed - no data")
            return {}
        
        # Calculate performance metrics
        equity_curve = [self.account_size]  # Build equity curve from trades
        current_balance = self.account_size
        
        for trade in self.strategy.trades:
            if trade['action'] == 'CLOSE':
                current_balance += trade['pnl']
                equity_curve.append(current_balance)
        
        metrics = self.analyzer.calculate_metrics(
            self.strategy.trades, equity_curve, self.account_size
        )
        
        # Compile results
        results = {
            'period': f"{start_date} to {end_date}",
            'total_bars': len(df),
            'initial_balance': self.account_size,
            'final_balance': self.strategy.current_balance,
            'trades': self.strategy.trades,
            'equity_curve': equity_curve,
            'metrics': metrics,
            'strategy_stats': {
                'trading_days': len(self.strategy.trading_days),
                'challenge_complete': self.strategy.challenge_complete,
                'confluence_scores': getattr(self.strategy, 'confluence_scores', []),
                'trades_filtered': getattr(self.strategy, 'trades_skipped_filters', {}),
                'risk_alerts': len(self.strategy.risk_alerts)
            }
        }
        
        return results
    
    def run_monthly_analysis(self, start_year: int = 2023, end_year: int = 2024) -> Dict:
        """
        Run month-by-month analysis over multiple years
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            Monthly analysis results
        """
        print(f"\n📅 MONTHLY ANALYSIS: {start_year} to {end_year}")
        print("=" * 60)
        
        monthly_results = []
        successful_months = 0
        total_months = 0
        
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                # Skip future months
                current_date = datetime.now()
                if datetime(year, month, 1) > current_date:
                    break
                
                # Calculate month boundaries
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                print(f"\n📊 Testing {start_date.strftime('%B %Y')}...")
                
                # Reset strategy for each month
                self.strategy = BTCUSDTEnhancedStrategy(self.account_size, self.risk_profile)
                
                # Run backtest for this month
                results = self.run_single_backtest(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                if results and 'metrics' in results:
                    total_months += 1
                    profit_pct = (results['final_balance'] - self.account_size) / self.account_size * 100
                    
                    # Check if target was reached
                    target_reached = results['strategy_stats']['challenge_complete']
                    if target_reached:
                        successful_months += 1
                    
                    monthly_result = {
                        'year': year,
                        'month': month,
                        'month_name': start_date.strftime('%B %Y'),
                        'profit_pct': profit_pct,
                        'target_reached': target_reached,
                        'trading_days': results['strategy_stats']['trading_days'],
                        'total_trades': results['metrics']['total_trades'],
                        'win_rate': results['metrics']['win_rate'],
                        'max_drawdown': results['metrics']['max_drawdown'],
                        'sharpe_ratio': results['metrics']['sharpe_ratio']
                    }
                    
                    monthly_results.append(monthly_result)
                    
                    status = "✅ TARGET" if target_reached else f"📊 {profit_pct:+.1f}%"
                    print(f"Result: {status}")
        
        # Calculate summary statistics
        success_rate = successful_months / total_months if total_months > 0 else 0
        avg_profit = np.mean([r['profit_pct'] for r in monthly_results]) if monthly_results else 0
        
        summary = {
            'total_months_tested': total_months,
            'successful_months': successful_months,
            'success_rate': success_rate,
            'average_profit_pct': avg_profit,
            'monthly_results': monthly_results
        }
        
        return summary
    
    def run_walk_forward_analysis(self, start_date: str, end_date: str, 
                                 window_months: int = 3, step_months: int = 1) -> Dict:
        """
        Run walk-forward analysis to test strategy robustness
        
        Args:
            start_date: Overall start date
            end_date: Overall end date
            window_months: Analysis window in months
            step_months: Step size in months
            
        Returns:
            Walk-forward analysis results
        """
        print(f"\n🚶 WALK-FORWARD ANALYSIS")
        print(f"Window: {window_months} months, Step: {step_months} month(s)")
        print("=" * 60)
        
        results = []
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current_start = start
        
        while current_start < end:
            # Calculate window end
            window_end = current_start + timedelta(days=window_months * 30)
            if window_end > end:
                window_end = end
            
            print(f"\n📊 Window: {current_start.strftime('%Y-%m-%d')} to {window_end.strftime('%Y-%m-%d')}")
            
            # Reset strategy
            self.strategy = BTCUSDTEnhancedStrategy(self.account_size, self.risk_profile)
            
            # Run backtest
            window_results = self.run_single_backtest(
                current_start.strftime('%Y-%m-%d'),
                window_end.strftime('%Y-%m-%d')
            )
            
            if window_results and 'metrics' in window_results:
                profit_pct = (window_results['final_balance'] - self.account_size) / self.account_size * 100
                
                result = {
                    'start_date': current_start.strftime('%Y-%m-%d'),
                    'end_date': window_end.strftime('%Y-%m-%d'),
                    'profit_pct': profit_pct,
                    'sharpe_ratio': window_results['metrics']['sharpe_ratio'],
                    'max_drawdown': window_results['metrics']['max_drawdown'],
                    'win_rate': window_results['metrics']['win_rate'],
                    'total_trades': window_results['metrics']['total_trades']
                }
                
                results.append(result)
                print(f"Result: {profit_pct:+.1f}% | Sharpe: {result['sharpe_ratio']:.2f}")
            
            # Move to next window
            current_start = current_start + timedelta(days=step_months * 30)
        
        # Calculate stability metrics
        if results:
            profits = [r['profit_pct'] for r in results]
            sharpes = [r['sharpe_ratio'] for r in results if r['sharpe_ratio'] != 0]
            
            summary = {
                'total_windows': len(results),
                'profitable_windows': len([r for r in results if r['profit_pct'] > 0]),
                'avg_profit_pct': np.mean(profits),
                'profit_std': np.std(profits),
                'avg_sharpe': np.mean(sharpes) if sharpes else 0,
                'consistency_score': len([r for r in results if r['profit_pct'] > 0]) / len(results),
                'results': results
            }
        else:
            summary = {'error': 'No valid results'}
        
        return summary
    
    def print_backtest_results(self, results: Dict):
        """Print formatted backtest results"""
        if not results or 'metrics' not in results:
            print("❌ No results to display")
            return
        
        print(f"\n🏆 BACKTEST RESULTS - {results['period']}")
        print("=" * 80)
        
        print(f"Initial Balance:        ${results['initial_balance']:,.2f}")
        print(f"Final Balance:          ${results['final_balance']:,.2f}")
        
        profit_pct = (results['final_balance'] - results['initial_balance']) / results['initial_balance'] * 100
        print(f"Profit/Loss:            {profit_pct:+.2f}%")
        
        metrics = results['metrics']
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"Total Return:           {metrics['total_return']*100:.2f}%")
        print(f"CAGR:                   {metrics['cagr']*100:.2f}%")
        print(f"Volatility:             {metrics['volatility']*100:.2f}%")
        print(f"Sharpe Ratio:           {metrics['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio:          {metrics['sortino_ratio']:.2f}")
        print(f"Max Drawdown:           {metrics['max_drawdown']*100:.2f}%")
        print(f"Calmar Ratio:           {metrics['calmar_ratio']:.2f}")
        print(f"Recovery Factor:        {metrics['recovery_factor']:.2f}")
        
        print(f"\n📈 TRADE ANALYSIS:")
        print(f"Total Trades:           {metrics['total_trades']}")
        print(f"Win Rate:               {metrics['win_rate']*100:.1f}%")
        print(f"Profit Factor:          {metrics['profit_factor']:.2f}")
        print(f"Expectancy:             ${metrics['expectancy']:.2f}")
        print(f"Average Win:            ${metrics['avg_win']:.2f}")
        print(f"Average Loss:           ${metrics['avg_loss']:.2f}")
        print(f"Max Win:                ${metrics['max_win']:.2f}")
        print(f"Max Loss:               ${metrics['max_loss']:.2f}")
        
        print(f"\n🎯 STRATEGY SPECIFIC:")
        stats = results['strategy_stats']
        print(f"Trading Days:           {stats['trading_days']}")
        print(f"Challenge Complete:     {'✅' if stats['challenge_complete'] else '❌'}")
        print(f"Risk Alerts:            {stats['risk_alerts']}")
        
        if 'confluence_scores' in stats and stats['confluence_scores']:
            avg_confluence = np.mean(stats['confluence_scores'])
            print(f"Avg Confluence Score:   {avg_confluence:.2f}/7")
        
        if 'trades_filtered' in stats:
            filtered = stats['trades_filtered']
            total_filtered = sum(filtered.values())
            print(f"Trades Filtered:        {total_filtered}")
            if total_filtered > 0:
                for filter_type, count in filtered.items():
                    if count > 0:
                        print(f"  - {filter_type.replace('_', ' ').title()}: {count}")
    
    def print_monthly_summary(self, monthly_results: Dict):
        """Print monthly analysis summary"""
        if not monthly_results or 'monthly_results' not in monthly_results:
            print("❌ No monthly results to display")
            return
        
        print(f"\n📅 MONTHLY ANALYSIS SUMMARY")
        print("=" * 80)
        
        print(f"Total Months Tested:    {monthly_results['total_months_tested']}")
        print(f"Successful Months:      {monthly_results['successful_months']}")
        print(f"Success Rate:           {monthly_results['success_rate']*100:.1f}%")
        print(f"Average Profit:         {monthly_results['average_profit_pct']:+.2f}%")
        
        print(f"\n📊 MONTHLY BREAKDOWN:")
        for result in monthly_results['monthly_results']:
            status = "✅" if result['target_reached'] else f"{result['profit_pct']:+.1f}%"
            print(f"{result['month_name']:<15} {status:>10} | Trades: {result['total_trades']:>3} | WR: {result['win_rate']*100:>5.1f}%")


if __name__ == "__main__":
    print("🧪 Testing BTC Backtest Engine")
    print("=" * 50)
    
    # Initialize backtest engine
    engine = BTCBacktestEngine(account_size=10000, risk_profile='moderate')
    
    # Test single backtest
    print("\n📊 Running single backtest...")
    results = engine.run_single_backtest("2024-01-01", "2024-02-01")
    
    if results:
        engine.print_backtest_results(results)
    
    print("\n✅ Backtest engine test completed!")