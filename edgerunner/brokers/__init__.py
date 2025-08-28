"""
Broker Connectivity Module
==========================

Multi-broker support with unified interface for IBKR, Bybit, MT5, and others.

Components:
-----------
- BrokerManager: Main broker management and routing
- IBKRClient: Interactive Brokers connectivity
- BybitClient: Bybit exchange connectivity
- MT5Client: MetaTrader 5 connectivity
- BrokerAdapter: Unified broker interface

Example:
--------
```python
from edgerunner.brokers import BrokerManager

brokers = BrokerManager(config)
brokers.connect_all()
order_id = brokers.place_order('BTCUSDT', 'BUY', 100, broker='bybit')
```
"""

from .manager import BrokerManager
from .ibkr_client import IBKRClient
from .bybit_client import BybitClient
from .mt5_client import MT5Client
from .adapter import BrokerAdapter

__all__ = [
    "BrokerManager",
    "IBKRClient",
    "BybitClient",
    "MT5Client",
    "BrokerAdapter"
]