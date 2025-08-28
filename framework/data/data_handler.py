"""
Universal Data Handler

Handles data acquisition and preprocessing for crypto, stocks, and forex.
Supports multiple data sources with unified interface.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging
from pathlib import Path

from ..core.universal_strategy import AssetType


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = '1h') -> pd.DataFrame:
        """Fetch OHLCV data for given symbol and period"""
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        """Validate if symbol is supported by this data source"""
        pass


class YFinanceSource(DataSource):
    """Yahoo Finance data source for stocks and crypto"""
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = '1h') -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance
        
        Args:
            symbol: Ticker symbol (e.g., 'BTC-USD', 'AAPL')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Standardize column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Remove timezone info for consistency
            if data.index.tz is not None:
                data.index = data.index.tz_localize(None)
            
            return data
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from Yahoo Finance: {str(e)}")
    
    def validate_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        """Validate Yahoo Finance symbol format"""
        if asset_type == AssetType.CRYPTO:
            return '-USD' in symbol or '-USDT' in symbol
        elif asset_type == AssetType.STOCKS:
            return len(symbol) <= 5 and symbol.isalpha()
        return False


class BinanceSource(DataSource):
    """Binance data source for crypto (requires binance package)"""
    
    def __init__(self):
        self.client = None
        try:
            from binance.client import Client
            # Note: For historical data, we don't need API keys
            self.client = Client()
        except ImportError:
            logging.warning("Binance package not installed. Install with: pip install python-binance")
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = '1h') -> pd.DataFrame:
        """Fetch data from Binance API"""
        if self.client is None:
            raise RuntimeError("Binance client not available. Install python-binance package.")
        
        try:
            # Convert interval format
            interval_map = {
                '1m': Client.KLINE_INTERVAL_1MINUTE,
                '5m': Client.KLINE_INTERVAL_5MINUTE,
                '15m': Client.KLINE_INTERVAL_15MINUTE,
                '30m': Client.KLINE_INTERVAL_30MINUTE,
                '1h': Client.KLINE_INTERVAL_1HOUR,
                '4h': Client.KLINE_INTERVAL_4HOUR,
                '1d': Client.KLINE_INTERVAL_1DAY
            }
            
            binance_interval = interval_map.get(interval, Client.KLINE_INTERVAL_1HOUR)
            
            # Fetch historical klines
            klines = self.client.get_historical_klines(
                symbol, binance_interval, start_date, end_date
            )
            
            if not klines:
                raise ValueError(f"No data found for {symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Select and convert relevant columns
            ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in ohlcv_cols:
                df[col] = pd.to_numeric(df[col])
            
            return df[ohlcv_cols]
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from Binance: {str(e)}")
    
    def validate_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        """Validate Binance symbol format"""
        return asset_type == AssetType.CRYPTO and symbol.endswith('USDT')


class ForexSource(DataSource):
    """Forex data source (placeholder - would integrate with forex provider)"""
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = '1h') -> pd.DataFrame:
        """Placeholder for forex data fetching"""
        # This would integrate with a forex data provider like OANDA, FXCM, etc.
        raise NotImplementedError("Forex data source not yet implemented")
    
    def validate_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        """Validate forex symbol format"""
        return asset_type == AssetType.FOREX and len(symbol) == 6


class DataHandler:
    """
    Universal data handler for multi-asset backtesting.
    
    Automatically selects appropriate data source based on asset type and symbol.
    Provides unified interface for data acquisition and preprocessing.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize data handler.
        
        Args:
            cache_dir: Directory for caching data (optional)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data sources
        self.sources = {
            'yfinance': YFinanceSource(),
            'binance': BinanceSource(),
            'forex': ForexSource()
        }
        
        # Asset type to preferred data source mapping
        self.preferred_sources = {
            AssetType.STOCKS: ['yfinance'],
            AssetType.CRYPTO: ['yfinance', 'binance'], 
            AssetType.FOREX: ['forex', 'yfinance']
        }
    
    def fetch_data(self, symbol: str, asset_type: AssetType,
                   start_date: str, end_date: str, 
                   interval: str = '1h',
                   source: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch OHLCV data for given asset.
        
        Args:
            symbol: Asset symbol
            asset_type: Type of asset (crypto/stocks/forex)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            source: Force specific data source (optional)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Check cache first
        if self.cache_dir:
            cached_data = self._load_from_cache(symbol, start_date, end_date, interval)
            if cached_data is not None:
                return cached_data
        
        # Determine data source
        if source:
            if source not in self.sources:
                raise ValueError(f"Unknown data source: {source}")
            data_source = self.sources[source]
        else:
            data_source = self._select_data_source(symbol, asset_type)
        
        # Fetch data
        data = data_source.fetch_data(symbol, start_date, end_date, interval)
        
        # Validate and clean data
        data = self._clean_data(data)
        
        # Cache data
        if self.cache_dir:
            self._save_to_cache(data, symbol, start_date, end_date, interval)
        
        return data
    
    def fetch_multiple_assets(self, symbols: List[str], asset_types: List[AssetType],
                             start_date: str, end_date: str, 
                             interval: str = '1h') -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple assets.
        
        Args:
            symbols: List of asset symbols
            asset_types: List of asset types (same length as symbols)
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        if len(symbols) != len(asset_types):
            raise ValueError("symbols and asset_types must have same length")
        
        data = {}
        for symbol, asset_type in zip(symbols, asset_types):
            try:
                data[symbol] = self.fetch_data(
                    symbol, asset_type, start_date, end_date, interval
                )
            except Exception as e:
                logging.error(f"Failed to fetch data for {symbol}: {str(e)}")
                continue
        
        return data
    
    def _select_data_source(self, symbol: str, asset_type: AssetType) -> DataSource:
        """Select best data source for given symbol and asset type"""
        preferred = self.preferred_sources.get(asset_type, ['yfinance'])
        
        for source_name in preferred:
            source = self.sources[source_name]
            if source.validate_symbol(symbol, asset_type):
                return source
        
        # Fallback to yfinance
        return self.sources['yfinance']
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data"""
        # Remove duplicates
        data = data[~data.index.duplicated(keep='first')]
        
        # Sort by index
        data = data.sort_index()
        
        # Remove rows with all NaN values
        data = data.dropna(how='all')
        
        # Forward fill missing values (conservative approach)
        data = data.fillna(method='ffill')
        
        # Remove remaining NaN rows
        data = data.dropna()
        
        # Validate OHLC relationships
        invalid_rows = (
            (data['High'] < data['Low']) |
            (data['High'] < data['Open']) |
            (data['High'] < data['Close']) |
            (data['Low'] > data['Open']) |
            (data['Low'] > data['Close'])
        )
        
        if invalid_rows.any():
            logging.warning(f"Removing {invalid_rows.sum()} rows with invalid OHLC data")
            data = data[~invalid_rows]
        
        return data
    
    def _load_from_cache(self, symbol: str, start_date: str, 
                        end_date: str, interval: str) -> Optional[pd.DataFrame]:
        """Load data from cache if available"""
        cache_file = self.cache_dir / f"{symbol}_{start_date}_{end_date}_{interval}.parquet"
        
        if cache_file.exists():
            try:
                return pd.read_parquet(cache_file)
            except Exception as e:
                logging.warning(f"Failed to load cache file: {str(e)}")
        
        return None
    
    def _save_to_cache(self, data: pd.DataFrame, symbol: str, 
                      start_date: str, end_date: str, interval: str):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{symbol}_{start_date}_{end_date}_{interval}.parquet"
        
        try:
            data.to_parquet(cache_file)
        except Exception as e:
            logging.warning(f"Failed to save cache file: {str(e)}")
    
    def get_available_symbols(self, asset_type: AssetType) -> List[str]:
        """Get list of available symbols for asset type (basic implementation)"""
        # This would be expanded to query actual available symbols
        if asset_type == AssetType.CRYPTO:
            return ['BTC-USD', 'ETH-USD', 'BTCUSDT', 'ETHUSDT']
        elif asset_type == AssetType.STOCKS:
            return ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        elif asset_type == AssetType.FOREX:
            return ['EURUSD', 'GBPUSD', 'XAUUSD']
        return []
    
    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[str, str]:
        """Validate and format date range"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start >= end:
                raise ValueError("Start date must be before end date")
            
            if end > datetime.now():
                end = datetime.now() - timedelta(days=1)
                logging.warning(f"End date adjusted to {end.strftime('%Y-%m-%d')}")
            
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
            
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")