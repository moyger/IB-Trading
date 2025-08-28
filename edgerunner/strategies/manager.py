"""
Strategy Manager - Strategy Lifecycle Management
===============================================

Manages strategy loading, execution, and monitoring.
"""

import logging
from typing import Dict, Any, List
from .base import BaseStrategy


class StrategyManager:
    """
    Strategy lifecycle management.
    
    Handles strategy loading, starting, stopping, and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Strategy Manager.
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Active strategies
        self.strategies = {}
        self.strategy_configs = config.get('strategies', {})
        
        # Load strategies
        self._load_strategies()
        
    def _load_strategies(self):
        """Load strategy configurations."""
        self.logger.info("Loading strategy configurations...")
        
        for strategy_name, strategy_config in self.strategy_configs.items():
            if strategy_config.get('enabled', False):
                self.logger.info(f"Strategy {strategy_name} is enabled")
                # Strategy instances will be created when started
                
    def start_strategy(self, strategy_name: str) -> bool:
        """
        Start a specific strategy.
        
        Args:
            strategy_name: Name of strategy to start
            
        Returns:
            True if successfully started
        """
        if strategy_name not in self.strategy_configs:
            self.logger.error(f"Strategy {strategy_name} not found in configuration")
            return False
            
        if strategy_name in self.strategies:
            self.logger.warning(f"Strategy {strategy_name} already running")
            return True
            
        try:
            # Create strategy instance (placeholder)
            # In practice, this would instantiate the actual strategy class
            self.strategies[strategy_name] = {
                'config': self.strategy_configs[strategy_name],
                'status': 'running',
                'instance': None  # Placeholder for actual strategy instance
            }
            
            self.logger.info(f"Started strategy: {strategy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start strategy {strategy_name}: {e}")
            return False
    
    def stop_strategy(self, strategy_name: str) -> bool:
        """
        Stop a specific strategy.
        
        Args:
            strategy_name: Name of strategy to stop
            
        Returns:
            True if successfully stopped
        """
        if strategy_name not in self.strategies:
            self.logger.warning(f"Strategy {strategy_name} not running")
            return True
            
        try:
            # Stop strategy instance
            strategy_info = self.strategies[strategy_name]
            strategy_info['status'] = 'stopped'
            
            # Clean up
            del self.strategies[strategy_name]
            
            self.logger.info(f"Stopped strategy: {strategy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop strategy {strategy_name}: {e}")
            return False
    
    def start_all(self):
        """Start all enabled strategies."""
        self.logger.info("Starting all enabled strategies...")
        
        for strategy_name, strategy_config in self.strategy_configs.items():
            if strategy_config.get('enabled', False):
                self.start_strategy(strategy_name)
    
    def stop_all(self):
        """Stop all running strategies."""
        self.logger.info("Stopping all strategies...")
        
        for strategy_name in list(self.strategies.keys()):
            self.stop_strategy(strategy_name)
    
    def status(self) -> Dict[str, Any]:
        """Get strategy manager status."""
        return {
            'configured_strategies': list(self.strategy_configs.keys()),
            'running_strategies': list(self.strategies.keys()),
            'enabled_count': sum(1 for cfg in self.strategy_configs.values() 
                               if cfg.get('enabled', False)),
            'running_count': len(self.strategies)
        }