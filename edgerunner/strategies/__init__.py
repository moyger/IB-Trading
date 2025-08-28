"""
Strategy Management Module
=========================

Strategy implementations, execution, and lifecycle management.

Components:
-----------
- StrategyManager: Main strategy orchestration
- BaseStrategy: Base class for all strategies
- StrategyRunner: Strategy execution engine
- StrategyOptimizer: Parameter optimization

Example:
--------
```python
from edgerunner.strategies import StrategyManager

manager = StrategyManager(config)
manager.start_strategy('btcusdt_ftmo')
```
"""

from .manager import StrategyManager
from .base import BaseStrategy
from .runner import StrategyRunner

__all__ = [
    "StrategyManager", 
    "BaseStrategy",
    "StrategyRunner"
]