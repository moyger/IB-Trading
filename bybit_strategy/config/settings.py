"""
Configuration settings for Bybit 1H Trend Composite Strategy
Adapted from FTMO strategy with crypto-specific optimizations
"""

import os
from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    
    # Account Settings
    initial_balance: float = 10000  # USDT
    testnet: bool = True  # Use testnet by default
    
    # Risk Management (adapted from FTMO)
    risk_per_trade: float = 1.5  # 1.5% per trade (vs FTMO's 1.25%)
    max_daily_risk: float = 5.0  # 5% max daily drawdown
    max_position_size: float = 25.0  # 25% max position size
    max_open_positions: int = 3  # Maximum concurrent positions
    
    # Timeframe Settings
    timeframe: str = '4h'  # 4-hour timeframe
    lookback_periods: int = 200  # 200 x 4H candles (~33 days)
    
    # Strategy Thresholds (4H timeframe optimized)
    min_trend_strength: float = 3.5  # Higher threshold for 4H (was 3.0)
    momentum_threshold: float = 3.0  # Stronger momentum filter (was 2.0)
    volume_threshold: float = 1.2  # Higher volume confirmation (was 0.8)
    
    # Crypto-Specific Settings
    funding_rate_threshold: float = 0.1  # Max funding rate
    volatility_filter: bool = True  # Enable volatility filtering
    use_market_hours: bool = False  # Crypto trades 24/7
    
    # Stop Loss and Take Profit Multipliers (4H optimized)
    sl_atr_multiplier: float = 3.0  # Wider stops for 4H (was 2.5)
    tp_atr_multiplier: float = 6.0  # Higher targets for 4H (was 4.0)
    trailing_stop: bool = True  # Enable trailing stops for longer timeframe
    trailing_stop_activation: float = 2.5  # Activate after 2.5x ATR profit
    trailing_stop_distance: float = 2.0  # Trail by 2.0x ATR
    
    # Position Sizing
    use_fixed_lot: bool = False
    fixed_lot_size: float = 0.01
    use_kelly_criterion: bool = False
    kelly_fraction: float = 0.25  # Conservative Kelly

@dataclass
class IndicatorConfig:
    """Technical indicator configuration"""
    
    # EMA Settings (4H timeframe optimized)
    ema_fast: int = 12  # Slower for 4H (was 8 for 1H)
    ema_medium: int = 26  # Standard FTMO setting
    ema_slow: int = 50  # Same as FTMO
    
    # RSI Settings (4H timeframe)
    rsi_period: int = 14  # Standard setting for 4H
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    rsi_strong_trend: float = 60.0
    rsi_weak_trend: float = 40.0
    
    # MACD Settings (4H timeframe)
    macd_fast: int = 12  # Standard FTMO setting
    macd_slow: int = 26  # Standard FTMO setting
    macd_signal: int = 9  # Standard FTMO setting
    
    # Bollinger Bands
    bb_period: int = 20
    bb_std_dev: float = 2.0
    
    # Volume Analysis
    volume_ma_period: int = 20
    volume_spike_threshold: float = 1.2
    
    # ATR Settings
    atr_period: int = 14
    atr_smoothing: str = 'RMA'  # RMA or SMA
    
    # Momentum Settings
    momentum_short: int = 5
    momentum_long: int = 10

@dataclass
class SymbolConfig:
    """Symbol-specific configuration"""
    
    # Primary Trading Pairs
    symbols: List[str] = field(default_factory=lambda: [
        'BTC/USDT:USDT',  # Bitcoin
        'ETH/USDT:USDT',  # Ethereum
        'SOL/USDT:USDT',  # Solana
        'ADA/USDT:USDT',  # Cardano
        'DOT/USDT:USDT',  # Polkadot
    ])
    
    # Alternative pairs for testing
    alt_symbols: List[str] = field(default_factory=lambda: [
        'AVAX/USDT:USDT',  # Avalanche
        'MATIC/USDT:USDT',  # Polygon
        'LINK/USDT:USDT',  # Chainlink
        'UNI/USDT:USDT',  # Uniswap
        'ATOM/USDT:USDT',  # Cosmos
    ])
    
    # Symbol-specific overrides
    symbol_overrides: Dict = field(default_factory=lambda: {
        'BTC/USDT:USDT': {
            'risk_per_trade': 1.0,  # Lower risk for BTC
            'sl_atr_multiplier': 2.0,
        },
        'SOL/USDT:USDT': {
            'risk_per_trade': 2.0,  # Higher risk for more volatile
            'momentum_threshold': 3.0,
        }
    })

