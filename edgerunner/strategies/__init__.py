"""
Strategy Management Module
=========================

Strategy implementations organized by asset class with execution and lifecycle management.

Asset Classes:
--------------
- forex/: Forex and metals trading strategies (XAUUSD, EURUSD, etc.)
- crypto/: Cryptocurrency strategies (BTCUSDT, ETHUSDT, etc.) 
- stocks/: Equity strategies (individual stocks, ETFs)
- indices/: Index-based strategies (SPX, NDX, etc.)

Components:
-----------
- StrategyManager: Main strategy orchestration
- BaseStrategy: Base class for all strategies
- StrategyRunner: Strategy execution engine

Example:
--------
```python
from edgerunner.strategies import StrategyManager
from edgerunner.strategies.forex import FOREX_STRATEGIES
from edgerunner.strategies.crypto import CRYPTO_STRATEGIES

manager = StrategyManager(config)

# Run forex strategy
manager.start_strategy('xauusd_ftmo_1h', broker='mt5')

# Run crypto strategy  
manager.start_strategy('btcusdt_enhanced', broker='bybit')
```
"""

from .manager import StrategyManager
from .base import BaseStrategy
from .runner import StrategyRunner

# Import asset class modules
from . import forex
from . import crypto
from . import stocks
from . import indices

# Aggregate all strategies
ALL_STRATEGIES = {
    **forex.FOREX_STRATEGIES,
    **crypto.CRYPTO_STRATEGIES,
    **stocks.STOCK_STRATEGIES,
    **indices.INDICES_STRATEGIES,
}

# Aggregate all symbols
ALL_SYMBOLS = {
    **forex.FOREX_SYMBOLS,
    **crypto.CRYPTO_SYMBOLS, 
    **stocks.STOCK_SYMBOLS,
    **indices.INDICES_SYMBOLS,
}

# Asset class mapping
ASSET_CLASSES = {
    'forex': forex,
    'crypto': crypto,
    'stocks': stocks,
    'indices': indices
}

__all__ = [
    "StrategyManager", 
    "BaseStrategy",
    "StrategyRunner",
    "forex",
    "crypto", 
    "stocks",
    "indices",
    "ALL_STRATEGIES",
    "ALL_SYMBOLS",
    "ASSET_CLASSES"
]