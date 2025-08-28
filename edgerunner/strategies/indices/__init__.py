"""
Indices Trading Strategies
==========================

Index-based trading strategies for major market indices.
"""

# Available indices strategies (placeholder for future development)
INDICES_STRATEGIES = {
    'sp500_momentum': 'SP500MomentumStrategy',
    'nasdaq_trend': 'NASDAQTrendStrategy',
    'dow_jones_breakout': 'DowJonesBreakoutStrategy',
}

# Major indices symbols
INDICES_SYMBOLS = {
    # US Indices
    'SPX': 'S&P 500 Index',
    'NDX': 'NASDAQ 100 Index', 
    'DJI': 'Dow Jones Industrial Average',
    'RUT': 'Russell 2000 Index',
    'VIX': 'CBOE Volatility Index',
    
    # International Indices
    'FTSE': 'FTSE 100 Index',
    'DAX': 'DAX 30 Index',
    'NIKKEI': 'Nikkei 225 Index',
    'HSI': 'Hang Seng Index',
    'ASX': 'ASX 200 Index'
}

# Broker mappings for indices
INDICES_BROKER_MAPPING = {
    # Interactive Brokers
    'interactive_brokers': {
        'SPX': 'SPX',
        'NDX': 'NDX',
        'DJI': 'INDU',
        'RUT': 'RUT',
        'VIX': 'VIX'
    },
    
    # MT5 (via webhook)
    'mt5': {
        'SPX': 'SP500',
        'DJI': 'DJ30',
        'NDX': 'NAS100',
        'FTSE': 'UK100',
        'DAX': 'GER30'
    }
}

__all__ = [
    'INDICES_STRATEGIES',
    'INDICES_SYMBOLS',
    'INDICES_BROKER_MAPPING'
]