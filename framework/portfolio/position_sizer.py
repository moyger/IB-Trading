"""
Position Sizing System

Advanced position sizing methods including fixed, volatility-based,
Kelly criterion, and risk parity approaches.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

from ..core.universal_strategy import StrategyConfig


@dataclass
class PositionSizeResult:
    """Result of position size calculation"""
    size: float
    confidence: float
    method: str
    risk_adjusted: bool
    metadata: Dict[str, Any] = None


class PositionSizer(ABC):
    """Abstract base class for position sizing methods"""
    
    @abstractmethod
    def calculate_size(self, signal_strength: float,
                      market_data: pd.DataFrame,
                      portfolio_value: float,
                      config: StrategyConfig) -> PositionSizeResult:
        """Calculate position size"""
        pass


class FixedPositionSizer(PositionSizer):
    """Fixed percentage position sizing"""
    
    def __init__(self, base_size: float = 0.02):
        self.base_size = base_size
    
    def calculate_size(self, signal_strength: float,
                      market_data: pd.DataFrame,
                      portfolio_value: float,
                      config: StrategyConfig) -> PositionSizeResult:
        """Calculate fixed position size"""
        size = self.base_size * signal_strength
        size = min(size, config.max_position_size)
        
        return PositionSizeResult(
            size=size,
            confidence=0.8,  # Fixed confidence
            method='fixed',
            risk_adjusted=False,
            metadata={'base_size': self.base_size}
        )


class VolatilityPositionSizer(PositionSizer):
    """Volatility-adjusted position sizing using ATR"""
    
    def __init__(self, base_size: float = 0.02, 
                 volatility_lookback: int = 20,
                 target_volatility: float = 0.02):
        self.base_size = base_size
        self.volatility_lookback = volatility_lookback
        self.target_volatility = target_volatility
    
    def calculate_size(self, signal_strength: float,
                      market_data: pd.DataFrame,
                      portfolio_value: float,
                      config: StrategyConfig) -> PositionSizeResult:
        """Calculate volatility-adjusted position size"""
        
        # Calculate ATR if not provided
        if 'ATR' not in market_data.columns:
            market_data = self._calculate_atr(market_data)
        
        if len(market_data) < self.volatility_lookback:
            # Fallback to fixed sizing
            size = self.base_size * signal_strength
            confidence = 0.5
        else:
            # Get current ATR and price
            current_atr = market_data['ATR'].iloc[-1]
            current_price = market_data['Close'].iloc[-1]
            
            # Calculate position volatility
            position_volatility = current_atr / current_price
            
            # Adjust size based on volatility
            volatility_multiplier = self.target_volatility / position_volatility
            size = self.base_size * volatility_multiplier * signal_strength
            
            # Higher confidence for volatility-adjusted sizing
            confidence = 0.85
        
        # Apply maximum position size limit
        size = min(size, config.max_position_size)
        
        return PositionSizeResult(
            size=size,
            confidence=confidence,
            method='volatility',
            risk_adjusted=True,
            metadata={
                'atr': current_atr if 'current_atr' in locals() else None,
                'volatility': position_volatility if 'position_volatility' in locals() else None,
                'target_volatility': self.target_volatility
            }
        )
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        high = data['High']
        low = data['Low']
        close = data['Close'].shift(1)
        
        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        data = data.copy()
        data['ATR'] = atr
        return data


class KellyPositionSizer(PositionSizer):
    """Kelly Criterion position sizing"""
    
    def __init__(self, lookback_period: int = 50,
                 kelly_fraction: float = 0.25):
        self.lookback_period = lookback_period
        self.kelly_fraction = kelly_fraction  # Fraction of full Kelly to use
    
    def calculate_size(self, signal_strength: float,
                      market_data: pd.DataFrame,
                      portfolio_value: float,
                      config: StrategyConfig) -> PositionSizeResult:
        """Calculate Kelly criterion position size"""
        
        if len(market_data) < self.lookback_period:
            # Fallback to fixed sizing
            size = config.risk_per_trade * signal_strength
            confidence = 0.5
            kelly_size = None
        else:
            # Calculate historical returns for Kelly estimation
            returns = market_data['Close'].pct_change().dropna()
            recent_returns = returns.tail(self.lookback_period)
            
            # Estimate win rate and average win/loss
            positive_returns = recent_returns[recent_returns > 0]
            negative_returns = recent_returns[recent_returns <= 0]
            
            if len(positive_returns) == 0 or len(negative_returns) == 0:
                # No clear pattern, use fixed sizing
                size = config.risk_per_trade * signal_strength
                confidence = 0.5
                kelly_size = None
            else:
                win_rate = len(positive_returns) / len(recent_returns)
                avg_win = positive_returns.mean()
                avg_loss = abs(negative_returns.mean())
                
                # Kelly formula: f = (bp - q) / b
                # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
                if avg_loss > 0:
                    b = avg_win / avg_loss
                    p = win_rate
                    q = 1 - win_rate
                    
                    kelly_size = (b * p - q) / b
                    kelly_size = max(0, kelly_size)  # Don't go negative
                    
                    # Apply fractional Kelly for safety
                    size = kelly_size * self.kelly_fraction * signal_strength
                    confidence = 0.9
                else:
                    size = config.risk_per_trade * signal_strength
                    confidence = 0.5
                    kelly_size = None
        
        # Apply maximum position size limit
        size = min(size, config.max_position_size)
        
        return PositionSizeResult(
            size=size,
            confidence=confidence,
            method='kelly',
            risk_adjusted=True,
            metadata={
                'kelly_size': kelly_size,
                'kelly_fraction': self.kelly_fraction,
                'lookback_period': self.lookback_period,
                'win_rate': win_rate if 'win_rate' in locals() else None,
                'avg_win': avg_win if 'avg_win' in locals() else None,
                'avg_loss': avg_loss if 'avg_loss' in locals() else None
            }
        )


class RiskParityPositionSizer(PositionSizer):
    """Risk parity position sizing for multi-asset portfolios"""
    
    def __init__(self, risk_budget: float = 0.02,
                 volatility_lookback: int = 30):
        self.risk_budget = risk_budget
        self.volatility_lookback = volatility_lookback
    
    def calculate_size(self, signal_strength: float,
                      market_data: pd.DataFrame,
                      portfolio_value: float,
                      config: StrategyConfig) -> PositionSizeResult:
        """Calculate risk parity position size"""
        
        if len(market_data) < self.volatility_lookback:
            # Fallback to fixed sizing
            size = config.risk_per_trade * signal_strength
            confidence = 0.6
            volatility = None
        else:
            # Calculate historical volatility
            returns = market_data['Close'].pct_change().dropna()
            volatility = returns.tail(self.volatility_lookback).std()
            
            if volatility == 0:
                size = config.risk_per_trade * signal_strength
                confidence = 0.6
            else:
                # Risk parity: allocate based on inverse volatility
                target_risk = self.risk_budget * signal_strength
                size = target_risk / volatility
                confidence = 0.85
        
        # Apply maximum position size limit
        size = min(size, config.max_position_size)
        
        return PositionSizeResult(
            size=size,
            confidence=confidence,
            method='risk_parity',
            risk_adjusted=True,
            metadata={
                'volatility': volatility,
                'risk_budget': self.risk_budget,
                'target_risk': target_risk if 'target_risk' in locals() else None
            }
        )


class AdaptivePositionSizer(PositionSizer):
    """Adaptive position sizing that switches between methods"""
    
    def __init__(self):
        self.sizers = {
            'fixed': FixedPositionSizer(),
            'volatility': VolatilityPositionSizer(),
            'kelly': KellyPositionSizer(),
            'risk_parity': RiskParityPositionSizer()
        }
        self.method_scores = {method: 0.5 for method in self.sizers.keys()}
    
    def calculate_size(self, signal_strength: float,
                      market_data: pd.DataFrame,
                      portfolio_value: float,
                      config: StrategyConfig) -> PositionSizeResult:
        """Calculate adaptive position size"""
        
        # Calculate size using all methods
        results = {}
        for method, sizer in self.sizers.items():
            try:
                result = sizer.calculate_size(
                    signal_strength, market_data, portfolio_value, config
                )
                results[method] = result
            except Exception as e:
                logging.warning(f"Error in {method} sizing: {str(e)}")
                continue
        
        if not results:
            # Fallback to fixed sizing
            return FixedPositionSizer().calculate_size(
                signal_strength, market_data, portfolio_value, config
            )
        
        # Select best method based on confidence and current scores
        best_method = max(results.keys(), 
                         key=lambda m: results[m].confidence * self.method_scores[m])
        
        best_result = results[best_method]
        
        # Update metadata to include all method results
        best_result.metadata = best_result.metadata or {}
        best_result.metadata['all_results'] = {
            method: {'size': result.size, 'confidence': result.confidence}
            for method, result in results.items()
        }
        best_result.metadata['selected_method'] = best_method
        
        return best_result
    
    def update_performance(self, method: str, performance: float):
        """Update method performance scores"""
        if method in self.method_scores:
            # Exponential moving average update
            alpha = 0.1
            self.method_scores[method] = (
                alpha * performance + (1 - alpha) * self.method_scores[method]
            )


class PositionSizingManager:
    """Manager class for position sizing operations"""
    
    def __init__(self, default_method: str = 'volatility'):
        self.sizers = {
            'fixed': FixedPositionSizer(),
            'volatility': VolatilityPositionSizer(),
            'kelly': KellyPositionSizer(),
            'risk_parity': RiskParityPositionSizer(),
            'adaptive': AdaptivePositionSizer()
        }
        self.default_method = default_method
        self.sizing_history = []
    
    def calculate_position_size(self, signal_strength: float,
                              market_data: pd.DataFrame,
                              portfolio_value: float,
                              config: StrategyConfig,
                              method: Optional[str] = None) -> PositionSizeResult:
        """
        Calculate position size using specified method.
        
        Args:
            signal_strength: Signal strength (0-1)
            market_data: Market data DataFrame
            portfolio_value: Current portfolio value
            config: Strategy configuration
            method: Position sizing method to use
            
        Returns:
            Position size result
        """
        method = method or config.position_sizing_method or self.default_method
        
        if method not in self.sizers:
            logging.warning(f"Unknown sizing method {method}, using {self.default_method}")
            method = self.default_method
        
        sizer = self.sizers[method]
        result = sizer.calculate_size(signal_strength, market_data, portfolio_value, config)
        
        # Store in history
        self.sizing_history.append({
            'timestamp': pd.Timestamp.now(),
            'method': method,
            'signal_strength': signal_strength,
            'size': result.size,
            'confidence': result.confidence
        })
        
        return result
    
    def get_sizing_statistics(self) -> Dict[str, Any]:
        """Get position sizing statistics"""
        if not self.sizing_history:
            return {}
        
        df = pd.DataFrame(self.sizing_history)
        
        stats = {
            'total_calculations': len(df),
            'methods_used': df['method'].value_counts().to_dict(),
            'avg_size_by_method': df.groupby('method')['size'].mean().to_dict(),
            'avg_confidence_by_method': df.groupby('method')['confidence'].mean().to_dict(),
            'size_distribution': {
                'min': df['size'].min(),
                'max': df['size'].max(),
                'mean': df['size'].mean(),
                'std': df['size'].std()
            }
        }
        
        return stats
    
    def configure_method(self, method: str, **kwargs):
        """Configure parameters for specific sizing method"""
        if method not in self.sizers:
            raise ValueError(f"Unknown method: {method}")
        
        # Update sizer parameters
        sizer = self.sizers[method]
        for param, value in kwargs.items():
            if hasattr(sizer, param):
                setattr(sizer, param, value)
            else:
                logging.warning(f"Unknown parameter {param} for method {method}")
    
    def compare_methods(self, signal_strength: float,
                       market_data: pd.DataFrame,
                       portfolio_value: float,
                       config: StrategyConfig) -> Dict[str, PositionSizeResult]:
        """Compare all position sizing methods"""
        results = {}
        
        for method, sizer in self.sizers.items():
            try:
                result = sizer.calculate_size(
                    signal_strength, market_data, portfolio_value, config
                )
                results[method] = result
            except Exception as e:
                logging.warning(f"Error comparing {method}: {str(e)}")
                continue
        
        return results