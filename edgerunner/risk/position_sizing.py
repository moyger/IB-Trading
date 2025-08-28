"""Position sizing utilities."""

class PositionSizer:
    """Position sizing with various methods."""
    def __init__(self, config):
        self.config = config
    
    def calculate_size(self, symbol, portfolio_value, signal_strength):
        """Calculate position size."""
        method = self.config.get('method', 'fixed')
        if method == 'fixed':
            return portfolio_value * 0.02  # 2% fixed
        return 1000  # Default

class KellyCalculator:
    """Kelly criterion calculator."""
    pass