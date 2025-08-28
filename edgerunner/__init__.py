"""
Edgerunner Trading Framework
===========================

Production-grade algorithmic trading framework with multi-venue execution,
robust risk management, and comprehensive backtesting capabilities.

Modules:
--------
- alpha: Alpha generation and signal processing
- strategies: Strategy implementations and wrappers  
- execution: Order routing and execution management
- brokers: Multi-broker connectivity (IBKR, Bybit, MT5)
- risk: Risk management and position sizing
- backtest: Backtesting engines and adapters
- monitor: System monitoring and alerting
- reports: Performance reporting and analytics
- utils: Common utilities and helpers
- models: Machine learning models and features
- api: REST/WebSocket API endpoints
- db: Database models and schemas

Usage:
------
```python
from edgerunner import EdgerunnerFramework

# Initialize framework
framework = EdgerunnerFramework(config_path="config/")
framework.start()

# Run backtest
results = framework.backtest.run_strategy("btcusdt_ftmo")

# Generate report  
framework.reports.generate_html_report(results)
```
"""

__version__ = "1.0.0"
__author__ = "Edgerunner Development Team"

# Import main framework class
from .core import EdgerunnerFramework

__all__ = ["EdgerunnerFramework", "__version__"]