"""
Alpha Generation Module
======================

Alpha functions and signal processing for generating trading signals.

Components:
-----------
- AlphaEngine: Main alpha generation engine
- SignalProcessor: Signal processing and filtering
- FeatureEngine: Feature extraction and engineering
- AlphaModel: Base class for alpha models

Example:
--------
```python
from edgerunner.alpha import AlphaEngine

engine = AlphaEngine(config)
signals = engine.generate_signals(['BTCUSDT'], timeframe='1h')
```
"""

from .engine import AlphaEngine
from .signals import SignalProcessor
from .features import FeatureEngine
from .models import AlphaModel

__all__ = [
    "AlphaEngine",
    "SignalProcessor", 
    "FeatureEngine",
    "AlphaModel"
]