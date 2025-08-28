"""
Backtesting Module
=================

Multi-engine backtesting with adapters for VectorBT, backtesting.py, and QuantConnect Lean.

Components:
-----------
- BacktestEngine: Main backtesting engine with adapter pattern
- VectorBTAdapter: VectorBT integration
- BacktestingPyAdapter: backtesting.py integration  
- LeanAdapter: QuantConnect Lean integration
- PerformanceAnalyzer: Performance metrics calculation

Example:
--------
```python
from edgerunner.backtest import BacktestEngine

engine = BacktestEngine(config)
results = engine.run_strategy('btcusdt_ftmo', engine='vectorbt')
```
"""

from .engine import BacktestEngine
from .adapters import VectorBTAdapter, BacktestingPyAdapter, LeanAdapter
from .performance import PerformanceAnalyzer

__all__ = [
    "BacktestEngine",
    "VectorBTAdapter",
    "BacktestingPyAdapter", 
    "LeanAdapter",
    "PerformanceAnalyzer"
]