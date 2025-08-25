#!/usr/bin/env python3
"""
Monthly Performance Analysis for 3-Stock Trend Composite Portfolio
Detailed month-by-month breakdown with performance metrics
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import the existing backtest class
import sys
sys.path.append('.')
from three_stock_trend_composite_backtest import ThreeStockTrendComposite, run_three_stock_backtest

def analyze_monthly_performance():
    """
    Run the backtest and analyze monthly performance
    """
    
    print("📊 MONTHLY PERFORMANCE ANALYSIS")
    print("=" * 80)
    print("🎯 3-Stock Trend Composite Portfolio: AMZN, TSLA, RBLX")
    print("💰 Capital: $5,000 | Period: Jan 2024 - Jul 2025")
    print("=" * 80)
    
    # Run the backtest to get results
    results_df, trades = run_three_stock_backtest()
    
    if results_df is None or results_df.empty:
        print("❌ No backtest results available")
        return
    
    # Convert date index to datetime if needed
    results_df['date'] = pd.to_datetime(results_df['date'])
    results_df.set_index('date', inplace=True)
    
    # Calculate monthly returns
    results_df['portfolio_return'] = results_df['portfolio_value'].pct_change()
    
    # Resample to monthly data (last day of each month)
    monthly_data = results_df.resample('M').agg({
        'portfolio_value': 'last',
        'total_stock_exposure': 'mean',
        'cash': 'last',
        'amzn_score': 'mean',
        'tsla_score': 'mean', 
        'rblx_score': 'mean',
        'amzn_price': 'last',
        'tsla_price': 'last',
        'rblx_price': 'last',
        'amzn_allocation': 'mean',
        'tsla_allocation': 'mean',
        'rblx_allocation': 'mean'
    })
    
    # Calculate monthly returns
    monthly_data['monthly_return'] = monthly_data['portfolio_value'].pct_change()
    monthly_data['cumulative_return'] = (monthly_data['portfolio_value'] / 5000) - 1
    
    # Calculate individual stock monthly returns for comparison
    stock_monthly_returns = {}
    
    for stock in ['AMZN', 'TSLA', 'RBLX']:
        price_col = f'{stock.lower()}_price'
        monthly_data[f'{stock}_monthly_return'] = monthly_data[price_col].pct_change()
        monthly_data[f'{stock}_cumulative_return'] = (monthly_data[price_col] / monthly_data[price_col].iloc[0]) - 1
    
    # Get SPY data for comparison
    try:
        spy = yf.Ticker("SPY")
        spy_df = spy.history(start="2024-01-01", end="2025-07-31")
        spy_monthly = spy_df['Close'].resample('M').last()
        spy_monthly_returns = spy_monthly.pct_change()
        spy_cumulative = (spy_monthly / spy_monthly.iloc[0]) - 1
        
        # Align with our data
        monthly_data['spy_monthly_return'] = spy_monthly_returns
        monthly_data['spy_cumulative_return'] = spy_cumulative
    except:
        monthly_data['spy_monthly_return'] = 0
        monthly_data['spy_cumulative_return'] = 0
    
    print("\n📅 MONTHLY PERFORMANCE BREAKDOWN:")
    print("=" * 120)
    print(f"{'Month':12} {'Portfolio':>10} {'Monthly':>8} {'Cumul':>8} {'Exposure':>8} {'AMZN':>6} {'TSLA':>6} {'RBLX':>6} {'vs SPY':>8}")
    print(f"{'':12} {'Value':>10} {'Return':>8} {'Return':>8} {'%':>8} {'Score':>6} {'Score':>6} {'Score':>6} {'Diff':>8}")
    print("-" * 120)
    
    monthly_summary = []
    
    for i, (date, row) in enumerate(monthly_data.iterrows()):
        month_year = date.strftime('%Y-%m')
        portfolio_value = row['portfolio_value']
        monthly_ret = row['monthly_return'] if not pd.isna(row['monthly_return']) else 0
        cumul_ret = row['cumulative_return']
        exposure = row['total_stock_exposure']
        
        amzn_score = row['amzn_score']
        tsla_score = row['tsla_score']
        rblx_score = row['rblx_score']
        
        spy_monthly_ret = row['spy_monthly_return'] if not pd.isna(row['spy_monthly_return']) else 0
        vs_spy = monthly_ret - spy_monthly_ret
        
        print(f"{month_year:12} ${portfolio_value:9,.0f} {monthly_ret:7.1%} {cumul_ret:7.1%} {exposure:7.1%} "
              f"{amzn_score:5.1f} {tsla_score:5.1f} {rblx_score:5.1f} {vs_spy:+7.1%}")
        
        monthly_summary.append({
            'month': month_year,
            'portfolio_value': portfolio_value,
            'monthly_return': monthly_ret,
            'cumulative_return': cumul_ret,
            'exposure': exposure,
            'amzn_score': amzn_score,
            'tsla_score': tsla_score,
            'rblx_score': rblx_score,
            'vs_spy': vs_spy,
            'spy_monthly_return': spy_monthly_ret
        })
    
    print()
    
    # Calculate performance statistics
    monthly_returns = monthly_data['monthly_return'].dropna()
    
    print("📈 MONTHLY PERFORMANCE STATISTICS:")
    print("-" * 60)
    print(f"Best Month:             {monthly_returns.max():+.1%}")
    print(f"Worst Month:            {monthly_returns.min():+.1%}")
    print(f"Average Monthly Return: {monthly_returns.mean():+.1%}")
    print(f"Monthly Volatility:     {monthly_returns.std():+.1%}")
    print(f"Positive Months:        {(monthly_returns > 0).sum()}/{len(monthly_returns)} ({(monthly_returns > 0).mean():.0%})")
    print(f"Negative Months:        {(monthly_returns < 0).sum()}/{len(monthly_returns)} ({(monthly_returns < 0).mean():.0%})")
    
    # Identify best and worst performing months
    best_month_idx = monthly_returns.idxmax()
    worst_month_idx = monthly_returns.idxmin()
    
    best_month = best_month_idx.strftime('%Y-%m')
    worst_month = worst_month_idx.strftime('%Y-%m')
    
    print(f"\n🏆 Best Month:  {best_month} (+{monthly_returns.max():.1%})")
    print(f"💀 Worst Month: {worst_month} ({monthly_returns.min():.1%})")
    
    # Show individual stock performance comparison
    print(f"\n📊 CUMULATIVE RETURNS BY MONTH:")
    print("=" * 80)
    print(f"{'Month':12} {'Portfolio':>10} {'AMZN':>8} {'TSLA':>8} {'RBLX':>8} {'SPY':>8}")
    print("-" * 80)
    
    for i, (date, row) in enumerate(monthly_data.iterrows()):
        month_year = date.strftime('%Y-%m')
        portfolio_cum = row['cumulative_return']
        amzn_cum = row['AMZN_cumulative_return']
        tsla_cum = row['TSLA_cumulative_return']
        rblx_cum = row['RBLX_cumulative_return']
        spy_cum = row['spy_cumulative_return']
        
        print(f"{month_year:12} {portfolio_cum:9.1%} {amzn_cum:7.1%} {tsla_cum:7.1%} {rblx_cum:7.1%} {spy_cum:7.1%}")
    
    # Quarterly analysis
    print(f"\n📊 QUARTERLY PERFORMANCE:")
    print("-" * 60)
    
    quarterly_data = results_df.resample('Q').agg({
        'portfolio_value': 'last'
    })
    quarterly_data['quarterly_return'] = quarterly_data['portfolio_value'].pct_change()
    quarterly_data['cumulative_return'] = (quarterly_data['portfolio_value'] / 5000) - 1
    
    for i, (date, row) in enumerate(quarterly_data.iterrows()):
        quarter = f"Q{date.quarter} {date.year}"
        quarterly_ret = row['quarterly_return'] if not pd.isna(row['quarterly_return']) else 0
        cumul_ret = row['cumulative_return']
        
        print(f"{quarter:8} | {quarterly_ret:+7.1%} (Cumulative: {cumul_ret:+7.1%})")
    
    # Risk-adjusted metrics
    risk_free_rate = 0.05 / 12  # Assume 5% annual risk-free rate
    excess_returns = monthly_returns - risk_free_rate
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(12) if excess_returns.std() > 0 else 0
    
    print(f"\n📏 RISK-ADJUSTED METRICS:")
    print("-" * 40)
    print(f"Annualized Sharpe Ratio:  {sharpe_ratio:.2f}")
    print(f"Monthly Win Rate:         {(monthly_returns > 0).mean():.0%}")
    print(f"Average Win:              {monthly_returns[monthly_returns > 0].mean():+.1%}")
    print(f"Average Loss:             {monthly_returns[monthly_returns < 0].mean():+.1%}")
    
    win_loss_ratio = abs(monthly_returns[monthly_returns > 0].mean() / monthly_returns[monthly_returns < 0].mean()) if len(monthly_returns[monthly_returns < 0]) > 0 else np.inf
    print(f"Win/Loss Ratio:           {win_loss_ratio:.1f}x")
    
    return monthly_summary, monthly_data

if __name__ == "__main__":
    monthly_summary, monthly_data = analyze_monthly_performance()