@dataclass
class APIConfig:
    """API configuration settings"""
    
    # Bybit API Settings
    api_key: str = os.getenv('BYBIT_API_KEY', '')
    api_secret: str = os.getenv('BYBIT_API_SECRET', '')
    
    # Endpoint Settings
    testnet_endpoint: str = 'https://api-testnet.bybit.com'
    mainnet_endpoint: str = 'https://api.bybit.com'
    
    # WebSocket Settings
    ws_testnet: str = 'wss://stream-testnet.bybit.com/v5/public/linear'
    ws_mainnet: str = 'wss://stream.bybit.com/v5/public/linear'
    
    # Rate Limiting
    rate_limit: bool = True
    requests_per_second: int = 10
    
    # Webhook Settings (for TradingView integration)
    webhook_url: str = os.getenv('WEBHOOK_URL', 'https://tradingview-webhook.karloestrada.workers.dev')
    webhook_auth_token: str = os.getenv('WEBHOOK_AUTH', '')
    
    # Retry Settings
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    
    # Data Settings
    start_date: str = '2024-01-01'
    end_date: str = '2024-12-31'
    
    # Commission and Slippage
    maker_fee: float = 0.01  # 0.01% maker fee
    taker_fee: float = 0.06  # 0.06% taker fee
    slippage: float = 0.05  # 0.05% slippage
    
    # Backtesting Parameters
    initial_capital: float = 10000
    use_spread: bool = True
    spread_points: int = 2
    
    # Performance Metrics
    calculate_sharpe: bool = True
    calculate_sortino: bool = True
    calculate_calmar: bool = True
    risk_free_rate: float = 0.05  # 5% annual

@dataclass
class LoggingConfig:
    """Logging configuration"""
    
    # File Settings
    log_dir: str = 'logs'
    log_file: str = 'bybit_strategy.log'
    
    # Logging Levels
    console_level: str = 'INFO'
    file_level: str = 'DEBUG'
    
    # Rotation Settings
    rotate_logs: bool = True
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    
    # Trade Logging
    log_trades: bool = True
    trade_log_file: str = 'trades.csv'
    
    # Performance Logging
    log_performance: bool = True
    performance_interval: int = 3600  # Log every hour

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.trading = TradingConfig()
        self.indicators = IndicatorConfig()
        self.symbols = SymbolConfig()
        self.api = APIConfig()
        self.backtest = BacktestConfig()
        self.logging = LoggingConfig()
    
    def get_symbol_config(self, symbol: str) -> dict:
        """Get configuration for specific symbol"""
        base_config = {
            'risk_per_trade': self.trading.risk_per_trade,
            'sl_atr_multiplier': self.trading.sl_atr_multiplier,
            'tp_atr_multiplier': self.trading.tp_atr_multiplier,
            'momentum_threshold': self.trading.momentum_threshold,
        }
        
        # Apply symbol-specific overrides
        if symbol in self.symbols.symbol_overrides:
            base_config.update(self.symbols.symbol_overrides[symbol])
        
        return base_config
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Validate risk settings
        if self.trading.risk_per_trade > 5.0:
            errors.append("Risk per trade exceeds 5%")
        
        if self.trading.max_daily_risk > 10.0:
            errors.append("Max daily risk exceeds 10%")
        
        # Validate API settings
        if not self.trading.testnet and not self.api.api_key:
            errors.append("API key required for mainnet trading")
        
        # Validate indicator settings
        if self.indicators.ema_fast >= self.indicators.ema_medium:
            errors.append("Fast EMA must be less than medium EMA")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'trading': self.trading.__dict__,
            'indicators': self.indicators.__dict__,
            'symbols': self.symbols.__dict__,
            'api': {k: v for k, v in self.api.__dict__.items() 
                   if k not in ['api_key', 'api_secret', 'webhook_auth_token']},
            'backtest': self.backtest.__dict__,
            'logging': self.logging.__dict__,
        }

# Global configuration instance
config = Config()