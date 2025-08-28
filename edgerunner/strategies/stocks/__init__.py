"""
Stock Trading Strategies
========================

Equity market strategies including momentum, trend-following, and multi-asset approaches.
"""

# Available stock strategies (will be populated after adaptation)
STOCK_STRATEGIES = {
    'dynamic_stock_selection': 'DynamicStockSelectionStrategy',
    'individual_stock_portfolio': 'IndividualStockPortfolioStrategy',
    'mtum_trend_composite': 'MTUMTrendCompositeStrategy',
    'three_stock_trend': 'ThreeStockTrendStrategy',
}

# Popular stock symbols
STOCK_SYMBOLS = {
    # Tech stocks
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation', 
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc.',
    'NFLX': 'Netflix Inc.',
    'NVDA': 'NVIDIA Corporation',
    
    # ETFs
    'SPY': 'SPDR S&P 500 ETF',
    'QQQ': 'Invesco QQQ Trust',
    'MTUM': 'Invesco MSCI USA Momentum Factor ETF',
    'VTI': 'Vanguard Total Stock Market ETF',
    'IWM': 'iShares Russell 2000 ETF',
    
    # Blue chips
    'MSFT': 'Microsoft Corporation',
    'JNJ': 'Johnson & Johnson',
    'UNH': 'UnitedHealth Group',
    'HD': 'The Home Depot',
    'PG': 'Procter & Gamble'
}

# Broker mappings for stocks
STOCK_BROKER_MAPPING = {
    # Interactive Brokers
    'interactive_brokers': {
        'AAPL': 'AAPL',
        'SPY': 'SPY',
        'MTUM': 'MTUM',
        # Direct mapping for most US stocks
    }
}

__all__ = [
    'STOCK_STRATEGIES',
    'STOCK_SYMBOLS',
    'STOCK_BROKER_MAPPING'
]