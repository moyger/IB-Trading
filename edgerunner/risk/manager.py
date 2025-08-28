"""
Risk Manager - Portfolio Risk Management
========================================

Comprehensive risk management with position sizing, exposure limits, and risk guards.
"""

import logging
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd


class RiskManager:
    """
    Main risk management engine.
    
    Handles position sizing, portfolio risk, and exposure management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Risk Manager.
        
        Args:
            config: Risk management configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load risk parameters
        self.position_sizing_config = config.get('position_sizing', {})
        self.risk_limits = config.get('risk_limits', {})
        self.metrics_config = config.get('metrics', {})
        
        # Current portfolio state
        self.positions = {}
        self.portfolio_value = 0.0
        self.daily_pnl = 0.0
        
        # Risk calculators
        from .position_sizing import PositionSizer
        from .metrics import RiskMetrics
        
        self.position_sizer = PositionSizer(self.position_sizing_config)
        self.risk_metrics = RiskMetrics(self.metrics_config)
        
        self.logger.info("Risk Manager initialized")
        
    def calculate_position_size(self, symbol: str, signal_strength: float, 
                              current_price: float = None) -> float:
        """
        Calculate position size for a trade.
        
        Args:
            symbol: Trading symbol
            signal_strength: Signal strength (-1 to 1)
            current_price: Current market price
            
        Returns:
            Position size in base currency
        """
        # Get portfolio metrics
        portfolio_value = self.get_portfolio_value()
        
        # Calculate base position size
        base_size = self.position_sizer.calculate_size(
            symbol=symbol,
            portfolio_value=portfolio_value,
            signal_strength=signal_strength
        )
        
        # Apply risk limits
        max_position = self.risk_limits.get('max_single_position', 0.05) * portfolio_value
        position_size = min(base_size, max_position)
        
        # Check daily loss limits
        if self._exceeds_daily_limits(position_size):
            self.logger.warning(f"Position size reduced due to daily limits: {symbol}")
            position_size = 0.0
            
        self.logger.debug(f"Position size for {symbol}: ${position_size:,.2f}")
        return position_size
    
    def check_risk_limits(self, symbol: str, trade_size: float) -> bool:
        """
        Check if trade passes risk limits.
        
        Args:
            symbol: Trading symbol
            trade_size: Proposed trade size
            
        Returns:
            True if trade passes risk checks
        """
        # Check portfolio exposure
        if not self._check_portfolio_exposure(trade_size):
            return False
            
        # Check position limits
        if not self._check_position_limits(symbol, trade_size):
            return False
            
        # Check correlation limits
        if not self._check_correlation_limits(symbol):
            return False
            
        # Check daily loss limits
        if self._exceeds_daily_limits(trade_size):
            return False
            
        return True
    
    def update_positions(self, positions: Dict[str, Any]):
        """Update current portfolio positions."""
        self.positions = positions
        self.portfolio_value = sum(pos.get('market_value', 0) for pos in positions.values())
        
    def get_portfolio_value(self) -> float:
        """Get current portfolio value."""
        return self.portfolio_value if self.portfolio_value > 0 else 100000  # Default
    
    def _check_portfolio_exposure(self, trade_size: float) -> bool:
        """Check if trade exceeds portfolio exposure limits."""
        max_exposure = self.risk_limits.get('max_portfolio_risk', 0.20)
        current_exposure = self._calculate_portfolio_exposure()
        
        return (current_exposure + trade_size / self.get_portfolio_value()) <= max_exposure
    
    def _check_position_limits(self, symbol: str, trade_size: float) -> bool:
        """Check position size limits."""
        max_position = self.risk_limits.get('max_single_position', 0.05)
        position_ratio = trade_size / self.get_portfolio_value()
        
        return position_ratio <= max_position
    
    def _check_correlation_limits(self, symbol: str) -> bool:
        """Check correlation limits (placeholder)."""
        # This would implement actual correlation checking
        return True
    
    def _exceeds_daily_limits(self, trade_size: float) -> bool:
        """Check if trade would exceed daily loss limits."""
        max_daily_loss = self.risk_limits.get('max_daily_loss', 0.03)
        max_loss_amount = max_daily_loss * self.get_portfolio_value()
        
        return abs(self.daily_pnl) + trade_size > max_loss_amount
    
    def _calculate_portfolio_exposure(self) -> float:
        """Calculate current portfolio exposure."""
        if not self.positions:
            return 0.0
            
        total_exposure = sum(
            abs(pos.get('market_value', 0)) for pos in self.positions.values()
        )
        
        return total_exposure / self.get_portfolio_value()
    
    def status(self) -> Dict[str, Any]:
        """Get risk manager status."""
        return {
            'portfolio_value': self.portfolio_value,
            'daily_pnl': self.daily_pnl,
            'positions_count': len(self.positions),
            'portfolio_exposure': self._calculate_portfolio_exposure(),
            'risk_limits': self.risk_limits
        }