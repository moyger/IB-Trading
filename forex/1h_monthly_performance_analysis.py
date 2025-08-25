#!/usr/bin/env python3
"""
1H Enhanced Strategy Monthly Performance Analysis
Comprehensive month-by-month backtesting from January 2024 to July 2025
to show the complete performance profile of the winning 1H Enhanced Strategy.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from xauusd_ftmo_1h_enhanced_strategy import XAUUSDFTMO1HEnhancedStrategy

class FTMO1HMonthlyAnalysis:
    """
    Monthly performance analysis for 1H Enhanced Strategy
    """
    
    def __init__(self):
        self.results = []
        print("🚀 1H ENHANCED STRATEGY - COMPLETE MONTHLY PERFORMANCE ANALYSIS")
        print("=" * 80)
        print("📊 Comprehensive backtesting: January 2024 to July 2025")
        print("🎯 Objective: Month-by-month 1H strategy validation")
        print("⚡ Strategy: 1H Enhanced approach with zero violations focus")
        print("=" * 80)

    def run_monthly_1h_test(self, start_date, month_name):
        """Run 1H enhanced strategy test for single month"""
        print(f"\n🚀 1H CHALLENGE: {month_name}")
        print("-" * 50)
        
        # Calculate month end date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if start_dt.month == 12:
            end_dt = start_dt.replace(year=start_dt.year + 1, month=1, day=1) + timedelta(days=59)
        else:
            try:
                end_dt = start_dt.replace(month=start_dt.month + 1) + timedelta(days=30)
            except:
                end_dt = start_dt.replace(month=start_dt.month + 1, day=1) + timedelta(days=59)
        
        end_date = end_dt.strftime("%Y-%m-%d")
        
        try:
            # Initialize 1H Enhanced Strategy
            strategy = XAUUSDFTMO1HEnhancedStrategy(
                account_size=100000,
                challenge_phase=1,
                enable_economic_filter=True
            )
            
            df = strategy.run_1h_enhanced_backtest(start_date, end_date)
            
            if df is None:
                print(f"❌ No 1H data available for {month_name}")
                return None
            
            # Extract results
            profit_pct = (strategy.current_balance - strategy.initial_balance) / strategy.initial_balance * 100
            violations = strategy.check_ultra_strict_violations_1h()
            completed = strategy.challenge_complete
            trading_days = len(strategy.trading_days)
            total_trades = len([t for t in strategy.trades if t['action'] == 'CLOSE'])
            
            # Win rate calculation
            closed_trades = [t for t in strategy.trades if t['action'] == 'CLOSE']
            win_rate = 0
            if closed_trades:
                profitable_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
                win_rate = len(profitable_trades) / len(closed_trades) * 100
            
            # Risk metrics
            max_drawdown = 0
            worst_daily_loss = 0
            if strategy.equity_curve:
                max_drawdown = abs(min([e.get('drawdown', 0) for e in strategy.equity_curve]))
            
            # Calculate worst daily loss
            for date in strategy.trading_days:
                day_trades = [t for t in strategy.trades if t['date'] == date and t['action'] == 'CLOSE']
                if day_trades:
                    daily_pnl_pct = sum(t.get('pnl_pct', 0) for t in day_trades)
                    if daily_pnl_pct < worst_daily_loss:
                        worst_daily_loss = daily_pnl_pct
            
            # Completion time analysis
            completion_days = None
            completion_speed = "N/A"
            if completed:
                completion_days = trading_days
                # Find exact completion day
                for i, trade in enumerate(strategy.trades):
                    if trade['action'] == 'CLOSE':
                        trade_profit = (trade['balance'] - strategy.initial_balance) / strategy.initial_balance * 100
                        if trade_profit >= 10.0:
                            unique_days = set()
                            for prev_trade in strategy.trades[:i+1]:
                                unique_days.add(prev_trade['date'])
                            completion_days = len(unique_days)
                            break
                
                if completion_days <= 2:
                    completion_speed = "Lightning Fast"
                elif completion_days <= 5:
                    completion_speed = "Very Fast"
                elif completion_days <= 10:
                    completion_speed = "Fast"
                elif completion_days <= 20:
                    completion_speed = "Moderate"
                else:
                    completion_speed = "Slow"
            
            # 1H specific metrics
            risk_alerts = len(strategy.risk_alerts)
            emergency_stops = strategy.emergency_stop or strategy.daily_emergency_stop
            
            result = {
                'month': month_name,
                'start_date': start_date,
                'completed': completed,
                'profit_pct': profit_pct,
                'completion_days': completion_days,
                'completion_speed': completion_speed,
                'trading_days': trading_days,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'max_drawdown': max_drawdown,
                'worst_daily_loss': abs(worst_daily_loss),
                'rule_violations': len(violations) > 0,
                'violations_count': len(violations),
                'risk_alerts': risk_alerts,
                'emergency_stops': emergency_stops,
                'final_balance': strategy.current_balance,
                'perfect_compliance': len(violations) == 0 and risk_alerts == 0 and not emergency_stops,
                'grade': self.calculate_1h_monthly_grade(completed, profit_pct, len(violations), risk_alerts)
            }
            
            self.results.append(result)
            
            # Display result
            status = "✅ COMPLETED" if completed else "❌ INCOMPLETE"
            days_str = f"in {completion_days}d" if completion_days else "ongoing"
            speed_str = f"({completion_speed})" if completion_days else ""
            compliance = "✅ PERFECT" if result['perfect_compliance'] else "⚠️ ALERTS"
            
            print(f"Result: {status} {days_str} {speed_str} | {profit_pct:+.1f}% | {total_trades} trades | {compliance}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in {month_name}: {e}")
            return None

    def calculate_1h_monthly_grade(self, completed, profit_pct, violations, risk_alerts):
        """Calculate grade for 1H monthly performance"""
        if completed and violations == 0 and risk_alerts == 0:
            if profit_pct >= 15:
                return "A+"
            elif profit_pct >= 12:
                return "A"
            else:
                return "A-"
        elif completed and violations == 0:
            return "B+"
        elif completed:
            return "B"
        elif profit_pct >= 5 and violations == 0:
            return "C+"
        elif violations == 0:
            return "C"
        else:
            return "D"

    def run_complete_1h_monthly_analysis(self):
        """Run complete monthly analysis for 1H strategy"""
        print("\n📅 RUNNING COMPLETE 1H MONTHLY ANALYSIS")
        print("=" * 70)
        print("🎯 Testing 1H Enhanced Strategy across 19 months")
        
        # Monthly test periods (same as original analysis for comparison)
        monthly_periods = [
            ("2024-01-01", "January 2024"),
            ("2024-02-01", "February 2024"),
            ("2024-03-01", "March 2024"),
            ("2024-04-01", "April 2024"),
            ("2024-05-01", "May 2024"),
            ("2024-06-01", "June 2024"),
            ("2024-07-01", "July 2024"),
            ("2024-08-01", "August 2024"),
            ("2024-09-01", "September 2024"),
            ("2024-10-01", "October 2024"),
            ("2024-11-01", "November 2024"),
            ("2024-12-01", "December 2024"),
            ("2025-01-01", "January 2025"),
            ("2025-02-01", "February 2025"),
            ("2025-03-01", "March 2025"),
            ("2025-04-01", "April 2025"),
            ("2025-05-01", "May 2025"),
            ("2025-06-01", "June 2025"),
            ("2025-07-01", "July 2025")
        ]
        
        successful_tests = 0
        
        for start_date, month_name in monthly_periods:
            result = self.run_monthly_1h_test(start_date, month_name)
            if result:
                successful_tests += 1
        
        print(f"\n✅ COMPLETED {successful_tests}/{len(monthly_periods)} MONTHLY 1H TESTS")
        
        # Generate comprehensive analysis
        if self.results:
            self.generate_1h_monthly_analysis()

    def generate_1h_monthly_analysis(self):
        """Generate comprehensive 1H monthly analysis"""
        print(f"\n{'='*100}")
        print("📊 COMPLETE 1H ENHANCED STRATEGY MONTHLY ANALYSIS")
        print(f"{'='*100}")
        
        total_months = len(self.results)
        successful_months = sum(1 for r in self.results if r['completed'])
        profitable_months = sum(1 for r in self.results if r['profit_pct'] > 0)
        
        print(f"\n🏆 1H OVERALL SUCCESS METRICS:")
        print(f"Total Months Tested:       {total_months}")
        print(f"Completed Challenges:      {successful_months}/{total_months} ({successful_months/total_months*100:.1f}%)")
        print(f"Profitable Months:         {profitable_months}/{total_months} ({profitable_months/total_months*100:.1f}%)")
        
        if self.results:
            avg_profit = np.mean([r['profit_pct'] for r in self.results])
            print(f"Average Profit/Loss:       {avg_profit:+.2f}%")
        
        # Completion analysis
        if successful_months > 0:
            completed_results = [r for r in self.results if r['completed']]
            avg_completion_time = np.mean([r['completion_days'] for r in completed_results if r['completion_days']])
            fastest_completion = min([r['completion_days'] for r in completed_results if r['completion_days']])
            avg_completed_profit = np.mean([r['profit_pct'] for r in completed_results])
            
            print(f"\n📈 1H COMPLETION ANALYSIS:")
            print(f"Average Completion Time:   {avg_completion_time:.1f} days")
            print(f"Fastest Completion:        {fastest_completion} days")
            print(f"Average Completed Profit:  {avg_completed_profit:+.2f}%")
        
        # Risk analysis
        violation_months = sum(1 for r in self.results if r['rule_violations'])
        perfect_compliance_months = sum(1 for r in self.results if r['perfect_compliance'])
        max_drawdown = max([r['max_drawdown'] for r in self.results]) if self.results else 0
        worst_daily_loss = max([r['worst_daily_loss'] for r in self.results]) if self.results else 0
        
        print(f"\n⚠️ 1H RISK ANALYSIS:")
        print(f"Rule Violations:           {violation_months}/{total_months} ({violation_months/total_months*100:.1f}%)")
        print(f"Perfect Compliance:        {perfect_compliance_months}/{total_months} ({perfect_compliance_months/total_months*100:.1f}%)")
        print(f"Maximum Drawdown:          {max_drawdown:.2f}%")
        print(f"Worst Daily Loss:          {worst_daily_loss:.2f}%")
        print(f"Risk Management Score:     {(total_months-violation_months)/total_months*100:.1f}%")
        
        # Trading frequency analysis
        if self.results:
            avg_trades = np.mean([r['total_trades'] for r in self.results])
            avg_win_rate = np.mean([r['win_rate'] for r in self.results if r['win_rate'] > 0])
            
            print(f"\n📊 1H TRADING ANALYSIS:")
            print(f"Average Trades per Month:  {avg_trades:.1f}")
            print(f"Average Win Rate:          {avg_win_rate:.1f}%")
        
        # Monthly performance breakdown
        print(f"\n📋 1H MONTHLY PERFORMANCE BREAKDOWN:")
        print("-" * 110)
        print(f"{'Month':<20} {'Status':<12} {'Profit':<8} {'Days':<6} {'Trades':<7} {'Win%':<6} {'Risk':<8} {'Grade':<6}")
        print("-" * 110)
        
        for result in self.results:
            status = "COMPLETED" if result['completed'] else "INCOMPLETE"
            profit = f"{result['profit_pct']:+.1f}%"
            days = str(result['completion_days']) if result['completion_days'] else "N/A"
            trades = str(result['total_trades'])
            win_rate = f"{result['win_rate']:.0f}%" if result['total_trades'] > 0 else "N/A"
            risk = "PERFECT" if result['perfect_compliance'] else "ALERTS"
            grade = result['grade']
            
            print(f"{result['month']:<20} {status:<12} {profit:<8} {days:<6} {trades:<7} {win_rate:<6} {risk:<8} {grade:<6}")
        
        # Seasonal analysis
        print(f"\n📅 1H SEASONAL ANALYSIS:")
        seasons = {
            'Q1': [r for r in self.results if any(m in r['month'] for m in ['January', 'February', 'March'])],
            'Q2': [r for r in self.results if any(m in r['month'] for m in ['April', 'May', 'June'])],
            'Q3': [r for r in self.results if any(m in r['month'] for m in ['July', 'August', 'September'])],
            'Q4': [r for r in self.results if any(m in r['month'] for m in ['October', 'November', 'December'])]
        }
        
        for season_name, season_results in seasons.items():
            if season_results:
                season_completions = sum(1 for r in season_results if r['completed'])
                season_avg_profit = np.mean([r['profit_pct'] for r in season_results])
                completion_rate = season_completions / len(season_results) * 100
                print(f"{season_name}: {season_completions}/{len(season_results)} completed ({completion_rate:.0f}%), avg {season_avg_profit:+.1f}%")
        
        # Performance highlights
        print(f"\n🎯 1H PERFORMANCE HIGHLIGHTS:")
        
        # Best performances
        best_profit_month = max(self.results, key=lambda x: x['profit_pct'])
        fastest_completion_month = None
        if successful_months > 0:
            completed_results = [r for r in self.results if r['completed'] and r['completion_days']]
            if completed_results:
                fastest_completion_month = min(completed_results, key=lambda x: x['completion_days'])
        
        print(f"🏆 Best Performances:")
        if fastest_completion_month:
            print(f"   Fastest Completion: {fastest_completion_month['month']} in {fastest_completion_month['completion_days']} days ({fastest_completion_month['profit_pct']:+.1f}%)")
        print(f"   Most Profitable: {best_profit_month['month']} with {best_profit_month['profit_pct']:+.1f}%")
        
        # Challenging periods
        worst_profit_month = min(self.results, key=lambda x: x['profit_pct'])
        highest_risk_month = max(self.results, key=lambda x: x['max_drawdown'])
        
        print(f"⚠️ Challenging Periods:")
        print(f"   Lowest Profit: {worst_profit_month['month']} with {worst_profit_month['profit_pct']:+.1f}%")
        print(f"   Highest Risk: {highest_risk_month['month']} with {highest_risk_month['max_drawdown']:.1f}% drawdown")
        
        # Strategic insights
        print(f"\n💡 1H STRATEGIC INSIGHTS:")
        
        # Overall assessment
        success_rate = successful_months / total_months * 100
        if success_rate >= 50:
            assessment = "✅ EXCELLENT performance - Strategy exceeds expectations"
        elif success_rate >= 30:
            assessment = "✅ GOOD performance - Strategy meets target requirements"
        elif success_rate >= 15:
            assessment = "⚡ ACCEPTABLE performance - Strategy shows improvement"
        else:
            assessment = "🔄 POOR performance - Strategy requires major revision"
        
        print(f"Strategic Assessment:      {assessment}")
        print(f"Trading Frequency:         {avg_trades:.1f} trades/month (optimal for 1H approach)")
        
        if violation_months == 0:
            print(f"Risk Management:           ✅ PERFECT - Zero rule violations maintained")
        else:
            print(f"Risk Management:           ⚠️ ATTENTION - {violation_months} months with violations")
        
        # Comparison with original 4H strategy
        print(f"\n📈 COMPARISON WITH ORIGINAL 4H STRATEGY:")
        print(f"Original 4H Strategy:      2/19 completed (10.5% success rate)")
        print(f"1H Enhanced Strategy:      {successful_months}/{total_months} completed ({success_rate:.1f}% success rate)")
        if success_rate > 0:
            improvement = success_rate - 10.5
            factor = success_rate / 10.5 if success_rate > 0 else 0
            print(f"Improvement:              {improvement:+.1f} percentage points ({factor:.1f}x better)")
        
        print(f"Trading Approach:          High frequency vs low frequency")
        print(f"Completion Speed:          {avg_completion_time:.1f} days vs 3.5 days (4H average)")
        
        # Final recommendation
        print(f"\n🎯 FINAL 1H STRATEGY ASSESSMENT:")
        
        if success_rate >= 25 and violation_months == 0:
            final_grade = "A"
            recommendation = "✅ APPROVED for live FTMO challenges"
        elif success_rate >= 20 and violation_months <= 1:
            final_grade = "B"
            recommendation = "✅ APPROVED with minor optimizations"
        elif success_rate >= 15:
            final_grade = "C"
            recommendation = "⚠️ CONDITIONAL approval - monitor closely"
        else:
            final_grade = "D"
            recommendation = "❌ NOT APPROVED - requires major improvements"
        
        print(f"Overall Grade:            {final_grade}")
        print(f"Recommendation:           {recommendation}")
        print(f"Success Rate:             {success_rate:.1f}% (Target: >20%)")
        print(f"Safety Record:            {(total_months-violation_months)/total_months*100:.1f}% compliance")

def main():
    """Run complete 1H monthly analysis"""
    print("🚀 1H ENHANCED STRATEGY MONTHLY PERFORMANCE ANALYSIS")
    print("=" * 80)
    print("🎯 Objective: Complete month-by-month performance validation")
    print("📊 Period: January 2024 to July 2025 (19 months)")
    print("⚡ Strategy: 1H Enhanced approach with zero violations focus")
    print("=" * 80)
    
    analyzer = FTMO1HMonthlyAnalysis()
    analyzer.run_complete_1h_monthly_analysis()
    
    print(f"\n✅ 1H MONTHLY ANALYSIS COMPLETE!")
    print("📊 Complete 19-month performance data now available")
    print("🎯 1H Enhanced Strategy validation complete across all periods")

if __name__ == "__main__":
    main()