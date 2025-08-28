"""
Risk Management System

Professional risk management with FTMO compliance, position sizing,
and portfolio-level risk controls.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

from ..core.universal_strategy import StrategyConfig, RiskProfile


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_daily_loss: float = 0.05
    max_overall_loss: float = 0.10
    max_position_size: float = 0.15
    max_correlation: float = 0.7
    max_sector_exposure: float = 0.3
    var_limit_95: float = 0.05
    var_limit_99: float = 0.10
    max_consecutive_losses: int = 5
    drawdown_stop: float = 0.15


@dataclass 
class RiskState:
    """Current risk state tracking"""
    daily_pnl: Dict[str, float] = field(default_factory=dict)
    overall_pnl: float = 0.0
    consecutive_losses: int = 0
    last_loss_date: Optional[datetime] = None
    emergency_stop: bool = False
    positions: Dict[str, float] = field(default_factory=dict)
    daily_var: float = 0.0
    portfolio_correlation: float = 0.0


class RiskManager:
    """
    Professional risk management system for trading strategies.
    
    Features:
    - Real-time risk monitoring
    - FTMO compliance
    - Portfolio-level limits
    - Dynamic position sizing
    - Emergency stop mechanisms
    """
    
    def __init__(self, risk_limits: Optional[RiskLimits] = None):
        """
        Initialize risk manager.
        
        Args:
            risk_limits: Custom risk limits (optional)
        """
        self.limits = risk_limits or RiskLimits()
        self.state = RiskState()
        self.risk_history = []
        
        # FTMO-specific settings
        self.ftmo_profiles = {
            'challenge': {
                'daily_loss_limit': 0.05,
                'overall_loss_limit': 0.10,
                'profit_target': 0.10,
                'max_position_size': 0.02
            },
            'verification': {
                'daily_loss_limit': 0.05,
                'overall_loss_limit': 0.05,
                'profit_target': 0.05,
                'max_position_size': 0.02
            },
            'funded': {
                'daily_loss_limit': 0.05,
                'overall_loss_limit': 0.12,
                'profit_target': None,
                'max_position_size': 0.02
            }
        }
    
    def apply_risk_rules(self, signals: pd.DataFrame, 
                        market_data: pd.DataFrame,
                        config: StrategyConfig) -> pd.DataFrame:
        """
        Apply risk management rules to trading signals.
        
        Args:
            signals: Raw trading signals with 'entries', 'exits', 'size' columns
            market_data: OHLCV market data
            config: Strategy configuration
            
        Returns:
            Risk-adjusted signals
        """
        # Copy to avoid modifying original
        adjusted_signals = signals.copy()
        
        # Apply FTMO rules if enabled
        if config.ftmo_compliant:
            adjusted_signals = self._apply_ftmo_rules(
                adjusted_signals, market_data, config
            )
        
        # Apply position size limits
        adjusted_signals = self._apply_position_limits(
            adjusted_signals, market_data, config
        )
        
        # Apply daily loss limits
        adjusted_signals = self._apply_daily_limits(
            adjusted_signals, market_data, config
        )
        
        # Apply correlation limits (for multi-asset)
        adjusted_signals = self._apply_correlation_limits(
            adjusted_signals, market_data, config
        )
        
        # Emergency stop check
        if self.state.emergency_stop:
            logging.warning("Emergency stop active - blocking all new positions")
            adjusted_signals['entries'] = False
            adjusted_signals['size'] = 0.0
        
        return adjusted_signals
    
    def _apply_ftmo_rules(self, signals: pd.DataFrame,
                         market_data: pd.DataFrame, 
                         config: StrategyConfig) -> pd.DataFrame:
        """Apply FTMO-specific risk rules"""
        # Determine FTMO phase (would be configured externally)
        ftmo_phase = getattr(config, 'ftmo_phase', 'challenge')
        ftmo_limits = self.ftmo_profiles.get(ftmo_phase, self.ftmo_profiles['challenge'])
        
        # Override config limits with FTMO limits
        max_position = min(config.max_position_size, ftmo_limits['max_position_size'])
        
        # Reduce position sizes for FTMO compliance
        if 'size' in signals.columns:
            signals['size'] = signals['size'].clip(0, max_position)
        
        # Apply buffer for safety (use only 80% of allowed risk)
        safety_factor = 0.8
        if 'size' in signals.columns:
            signals['size'] *= safety_factor
        
        return signals
    
    def _apply_position_limits(self, signals: pd.DataFrame,
                             market_data: pd.DataFrame,
                             config: StrategyConfig) -> pd.DataFrame:
        """Apply position size limits"""
        max_size = config.max_position_size
        
        if 'size' in signals.columns:
            # Clip position sizes to maximum
            signals['size'] = signals['size'].clip(0, max_size)
            
            # Apply volatility adjustment if available
            if 'ATR' in market_data.columns:
                signals = self._apply_volatility_adjustment(
                    signals, market_data, config
                )
        
        return signals
    
    def _apply_volatility_adjustment(self, signals: pd.DataFrame,
                                   market_data: pd.DataFrame,
                                   config: StrategyConfig) -> pd.DataFrame:
        """Adjust position sizes based on volatility"""
        if 'ATR' in market_data.columns and 'Close' in market_data.columns:
            # Calculate volatility factor
            volatility = market_data['ATR'] / market_data['Close']
            
            # Reduce position size in high volatility periods
            volatility_factor = 1.0 / (1.0 + volatility * 10)  # Scaling factor
            
            if 'size' in signals.columns:
                signals['size'] *= volatility_factor.reindex(signals.index, method='ffill')
        
        return signals
    
    def _apply_daily_limits(self, signals: pd.DataFrame,
                          market_data: pd.DataFrame,
                          config: StrategyConfig) -> pd.DataFrame:
        """Apply daily loss limits"""
        # Track daily P&L (simplified implementation)
        current_date = datetime.now().date()
        daily_pnl = self.state.daily_pnl.get(str(current_date), 0.0)
        
        # If daily loss limit exceeded, block new entries
        if daily_pnl <= -config.max_daily_loss:
            logging.warning(f"Daily loss limit exceeded: {daily_pnl:.2%}")
            signals['entries'] = False
            signals['size'] = 0.0
            
            # Trigger emergency stop
            self.state.emergency_stop = True
        
        return signals
    
    def _apply_correlation_limits(self, signals: pd.DataFrame,
                                market_data: pd.DataFrame,
                                config: StrategyConfig) -> pd.DataFrame:
        """Apply correlation limits for multi-asset portfolios"""
        # This would be implemented for multi-asset strategies
        # For now, return signals unchanged
        return signals
    
    def update_pnl(self, symbol: str, pnl: float, timestamp: datetime):
        """
        Update P&L tracking for risk monitoring.
        
        Args:
            symbol: Asset symbol
            pnl: Realized P&L
            timestamp: Trade timestamp
        """
        date_str = timestamp.date().strftime('%Y-%m-%d')
        
        # Update daily P&L
        if date_str not in self.state.daily_pnl:
            self.state.daily_pnl[date_str] = 0.0
        self.state.daily_pnl[date_str] += pnl
        
        # Update overall P&L
        self.state.overall_pnl += pnl
        
        # Track consecutive losses
        if pnl < 0:
            if (self.state.last_loss_date is None or 
                (timestamp.date() - self.state.last_loss_date).days <= 1):
                self.state.consecutive_losses += 1
            else:
                self.state.consecutive_losses = 1
            self.state.last_loss_date = timestamp.date()
        else:
            self.state.consecutive_losses = 0
        
        # Check risk limits
        self._check_risk_limits()
    
    def _check_risk_limits(self):
        """Check if any risk limits have been breached"""
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        daily_pnl = self.state.daily_pnl.get(current_date, 0.0)
        
        # Daily loss limit
        if daily_pnl <= -self.limits.max_daily_loss:
            logging.error(f"Daily loss limit breached: {daily_pnl:.2%}")
            self.state.emergency_stop = True
        
        # Overall loss limit  
        if self.state.overall_pnl <= -self.limits.max_overall_loss:
            logging.error(f"Overall loss limit breached: {self.state.overall_pnl:.2%}")
            self.state.emergency_stop = True
        
        # Consecutive losses
        if self.state.consecutive_losses >= self.limits.max_consecutive_losses:
            logging.warning(f"Too many consecutive losses: {self.state.consecutive_losses}")
            self.state.emergency_stop = True
    
    def reset_daily_limits(self):
        """Reset daily tracking (called at start of each day)"""
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        
        # Reset daily P&L
        self.state.daily_pnl[current_date] = 0.0
        
        # Reset emergency stop if it was due to daily limits
        if self.state.emergency_stop:
            # Check if overall limits still allow trading
            if self.state.overall_pnl > -self.limits.max_overall_loss:
                self.state.emergency_stop = False
                logging.info("Daily limits reset - emergency stop lifted")
    
    def calculate_value_at_risk(self, returns: pd.Series, 
                              confidence_level: float = 0.05) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Series of portfolio returns
            confidence_level: Confidence level (0.05 = 95% VaR)
            
        Returns:
            VaR as a positive number
        """
        if len(returns) < 30:  # Need minimum data
            return 0.0
        
        var = np.percentile(returns, confidence_level * 100)
        return -var  # Return as positive number
    
    def calculate_portfolio_metrics(self, portfolio_value: pd.Series) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        returns = portfolio_value.pct_change().dropna()
        
        if len(returns) < 2:
            return {}
        
        metrics = {
            'volatility': returns.std() * np.sqrt(252),  # Annualized
            'var_95': self.calculate_value_at_risk(returns, 0.05),
            'var_99': self.calculate_value_at_risk(returns, 0.01),
            'max_drawdown': self._calculate_max_drawdown(portfolio_value),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'downside_deviation': self._calculate_downside_deviation(returns)
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, portfolio_value: pd.Series) -> float:
        """Calculate maximum drawdown"""
        rolling_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value / rolling_max - 1)
        return drawdown.min()
    
    def _calculate_downside_deviation(self, returns: pd.Series, 
                                    target_return: float = 0.0) -> float:
        """Calculate downside deviation (semi-standard deviation)"""
        downside_returns = returns[returns < target_return] - target_return
        return np.sqrt((downside_returns ** 2).mean())
    
    def get_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        
        report = {
            'risk_state': {
                'emergency_stop': self.state.emergency_stop,
                'daily_pnl': self.state.daily_pnl.get(current_date, 0.0),
                'overall_pnl': self.state.overall_pnl,
                'consecutive_losses': self.state.consecutive_losses
            },
            'risk_limits': {
                'max_daily_loss': self.limits.max_daily_loss,
                'max_overall_loss': self.limits.max_overall_loss,
                'max_position_size': self.limits.max_position_size,
                'drawdown_stop': self.limits.drawdown_stop
            },
            'utilization': {
                'daily_loss_used': abs(self.state.daily_pnl.get(current_date, 0.0)) / self.limits.max_daily_loss,
                'overall_loss_used': abs(self.state.overall_pnl) / self.limits.max_overall_loss,
            },
            'warnings': self._generate_warnings(),
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def _generate_warnings(self) -> List[str]:
        """Generate risk warnings"""
        warnings = []
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        daily_pnl = self.state.daily_pnl.get(current_date, 0.0)
        
        # Daily loss warnings
        daily_usage = abs(daily_pnl) / self.limits.max_daily_loss
        if daily_usage > 0.8:
            warnings.append(f"Daily loss limit usage high: {daily_usage:.1%}")
        
        # Overall loss warnings
        overall_usage = abs(self.state.overall_pnl) / self.limits.max_overall_loss
        if overall_usage > 0.8:
            warnings.append(f"Overall loss limit usage high: {overall_usage:.1%}")
        
        # Consecutive losses
        if self.state.consecutive_losses >= 3:
            warnings.append(f"Consecutive losses: {self.state.consecutive_losses}")
        
        return warnings
    
    def set_ftmo_mode(self, phase: str, account_size: float = 100000):
        """
        Configure for FTMO challenge/verification/funded account.
        
        Args:
            phase: 'challenge', 'verification', or 'funded'
            account_size: Account size for calculating absolute limits
        """
        if phase not in self.ftmo_profiles:
            raise ValueError(f"Unknown FTMO phase: {phase}")
        
        profile = self.ftmo_profiles[phase]
        
        # Update limits based on FTMO profile
        self.limits.max_daily_loss = profile['daily_loss_limit']
        self.limits.max_overall_loss = profile['overall_loss_limit']
        self.limits.max_position_size = profile['max_position_size']
        
        logging.info(f"FTMO mode set to {phase} with account size ${account_size:,.0f}")
    
    def simulate_risk_scenario(self, scenario_returns: pd.Series) -> Dict[str, float]:
        """
        Simulate risk metrics under stress scenario.
        
        Args:
            scenario_returns: Returns series for stress testing
            
        Returns:
            Dictionary of stress test results
        """
        scenario_results = {
            'worst_day_loss': scenario_returns.min(),
            'worst_week_loss': scenario_returns.rolling(5).sum().min(),
            'worst_month_loss': scenario_returns.rolling(21).sum().min(),
            'var_95_stress': self.calculate_value_at_risk(scenario_returns, 0.05),
            'var_99_stress': self.calculate_value_at_risk(scenario_returns, 0.01),
            'expected_shortfall': scenario_returns[scenario_returns <= scenario_returns.quantile(0.05)].mean()
        }
        
        return scenario_results