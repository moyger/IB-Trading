"""
Universal Strategy Base Class

Professional-grade strategy interface for VectorBT-based backtesting.
Supports crypto, stocks, and forex with built-in risk management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
import vectorbt as vbt
from dataclasses import dataclass
from enum import Enum


class AssetType(Enum):
    """Supported asset types"""
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"


class RiskProfile(Enum):
    """Pre-defined risk profiles"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


@dataclass
class StrategyConfig:
    """Strategy configuration parameters"""
    
    # Basic settings
    name: str
    asset_type: AssetType
    risk_profile: RiskProfile = RiskProfile.MODERATE
    
    # Risk management
    risk_per_trade: float = 0.02  # 2% risk per trade
    max_daily_loss: float = 0.05  # 5% daily loss limit
    max_overall_loss: float = 0.10  # 10% overall loss limit
    max_position_size: float = 0.15  # 15% max position size
    
    # Position sizing
    position_sizing_method: str = 'fixed'  # 'fixed', 'volatility', 'kelly'
    volatility_lookback: int = 20
    kelly_lookback: int = 50
    
    # Transaction costs
    commission: float = 0.001  # 0.1% commission
    slippage: float = 0.0005   # 0.05% slippage
    
    # FTMO compliance (for relevant strategies)
    ftmo_compliant: bool = False
    daily_loss_limit: float = 0.05  # 5% for FTMO
    overall_loss_limit: float = 0.10  # 10% for FTMO
    
    # Strategy-specific parameters (can be extended)
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}
            
        # Apply risk profile defaults
        if self.risk_profile == RiskProfile.CONSERVATIVE:
            self.risk_per_trade = 0.01
            self.max_daily_loss = 0.03
            self.max_position_size = 0.10
        elif self.risk_profile == RiskProfile.AGGRESSIVE:
            self.risk_per_trade = 0.03
            self.max_daily_loss = 0.07
            self.max_position_size = 0.25


class UniversalStrategy(ABC):
    """
    Base class for all trading strategies.
    
    Provides a unified interface for VectorBT-based backtesting with
    professional risk management and multi-asset support.
    """
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.data = None
        self.signals = None
        self.portfolio = None
        
        # Performance tracking
        self.monthly_summaries = []
        self.trade_log = []
        
        # Risk management state
        self.daily_loss_tracker = {}
        self.overall_loss_tracker = 0.0
        self.emergency_stop = False
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from market data.
        
        Args:
            data: OHLCV DataFrame with DatetimeIndex
            
        Returns:
            DataFrame with columns: 'entries', 'exits', 'size'
            - entries: Boolean array for long entry signals
            - exits: Boolean array for exit signals  
            - size: Position size for each signal (optional)
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators needed for the strategy.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            DataFrame with calculated indicators
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data format"""
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        if not all(col in data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in data.columns]
            raise ValueError(f"Missing required columns: {missing}")
            
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have DatetimeIndex")
            
        if data.empty:
            raise ValueError("Data cannot be empty")
            
        return True
    
    def calculate_position_size(self, signal_strength: float = 1.0, 
                              current_price: float = None, 
                              atr: float = None) -> float:
        """
        Calculate position size based on configured method.
        
        Args:
            signal_strength: Strength of the signal (0-1)
            current_price: Current market price
            atr: Average True Range for volatility sizing
            
        Returns:
            Position size as fraction of portfolio
        """
        base_size = self.config.risk_per_trade
        
        if self.config.position_sizing_method == 'fixed':
            return min(base_size * signal_strength, self.config.max_position_size)
            
        elif self.config.position_sizing_method == 'volatility' and atr and current_price:
            # Volatility-adjusted position sizing
            volatility_factor = atr / current_price
            adjusted_size = base_size / (volatility_factor * 10)  # Scale factor
            return min(adjusted_size * signal_strength, self.config.max_position_size)
            
        elif self.config.position_sizing_method == 'kelly':
            # Kelly criterion (simplified - requires historical analysis)
            # This would need win rate and avg win/loss from backtesting
            kelly_fraction = base_size * 1.5  # Placeholder
            return min(kelly_fraction * signal_strength, self.config.max_position_size)
            
        else:
            return min(base_size * signal_strength, self.config.max_position_size)
    
    def apply_risk_management(self, signals: pd.DataFrame, 
                            data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply risk management rules to trading signals.
        
        Args:
            signals: Raw trading signals
            data: Market data
            
        Returns:
            Risk-adjusted signals
        """
        # Copy signals to avoid modifying original
        adjusted_signals = signals.copy()
        
        # Apply daily loss limits
        if self.config.ftmo_compliant:
            adjusted_signals = self._apply_ftmo_limits(adjusted_signals, data)
        
        # Apply position size limits
        if 'size' in adjusted_signals.columns:
            adjusted_signals['size'] = adjusted_signals['size'].clip(
                0, self.config.max_position_size
            )
        
        return adjusted_signals
    
    def _apply_ftmo_limits(self, signals: pd.DataFrame, 
                          data: pd.DataFrame) -> pd.DataFrame:
        """Apply FTMO-specific risk management"""
        # This would implement daily loss tracking and emergency stops
        # Simplified version for now
        return signals
    
    def calculate_monthly_summary(self, portfolio_value: pd.Series, 
                                trades: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Calculate monthly performance summary.
        
        Args:
            portfolio_value: Time series of portfolio values
            trades: DataFrame of executed trades
            
        Returns:
            Dictionary with monthly statistics
        """
        monthly_returns = portfolio_value.resample('M').last().pct_change()
        
        summary = {
            'total_return': (portfolio_value.iloc[-1] / portfolio_value.iloc[0] - 1) * 100,
            'monthly_returns': monthly_returns.dropna() * 100,
            'win_rate': 0.0,
            'total_trades': 0,
            'avg_trade_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0
        }
        
        if trades is not None and not trades.empty:
            summary['total_trades'] = len(trades)
            if 'PnL' in trades.columns:
                summary['win_rate'] = (trades['PnL'] > 0).mean() * 100
                summary['avg_trade_return'] = trades['PnL'].mean()
        
        # Calculate drawdown
        rolling_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value / rolling_max - 1) * 100
        summary['max_drawdown'] = drawdown.min()
        
        # Calculate Sharpe ratio
        if len(monthly_returns) > 1:
            excess_returns = monthly_returns - 0.02/12  # Assume 2% risk-free rate
            summary['sharpe_ratio'] = excess_returns.mean() / excess_returns.std() * np.sqrt(12)
            
            # Sortino ratio (downside deviation)
            negative_returns = excess_returns[excess_returns < 0]
            if len(negative_returns) > 0:
                downside_std = negative_returns.std()
                summary['sortino_ratio'] = excess_returns.mean() / downside_std * np.sqrt(12)
        
        return summary
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy metadata and configuration"""
        return {
            'name': self.config.name,
            'asset_type': self.config.asset_type.value,
            'risk_profile': self.config.risk_profile.value,
            'risk_per_trade': self.config.risk_per_trade,
            'max_daily_loss': self.config.max_daily_loss,
            'ftmo_compliant': self.config.ftmo_compliant,
            'position_sizing': self.config.position_sizing_method,
            'commission': self.config.commission,
            'parameters': self.config.params
        }
    
    def __str__(self) -> str:
        return f"{self.config.name} ({self.config.asset_type.value})"
    
    def __repr__(self) -> str:
        return f"UniversalStrategy(name='{self.config.name}', asset_type='{self.config.asset_type.value}')"