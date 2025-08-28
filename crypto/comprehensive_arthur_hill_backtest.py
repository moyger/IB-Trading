#!/usr/bin/env python3
"""
Comprehensive Arthur Hill Trend Strategy Backtest
Multi-period, multi-profile analysis with detailed performance metrics
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), 'strategies'))

from arthur_hill_trend_strategy import ArthurHillTrendStrategy
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveArthurHillBacktest:
    """
    Comprehensive backtesting framework for Arthur Hill Trend Strategy
    Tests across multiple periods, risk profiles, and market conditions
    """
    
    def __init__(self):
        self.results = {}
        self.summary_stats = {}
        
    def run_comprehensive_backtest(self):
        """Run comprehensive multi-dimensional backtest"""
        print("🚀 COMPREHENSIVE ARTHUR HILL TREND STRATEGY BACKTEST")
        print("=" * 65)
        print("📊 Testing across multiple periods and risk profiles")
        print("🎯 Analyzing performance in different market conditions")
        
        # Define test periods with different market characteristics (Aug 2023 - July 2025)
        test_periods = [
            {
                'name': 'Early Bull Phase',
                'start': '2023-08-01',
                'end': '2024-01-01',
                'description': 'Initial recovery and momentum building'
            },
            {
                'name': 'Peak Bull Market',
                'start': '2024-01-01',
                'end': '2024-06-01',
                'description': 'Strong uptrend and ATH approaches'
            },
            {
                'name': 'Summer Consolidation',
                'start': '2024-06-01',
                'end': '2024-11-01',
                'description': 'Volatile sideways movement'
            },
            {
                'name': 'Market Maturation',
                'start': '2024-11-01',
                'end': '2025-04-01',
                'description': 'Trend development phase'
            },
            {
                'name': 'Recent Period',
                'start': '2025-04-01',
                'end': '2025-07-31',
                'description': 'Latest market behavior'
            },
            {
                'name': 'Full 24-Month Cycle',
                'start': '2023-08-01',
                'end': '2025-07-31',
                'description': 'Complete 24-month test period as per CLAUDE.md'
            }
        ]
        
        # Risk profiles to test
        risk_profiles = ['conservative', 'moderate', 'aggressive']
        
        # Run backtests for each combination
        for period in test_periods:
            print(f"\n{'='*20} {period['name'].upper()} {'='*20}")
            print(f"📅 Period: {period['start']} to {period['end']}")
            print(f"📋 Description: {period['description']}")
            
            period_results = {}
            
            for profile in risk_profiles:
                print(f"\n🎯 Testing {profile.upper()} profile...")
                
                try:
                    # Initialize strategy
                    strategy = ArthurHillTrendStrategy(
                        account_size=10000,
                        risk_profile=profile
                    )
                    
                    # Run backtest
                    result_df = strategy.run_backtest(period['start'], period['end'])
                    
                    if result_df is not None:
                        # Collect results
                        period_results[profile] = self._extract_strategy_metrics(strategy, period)
                        print(f"✅ {profile.title()} completed: "
                              f"{period_results[profile]['total_return']:+.2f}% return, "
                              f"{period_results[profile]['total_trades']} trades")
                    else:
                        print(f"❌ {profile.title()} failed")
                        
                except Exception as e:
                    print(f"❌ {profile.title()} error: {e}")
            
            self.results[period['name']] = period_results
        
        # Generate comprehensive analysis
        self._analyze_results()
        self._print_comprehensive_report()
        
        return self.results
    
    def _extract_strategy_metrics(self, strategy, period_info):
        """Extract comprehensive metrics from strategy"""
        
        # Basic performance metrics
        metrics = {
            'period_name': period_info['name'],
            'period_start': period_info['start'],
            'period_end': period_info['end'],
            'initial_balance': strategy.initial_balance,
            'final_balance': strategy.current_balance,
            'total_return': getattr(strategy, 'total_return', 0),
            'total_trades': getattr(strategy, 'total_trades', 0),
            'win_rate': getattr(strategy, 'win_rate', 0),
            'max_drawdown': getattr(strategy, 'max_drawdown', 0),
            'profit_factor': getattr(strategy, 'profit_factor', 0),
            'avg_win': getattr(strategy, 'avg_win', 0),
            'avg_loss': getattr(strategy, 'avg_loss', 0),
            'largest_win': getattr(strategy, 'largest_win', 0),
            'largest_loss': getattr(strategy, 'largest_loss', 0),
            'consecutive_wins': strategy.consecutive_wins,
            'consecutive_losses': strategy.consecutive_losses
        }
        
        # Strategy-specific metrics
        if hasattr(strategy, 'trades') and strategy.trades:
            trades = [t for t in strategy.trades if 'pnl' in t]
            
            if trades:
                # Trade duration analysis
                durations = [t.get('bars_held', 0) for t in trades]
                metrics['avg_trade_duration'] = np.mean(durations) if durations else 0
                metrics['max_trade_duration'] = max(durations) if durations else 0
                
                # Entry strength analysis
                entry_strengths = [abs(t.get('trend_composite', 0)) for t in trades]
                metrics['avg_entry_strength'] = np.mean(entry_strengths) if entry_strengths else 0
                
                # Exit reason analysis
                exit_reasons = {}
                for trade in trades:
                    reason = trade.get('exit_reason', 'Unknown')
                    exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
                
                metrics['exit_reasons'] = exit_reasons
                
                # ATR stop effectiveness
                atr_stops = exit_reasons.get('ATR_Stop', 0)
                trend_reversals = exit_reasons.get('Trend_Reversal', 0)
                
                metrics['atr_stop_rate'] = (atr_stops / len(trades) * 100) if trades else 0
                metrics['trend_reversal_rate'] = (trend_reversals / len(trades) * 100) if trades else 0
                
                # Return distribution
                returns = [t.get('return_pct', 0) for t in trades]
                if returns:
                    metrics['return_std'] = np.std(returns)
                    metrics['return_skew'] = pd.Series(returns).skew()
                    metrics['positive_returns'] = len([r for r in returns if r > 0])
                    metrics['negative_returns'] = len([r for r in returns if r <= 0])
        
        # Risk-adjusted metrics
        if metrics['total_return'] != 0 and metrics['max_drawdown'] != 0:
            metrics['calmar_ratio'] = abs(metrics['total_return'] / metrics['max_drawdown'])
        else:
            metrics['calmar_ratio'] = 0
        
        # Trade frequency (trades per month)
        try:
            start_date = datetime.strptime(period_info['start'], '%Y-%m-%d')
            end_date = datetime.strptime(period_info['end'], '%Y-%m-%d')
            months = (end_date - start_date).days / 30.44
            metrics['trades_per_month'] = metrics['total_trades'] / months if months > 0 else 0
        except:
            metrics['trades_per_month'] = 0
        
        return metrics
    
    def _analyze_results(self):
        """Analyze results across all periods and profiles"""
        print(f"\n🔬 ANALYZING COMPREHENSIVE RESULTS...")
        
        # Aggregate statistics by profile
        profile_aggregates = {'conservative': [], 'moderate': [], 'aggressive': []}
        
        for period_name, period_results in self.results.items():
            for profile, metrics in period_results.items():
                profile_aggregates[profile].append(metrics)
        
        # Calculate summary statistics
        for profile, results_list in profile_aggregates.items():
            if not results_list:
                continue
                
            summary = {
                'profile': profile,
                'periods_tested': len(results_list),
                'avg_return': np.mean([r['total_return'] for r in results_list]),
                'total_trades': sum([r['total_trades'] for r in results_list]),
                'avg_win_rate': np.mean([r['win_rate'] for r in results_list]),
                'avg_max_drawdown': np.mean([r['max_drawdown'] for r in results_list]),
                'avg_profit_factor': np.mean([r['profit_factor'] for r in results_list if r['profit_factor'] != float('inf')]),
                'consistency': len([r for r in results_list if r['total_return'] > 0]) / len(results_list),
                'best_period': max(results_list, key=lambda x: x['total_return'])['period_name'],
                'worst_period': min(results_list, key=lambda x: x['total_return'])['period_name'],
                'avg_trades_per_month': np.mean([r['trades_per_month'] for r in results_list]),
                'return_volatility': np.std([r['total_return'] for r in results_list])
            }
            
            self.summary_stats[profile] = summary
    
    def _print_comprehensive_report(self):
        """Print detailed comprehensive report"""
        print(f"\n📊 COMPREHENSIVE ARTHUR HILL STRATEGY ANALYSIS")
        print("=" * 70)
        
        # Summary by profile
        print(f"\n🎯 PROFILE PERFORMANCE SUMMARY:")
        print("-" * 70)
        print(f"{'Profile':<12} {'Avg Return':<11} {'Consistency':<12} {'Avg Trades/Mo':<13} {'Avg Drawdown'}")
        print("-" * 70)
        
        for profile, stats in self.summary_stats.items():
            print(f"{profile.title():<12} "
                  f"{stats['avg_return']:>+7.2f}%   "
                  f"{stats['consistency']:>8.1%}     "
                  f"{stats['avg_trades_per_month']:>9.1f}     "
                  f"{stats['avg_max_drawdown']:>8.2f}%")
        
        # Detailed period analysis
        print(f"\n📋 DETAILED PERIOD ANALYSIS:")
        print("=" * 100)
        
        for period_name, period_results in self.results.items():
            print(f"\n🗓️  {period_name.upper()}:")
            if period_results:
                print(f"{'Profile':<12} {'Return':<8} {'Trades':<7} {'Win Rate':<9} {'PF':<6} {'Drawdown':<10} {'ATR Stops'}")
                print("-" * 80)
                
                for profile in ['conservative', 'moderate', 'aggressive']:
                    if profile in period_results:
                        metrics = period_results[profile]
                        atr_rate = metrics.get('atr_stop_rate', 0)
                        
                        print(f"{profile.title():<12} "
                              f"{metrics['total_return']:>+6.1f}% "
                              f"{metrics['total_trades']:>6} "
                              f"{metrics['win_rate']:>7.1f}% "
                              f"{metrics['profit_factor']:>5.1f} "
                              f"{metrics['max_drawdown']:>8.2f}% "
                              f"{atr_rate:>7.1f}%")
            else:
                print("   No results available")
        
        # Strategy-specific insights
        print(f"\n🎯 STRATEGY-SPECIFIC INSIGHTS:")
        print("-" * 50)
        
        # ATR Trailing Stop Analysis
        all_atr_rates = []
        all_trend_rates = []
        
        for period_results in self.results.values():
            for metrics in period_results.values():
                if 'atr_stop_rate' in metrics:
                    all_atr_rates.append(metrics['atr_stop_rate'])
                if 'trend_reversal_rate' in metrics:
                    all_trend_rates.append(metrics['trend_reversal_rate'])
        
        if all_atr_rates:
            print(f"🛡️  ATR Trailing Stop Effectiveness:")
            print(f"   Average ATR stop rate: {np.mean(all_atr_rates):.1f}%")
            print(f"   Average trend reversal rate: {np.mean(all_trend_rates):.1f}%")
        
        # Best performing configurations
        print(f"\n🏆 BEST PERFORMING CONFIGURATIONS:")
        
        best_overall = None
        best_return = -float('inf')
        
        for period_name, period_results in self.results.items():
            for profile, metrics in period_results.items():
                if metrics['total_return'] > best_return:
                    best_return = metrics['total_return']
                    best_overall = (period_name, profile, metrics)
        
        if best_overall:
            period, profile, metrics = best_overall
            print(f"   Best Performance: {profile.title()} in {period}")
            print(f"   Return: {metrics['total_return']:+.2f}%")
            print(f"   Trades: {metrics['total_trades']}")
            print(f"   Win Rate: {metrics['win_rate']:.1f}%")
            print(f"   Max Drawdown: {metrics['max_drawdown']:.2f}%")
        
        # Risk-adjusted performance
        print(f"\n📊 RISK-ADJUSTED ANALYSIS:")
        
        for profile, stats in self.summary_stats.items():
            risk_adjusted_return = stats['avg_return'] / max(stats['avg_max_drawdown'], 0.01)
            consistency_score = stats['consistency'] * 100
            
            print(f"   {profile.title()}:")
            print(f"   - Risk-Adjusted Return: {risk_adjusted_return:.1f}")
            print(f"   - Consistency Score: {consistency_score:.0f}%")
            print(f"   - Return Volatility: {stats['return_volatility']:.2f}%")
        
        # Market condition analysis
        print(f"\n🌊 MARKET CONDITION PERFORMANCE:")
        
        market_performance = {}
        for period_name, period_results in self.results.items():
            avg_return = np.mean([m['total_return'] for m in period_results.values()]) if period_results else 0
            market_performance[period_name] = avg_return
        
        best_market = max(market_performance, key=market_performance.get)
        worst_market = min(market_performance, key=market_performance.get)
        
        print(f"   Best Market Condition: {best_market} ({market_performance[best_market]:+.2f}% avg)")
        print(f"   Worst Market Condition: {worst_market} ({market_performance[worst_market]:+.2f}% avg)")
        
        # Final recommendations
        print(f"\n💡 STRATEGY RECOMMENDATIONS:")
        print("-" * 40)
        
        # Find most consistent profile
        most_consistent = max(self.summary_stats.keys(), key=lambda p: self.summary_stats[p]['consistency'])
        highest_return = max(self.summary_stats.keys(), key=lambda p: self.summary_stats[p]['avg_return'])
        lowest_drawdown = min(self.summary_stats.keys(), key=lambda p: self.summary_stats[p]['avg_max_drawdown'])
        
        print(f"✅ Most Consistent: {most_consistent.title()} ({self.summary_stats[most_consistent]['consistency']:.1%} win periods)")
        print(f"📈 Highest Returns: {highest_return.title()} ({self.summary_stats[highest_return]['avg_return']:+.2f}% avg)")
        print(f"🛡️ Lowest Risk: {lowest_drawdown.title()} ({self.summary_stats[lowest_drawdown]['avg_max_drawdown']:.2f}% avg drawdown)")
        
        # Overall assessment
        overall_trades = sum([stats['total_trades'] for stats in self.summary_stats.values()])
        overall_avg_return = np.mean([stats['avg_return'] for stats in self.summary_stats.values()])
        
        print(f"\n🎉 OVERALL ASSESSMENT:")
        print(f"   Total Trades Analyzed: {overall_trades}")
        print(f"   Average Return Across All Tests: {overall_avg_return:+.2f}%")
        print(f"   Strategy Type: Conservative trend-following with ATR stops")
        print(f"   Best Use Case: Risk-controlled systematic trading")

def main():
    """Run comprehensive Arthur Hill backtest"""
    print("🚀 Starting Comprehensive Arthur Hill Trend Strategy Backtest...")
    
    # Initialize comprehensive backtest
    comprehensive_backtest = ComprehensiveArthurHillBacktest()
    
    # Run comprehensive analysis
    results = comprehensive_backtest.run_comprehensive_backtest()
    
    print(f"\n🎉 COMPREHENSIVE BACKTEST COMPLETE!")
    print("📊 All results analyzed across multiple periods and risk profiles")
    print("💾 Results stored for further analysis")
    
    return results

if __name__ == "__main__":
    main()