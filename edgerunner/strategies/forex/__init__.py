"""
Forex Trading Strategies
========================

Production-ready forex strategies adapted from FTMO-compliant systems.
"""

from .xauusd_ftmo_1h_enhanced_strategy import XAUUSDFTMO1HEnhancedStrategy
from .xauusd_ftmo_1h_live_trader import FTMO1HLiveTrader

# Available forex strategies
FOREX_STRATEGIES = {
    'xauusd_ftmo_1h': XAUUSDFTMO1HEnhancedStrategy,
    'xauusd_live_trader': FTMO1HLiveTrader,
}

# Supported forex symbols
FOREX_SYMBOLS = {
    'XAUUSD': 'Gold vs USD',
    'XAGUSD': 'Silver vs USD', 
    'EURUSD': 'Euro vs USD',
    'GBPUSD': 'British Pound vs USD',
    'USDJPY': 'USD vs Japanese Yen',
    'AUDUSD': 'Australian Dollar vs USD',
    'USDCAD': 'USD vs Canadian Dollar',
    'NZDUSD': 'New Zealand Dollar vs USD',
    'USDCHF': 'USD vs Swiss Franc'
}

__all__ = [
    'XAUUSDFTMO1HEnhancedStrategy',
    'FTMO1HLiveTrader',
    'FOREX_STRATEGIES',
    'FOREX_SYMBOLS'
]