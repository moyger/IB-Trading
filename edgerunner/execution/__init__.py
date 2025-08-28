"""
Execution Module
===============

Order execution, routing, and trade management.

Components:
-----------
- ExecutionEngine: Main execution engine
- OrderRouter: Intelligent order routing
- SlippageModel: Slippage estimation and modeling
- TradeManager: Trade lifecycle management

Example:
--------
```python
from edgerunner.execution import ExecutionEngine

engine = ExecutionEngine(brokers, risk_manager, config)
order_id = engine.execute_signal('BTCUSDT', 'BUY', 1000)
```
"""

from .engine import ExecutionEngine
from .router import OrderRouter
from .slippage import SlippageModel
from .trade_manager import TradeManager

__all__ = [
    "ExecutionEngine",
    "OrderRouter", 
    "SlippageModel",
    "TradeManager"
]