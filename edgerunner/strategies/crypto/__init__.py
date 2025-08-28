"""
Cryptocurrency Trading Strategies
==================================

Production-ready cryptocurrency strategies with FTMO-style risk management.
"""

# Import strategies (will need to be updated when strategies are adapted)
# from .btcusdt_ftmo_1h_strategy import BTCUSDTStrategy
# from .btcusdt_enhanced_strategy import BTCUSDTEnhancedStrategy  
# from .arthur_hill_trend_strategy import ArthurHillTrendStrategy
# from .multi_confluence_momentum_strategy import MultiConfluenceMomentumStrategy

# Available crypto strategies (placeholder - will be populated after adaptation)
CRYPTO_STRATEGIES = {
    'btcusdt_ftmo_1h': 'BTCUSDTStrategy',
    'btcusdt_enhanced': 'BTCUSDTEnhancedStrategy',
    'arthur_hill_trend': 'ArthurHillTrendStrategy', 
    'multi_confluence': 'MultiConfluenceMomentumStrategy',
}

# Supported crypto symbols
CRYPTO_SYMBOLS = {
    'BTCUSDT': 'Bitcoin vs USDT',
    'ETHUSDT': 'Ethereum vs USDT',
    'ADAUSDT': 'Cardano vs USDT',
    'DOTUSDT': 'Polkadot vs USDT', 
    'LINKUSDT': 'Chainlink vs USDT',
    'SOLUSDT': 'Solana vs USDT',
    'AVAXUSDT': 'Avalanche vs USDT',
    'MATICUSDT': 'Polygon vs USDT',
    'XRPUSDT': 'XRP vs USDT'
}

# Broker mappings for crypto
CRYPTO_BROKER_MAPPING = {
    # Bybit
    'bybit': {
        'BTCUSDT': 'BTCUSDT',
        'ETHUSDT': 'ETHUSDT',
        # Add more mappings
    },
    
    # MT5 (via webhook)
    'mt5': {
        'BTCUSDT': 'BTCUSD',
        'ETHUSDT': 'ETHUSD',
        'XRPUSDT': 'XRPUSD',
        # Add more mappings
    }
}

__all__ = [
    'CRYPTO_STRATEGIES',
    'CRYPTO_SYMBOLS', 
    'CRYPTO_BROKER_MAPPING'
]