"""
IB Trading Universal Backtesting Framework

A professional-grade backtesting framework built on VectorBT, Pandas, and NumPy
for testing crypto, stocks, and forex algorithmic trading strategies.

Key Features:
- Ultra-fast vectorized backtesting (100-1000x faster than event-driven)
- Multi-asset support (crypto, stocks, forex)
- Professional risk management
- Comprehensive reporting and analytics
- FTMO compliance built-in
- Monthly performance tracking
"""

__version__ = "1.0.0"
__author__ = "IB Trading Framework"

# Core framework imports
from .core.universal_strategy import UniversalStrategy
from .core.backtest_engine import BacktestEngine
from .data.data_handler import DataHandler
from .portfolio.risk_manager import RiskManager
from .reporting.performance_analyzer import PerformanceAnalyzer

__all__ = [
    'UniversalStrategy',
    'BacktestEngine', 
    'DataHandler',
    'RiskManager',
    'PerformanceAnalyzer'
]