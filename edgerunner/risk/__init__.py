"""
Risk Management Module
=====================

Comprehensive risk management with position sizing, guards, and exposure limits.

Components:
-----------
- RiskManager: Main risk management engine
- PositionSizer: Kelly criterion and other position sizing methods
- RiskGuards: Circuit breakers and risk guards
- ExposureManager: Portfolio exposure and correlation limits
- VaRCalculator: Value at Risk calculations

Example:
--------
```python
from edgerunner.risk import RiskManager

risk_mgr = RiskManager(config)
position_size = risk_mgr.calculate_position_size('BTCUSDT', signal_strength=0.8)
```
"""

from .manager import RiskManager
from .position_sizing import PositionSizer, KellyCalculator
from .guards import RiskGuards, CircuitBreaker
from .exposure import ExposureManager
from .metrics import VaRCalculator, RiskMetrics

__all__ = [
    "RiskManager",
    "PositionSizer",
    "KellyCalculator",
    "RiskGuards",
    "CircuitBreaker", 
    "ExposureManager",
    "VaRCalculator",
    "RiskMetrics"
]