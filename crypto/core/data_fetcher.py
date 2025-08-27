#!/usr/bin/env python3
"""
Enhanced Data Fetcher for BTCUSDT Strategy
Supports multiple data sources with robust error handling and preprocessing
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import warnings
import time
from typing import Optional, Tuple, Dict, Any

warnings.filterwarnings('ignore')

class BTCDataFetcher:
    """Enhanced data fetcher with multiple sources and preprocessing"""
    
    def __init__(self):
        self.primary_source = 'yfinance'
        self.backup_sources = ['binance_api']
        
    def fetch_btc_data(self, start_date: str, end_date: str, 
                       interval: str = '1h', symbol: str = 'BTC-USD') -> Optional[pd.DataFrame]:
        """
        Fetch BTCUSDT data with fallback sources
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD) 
            interval: Data interval (1h, 4h, 1d)
            symbol: Trading symbol
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        print(f"📊 Fetching {symbol} data from {start_date} to {end_date} ({interval})")
        
        # Try primary source first
        df = self._fetch_yfinance(symbol, start_date, end_date, interval)
        
        if df is not None and not df.empty:
            return self._preprocess_data(df)
        
        print("⚠️ Primary source failed, trying backup sources...")
        
        # Try backup sources
        for source in self.backup_sources:
            if source == 'binance_api':
                df = self._fetch_binance_fallback(start_date, end_date, interval)
                if df is not None and not df.empty:
                    return self._preprocess_data(df)
        
        print("❌ All data sources failed")
        return None
    
    def _fetch_yfinance(self, symbol: str, start_date: str, end_date: str, 
                       interval: str) -> Optional[pd.DataFrame]:
        """Fetch data using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                print(f"❌ No data returned from yfinance for {symbol}")
                return None
                
            print(f"✅ Downloaded {len(df)} {interval} periods from yfinance")
            return df
            
        except Exception as e:
            print(f"❌ yfinance error: {e}")
            return None
    
    def _fetch_binance_fallback(self, start_date: str, end_date: str, 
                               interval: str) -> Optional[pd.DataFrame]:
        """Fallback to Binance API for BTCUSDT data"""
        try:
            # Convert interval to Binance format
            binance_interval = self._convert_interval_to_binance(interval)
            
            # Convert dates to milliseconds
            start_ms = int(pd.to_datetime(start_date).timestamp() * 1000)
            end_ms = int(pd.to_datetime(end_date).timestamp() * 1000)
            
            # Binance API endpoint
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': 'BTCUSDT',
                'interval': binance_interval,
                'startTime': start_ms,
                'endTime': end_ms,
                'limit': 1000
            }
            
            # Fetch data in chunks if needed
            all_data = []
            current_start = start_ms
            
            while current_start < end_ms:
                params['startTime'] = current_start
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code != 200:
                    print(f"❌ Binance API error: {response.status_code}")
                    break
                
                data = response.json()
                if not data:
                    break
                
                all_data.extend(data)
                current_start = data[-1][6] + 1  # Next start time
                time.sleep(0.1)  # Rate limiting
            
            if not all_data:
                return None
            
            # Convert to DataFrame
            columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                      'Close time', 'Quote asset volume', 'Number of trades',
                      'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
            
            df = pd.DataFrame(all_data, columns=columns)
            
            # Convert to standard format
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
            df = df.set_index('Open time')
            
            # Select and convert OHLCV columns
            ohlcv_df = pd.DataFrame({
                'Open': pd.to_numeric(df['Open']),
                'High': pd.to_numeric(df['High']),
                'Low': pd.to_numeric(df['Low']),
                'Close': pd.to_numeric(df['Close']),
                'Volume': pd.to_numeric(df['Volume'])
            }, index=df.index)
            
            print(f"✅ Downloaded {len(ohlcv_df)} periods from Binance API")
            return ohlcv_df
            
        except Exception as e:
            print(f"❌ Binance API error: {e}")
            return None
    
    def _convert_interval_to_binance(self, interval: str) -> str:
        """Convert interval to Binance format"""
        interval_map = {
            '1m': '1m',
            '5m': '5m', 
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        return interval_map.get(interval, '1h')
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess raw OHLCV data with quality checks and enhancements"""
        print("🔧 Preprocessing data...")
        
        # Data quality checks
        df = self._quality_checks(df)
        
        # Add basic technical indicators for preprocessing
        df = self._add_basic_indicators(df)
        
        # Market hours detection (crypto trades 24/7 but good to track sessions)
        df = self._add_market_sessions(df)
        
        print(f"✅ Preprocessed data ready: {len(df)} periods")
        return df
    
    def _quality_checks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform data quality checks and cleaning"""
        initial_len = len(df)
        
        # Remove rows with missing OHLCV data
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        
        # Check for invalid price relationships
        invalid_mask = (
            (df['High'] < df['Low']) |
            (df['High'] < df['Open']) |
            (df['High'] < df['Close']) |
            (df['Low'] > df['Open']) |
            (df['Low'] > df['Close'])
        )
        
        if invalid_mask.any():
            print(f"⚠️ Removing {invalid_mask.sum()} invalid price bars")
            df = df[~invalid_mask]
        
        # Remove extreme outliers (price movements > 50% in one bar)
        price_change = df['Close'].pct_change()
        outlier_mask = abs(price_change) > 0.5
        
        if outlier_mask.any():
            print(f"⚠️ Removing {outlier_mask.sum()} extreme outlier bars")
            df = df[~outlier_mask]
        
        # Fill missing volume with median
        if 'Volume' in df.columns:
            median_volume = df['Volume'].median()
            df['Volume'] = df['Volume'].fillna(median_volume)
        else:
            df['Volume'] = 1  # Default volume if not available
        
        removed_count = initial_len - len(df)
        if removed_count > 0:
            print(f"🔧 Data cleaning: Removed {removed_count} invalid bars")
        
        return df
    
    def _add_basic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic preprocessing indicators"""
        # True Range for volatility calculation
        df['high_low'] = df['High'] - df['Low']
        df['high_close'] = abs(df['High'] - df['Close'].shift(1))
        df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        
        # Average True Range (14-period)
        df['atr_14'] = df['true_range'].rolling(window=14).mean()
        
        # Price-based volatility measures
        df['close_pct_change'] = df['Close'].pct_change()
        df['volatility_20'] = df['close_pct_change'].rolling(window=20).std()
        
        # Volume-based indicators
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
        
        # Price gaps (important for crypto)
        df['gap'] = df['Open'] - df['Close'].shift(1)
        df['gap_pct'] = (df['gap'] / df['Close'].shift(1)) * 100
        
        return df
    
    def _add_market_sessions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market session information (useful even for 24/7 crypto)"""
        # Add hour and day of week
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        
        # Define major market sessions (crypto has higher activity during these times)
        def get_session(hour):
            if 0 <= hour < 8:
                return 'Asian'
            elif 8 <= hour < 16:
                return 'European'
            else:
                return 'American'
        
        df['session'] = df['hour'].apply(get_session)
        
        # Weekend vs weekday (crypto trades 24/7 but patterns may differ)
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive data summary"""
        if df is None or df.empty:
            return {}
        
        return {
            'total_periods': len(df),
            'date_range': {
                'start': df.index.min().strftime('%Y-%m-%d %H:%M'),
                'end': df.index.max().strftime('%Y-%m-%d %H:%M')
            },
            'price_range': {
                'min': df['Low'].min(),
                'max': df['High'].max(),
                'current': df['Close'].iloc[-1]
            },
            'volume_stats': {
                'total': df['Volume'].sum(),
                'average': df['Volume'].mean(),
                'max_single_period': df['Volume'].max()
            },
            'quality_metrics': {
                'missing_data_pct': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'avg_volatility': df['volatility_20'].mean() * 100,
                'avg_daily_range': (df['High'] - df['Low']).mean() / df['Close'].mean() * 100
            }
        }


if __name__ == "__main__":
    # Test the data fetcher
    print("🧪 Testing BTCUSDT Data Fetcher")
    print("=" * 50)
    
    fetcher = BTCDataFetcher()
    
    # Test with recent data
    df = fetcher.fetch_btc_data("2024-01-01", "2024-02-01", "1h")
    
    if df is not None:
        summary = fetcher.get_data_summary(df)
        
        print("📊 Data Summary:")
        print(f"Total periods: {summary['total_periods']}")
        print(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"Price range: ${summary['price_range']['min']:,.2f} - ${summary['price_range']['max']:,.2f}")
        print(f"Current price: ${summary['price_range']['current']:,.2f}")
        print(f"Average volatility: {summary['quality_metrics']['avg_volatility']:.2f}%")
        print(f"Missing data: {summary['quality_metrics']['missing_data_pct']:.2f}%")
        
        print("\n✅ Data fetcher test successful!")
    else:
        print("❌ Data fetcher test failed")