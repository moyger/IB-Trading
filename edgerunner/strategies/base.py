"""Base strategy class."""

class BaseStrategy:
    """Base class for all strategies."""
    def __init__(self, config):
        self.config = config
        
    def generate_signals(self, data):
        """Generate trading signals."""
        raise NotImplementedError