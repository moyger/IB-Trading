#!/usr/bin/env python3
"""
Analyze BTC strategy performance and market conditions
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

def analyze_btc_market_data():
    # Test direct data download to understand what data we can access
    ticker = yf.Ticker('BTC-USD')
    
    # Test different periods to understand performance
    test_periods = [
        ('2024-01-01', '2024-02-29'),  # Feb 2024 mentioned as exceptional
        ('2024-03-01', '2024-04-30'),  # Spring period
        ('2024-05-01', '2024-06-30'),  # Early summer
    ]
    
    print('Testing BTC-USD data availability and basic statistics:')
    print('='*80)
    
    for start, end in test_periods:
        try:
            df = ticker.history(start=start, end=end, interval='1h')
            if not df.empty:
                returns = df['Close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(24 * 365) * 100  # Annualized
                total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
                
                print(f'\nPeriod: {start} to {end}')
                print(f'  Data points: {len(df)}')
                print(f'  Price range: ${df["Close"].min():.0f} - ${df["Close"].max():.0f}')
                print(f'  Period return: {total_return:.1f}%')
                print(f'  Annualized volatility: {volatility:.1f}%')
                print(f'  Avg daily volume: ${df["Volume"].mean()/1e9:.1f}B')
        except Exception as e:
            print(f'Error for period {start} to {end}: {e}')
    
    # Now test daily data for longer period analysis
    print('\n' + '='*80)
    print('Testing longer-term daily data:')
    print('='*80)
    
    df_daily = ticker.history(start='2023-01-01', end='2024-12-31', interval='1d')
    if not df_daily.empty:
        # Calculate monthly returns
        df_daily['Month'] = pd.to_datetime(df_daily.index).to_period('M')
        monthly_returns = df_daily.groupby('Month')['Close'].agg(['first', 'last'])
        monthly_returns['return'] = (monthly_returns['last'] / monthly_returns['first'] - 1) * 100
        
        print(f'\nMonthly BTC Returns (2023-2024):')
        for month, row in monthly_returns.iterrows():
            if not pd.isna(row['return']):
                print(f'  {month}: {row["return"]:+.1f}%')
        
        # Identify best and worst months
        best_month = monthly_returns['return'].idxmax()
        worst_month = monthly_returns['return'].idxmin()
        
        print(f'\nBest Month: {best_month} ({monthly_returns.loc[best_month, "return"]:+.1f}%)')
        print(f'Worst Month: {worst_month} ({monthly_returns.loc[worst_month, "return"]:+.1f}%)')
        
        # Calculate overall statistics
        print(f'\nOverall Statistics:')
        print(f'  Average monthly return: {monthly_returns["return"].mean():.1f}%')
        print(f'  Median monthly return: {monthly_returns["return"].median():.1f}%')
        print(f'  Monthly volatility: {monthly_returns["return"].std():.1f}%')
        print(f'  Positive months: {(monthly_returns["return"] > 0).sum()} / {len(monthly_returns)}')

if __name__ == "__main__":
    analyze_btc_market_data()