"""
Performance Analysis System - Updated

Professional-grade performance analytics with industry-standard metrics,
risk analysis, and benchmarking capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class PerformanceAnalyzer:
    """
    Comprehensive performance analysis for trading strategies.
    
    Calculates industry-standard metrics used by hedge funds and
    institutional investors for strategy evaluation.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize performance analyzer.
        
        Args:
            risk_free_rate: Annual risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
        
    def analyze_portfolio(self, portfolio_value: pd.Series, 
                         trades: Optional[pd.DataFrame] = None,
                         benchmark_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Comprehensive portfolio performance analysis.
        
        Args:
            portfolio_value: Portfolio value time series
            trades: Trade records DataFrame (optional)
            benchmark_data: Benchmark price data for comparison
            
        Returns:
            Dictionary with comprehensive performance metrics
        """
        # Calculate returns
        returns = portfolio_value.pct_change().dropna()
        
        # Calculate all performance metrics
        performance = {
            # Return Metrics
            'total_return': self._calculate_total_return(portfolio_value),
            'annualized_return': self._calculate_annualized_return(portfolio_value),
            'cagr': self._calculate_cagr(portfolio_value),
            
            # Risk Metrics
            'volatility': self._calculate_volatility(returns),
            'max_drawdown': self._calculate_max_drawdown(portfolio_value),
            'var_95': self._calculate_var(returns, 0.05),
            'var_99': self._calculate_var(returns, 0.01),
            'expected_shortfall_95': self._calculate_expected_shortfall(returns, 0.05),
            'downside_deviation': self._calculate_downside_deviation(returns),
            
            # Risk-Adjusted Metrics
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'calmar_ratio': self._calculate_calmar_ratio(portfolio_value),
            'omega_ratio': self._calculate_omega_ratio(returns),
            'information_ratio': 0.0,  # Calculated later if benchmark provided
            
            # Trade Metrics (if trades provided)
            'win_rate': self._calculate_win_rate_from_trades(trades) if trades is not None else 0.0,
            'profit_factor': self._calculate_profit_factor_from_trades(trades) if trades is not None else 0.0,
            'avg_trade_return': self._calculate_avg_trade_from_trades(trades) if trades is not None else 0.0,
            'best_trade': self._calculate_best_trade_from_trades(trades) if trades is not None else 0.0,
            'worst_trade': self._calculate_worst_trade_from_trades(trades) if trades is not None else 0.0,
            'avg_trade_duration': self._calculate_avg_duration_from_trades(trades) if trades is not None else 0.0,
            'total_trades': len(trades) if trades is not None else 0,
            
            # Distribution Metrics
            'skewness': returns.skew() if len(returns) > 0 else 0.0,
            'kurtosis': returns.kurtosis() if len(returns) > 0 else 0.0,
            'tail_ratio': self._calculate_tail_ratio(returns),
            
            # Consistency Metrics
            'monthly_win_rate': self._calculate_monthly_win_rate(portfolio_value),
            'max_consecutive_wins': 0,  # Would calculate from trades
            'max_consecutive_losses': 0,  # Would calculate from trades
            'recovery_factor': self._calculate_recovery_factor(portfolio_value),
            
            # Performance Attribution
            'long_trade_ratio': 50.0,  # Placeholder
            'short_trade_ratio': 50.0,  # Placeholder
            'avg_win_size': 0.0,  # Would calculate from trades
            'avg_loss_size': 0.0,  # Would calculate from trades
        }
        
        # Benchmark comparison if provided
        if benchmark_data is not None:
            benchmark_metrics = self._calculate_benchmark_metrics(
                portfolio_value, benchmark_data
            )
            performance.update(benchmark_metrics)
        
        return performance
    
    # Return Metrics
    def _calculate_total_return(self, portfolio_value: pd.Series) -> float:
        """Calculate total return percentage"""
        if len(portfolio_value) == 0:
            return 0.0
        return (portfolio_value.iloc[-1] / portfolio_value.iloc[0] - 1) * 100
    
    def _calculate_annualized_return(self, portfolio_value: pd.Series) -> float:
        """Calculate annualized return"""
        if len(portfolio_value) < 2:
            return 0.0
        
        days = (portfolio_value.index[-1] - portfolio_value.index[0]).days
        if days == 0:
            return 0.0
        
        total_return = portfolio_value.iloc[-1] / portfolio_value.iloc[0]
        years = days / 365.25
        return (total_return ** (1/years) - 1) * 100 if years > 0 else 0.0
    
    def _calculate_cagr(self, portfolio_value: pd.Series) -> float:
        """Calculate Compound Annual Growth Rate"""
        return self._calculate_annualized_return(portfolio_value)
    
    # Risk Metrics
    def _calculate_volatility(self, returns: pd.Series) -> float:
        """Calculate annualized volatility"""
        if len(returns) < 2:
            return 0.0
        return returns.std() * np.sqrt(252) * 100  # Assuming daily returns
    
    def _calculate_max_drawdown(self, portfolio_value: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(portfolio_value) == 0:
            return 0.0
        
        rolling_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value / rolling_max - 1) * 100
        return drawdown.min()
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        if len(returns) < 30:  # Need minimum observations
            return 0.0
        return -np.percentile(returns, confidence_level * 100) * 100
    
    def _calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        if len(returns) < 30:
            return 0.0
        var_threshold = np.percentile(returns, confidence_level * 100)
        tail_returns = returns[returns <= var_threshold]
        return -tail_returns.mean() * 100 if len(tail_returns) > 0 else 0.0
    
    def _calculate_downside_deviation(self, returns: pd.Series) -> float:
        """Calculate downside deviation"""
        if len(returns) == 0:
            return 0.0
        downside_returns = returns[returns < 0]
        return downside_returns.std() * np.sqrt(252) * 100 if len(downside_returns) > 0 else 0.0
    
    # Risk-Adjusted Metrics
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0.0
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if excess_returns.mean() > 0 else 0.0
        
        downside_std = downside_returns.std()
        return excess_returns.mean() / downside_std * np.sqrt(252) if downside_std != 0 else 0.0
    
    def _calculate_calmar_ratio(self, portfolio_value: pd.Series) -> float:
        """Calculate Calmar ratio (CAGR / Max Drawdown)"""
        cagr = self._calculate_cagr(portfolio_value)
        max_dd = abs(self._calculate_max_drawdown(portfolio_value))
        return cagr / max_dd if max_dd != 0 else 0.0
    
    def _calculate_omega_ratio(self, returns: pd.Series, threshold: float = 0.0) -> float:
        """Calculate Omega ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - threshold
        positive_returns = excess_returns[excess_returns > 0].sum()
        negative_returns = abs(excess_returns[excess_returns <= 0].sum())
        
        return positive_returns / negative_returns if negative_returns != 0 else float('inf')
    
    # Trade-based metrics
    def _calculate_win_rate_from_trades(self, trades: pd.DataFrame) -> float:
        """Calculate win rate from trades DataFrame"""
        if trades is None or len(trades) == 0:
            return 0.0
        
        if 'PnL' in trades.columns:
            winning_trades = (trades['PnL'] > 0).sum()
            return winning_trades / len(trades) * 100
        return 0.0
    
    def _calculate_profit_factor_from_trades(self, trades: pd.DataFrame) -> float:
        """Calculate profit factor from trades"""
        if trades is None or len(trades) == 0 or 'PnL' not in trades.columns:
            return 0.0
        
        winning_trades = trades['PnL'][trades['PnL'] > 0]
        losing_trades = trades['PnL'][trades['PnL'] <= 0]
        
        gross_profit = winning_trades.sum()
        gross_loss = abs(losing_trades.sum())
        
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')
    
    def _calculate_avg_trade_from_trades(self, trades: pd.DataFrame) -> float:
        """Calculate average trade return"""
        if trades is None or len(trades) == 0 or 'PnL' not in trades.columns:
            return 0.0
        
        return trades['PnL'].mean() * 100
    
    def _calculate_best_trade_from_trades(self, trades: pd.DataFrame) -> float:
        """Calculate best trade return"""
        if trades is None or len(trades) == 0 or 'PnL' not in trades.columns:
            return 0.0
        
        return trades['PnL'].max() * 100
    
    def _calculate_worst_trade_from_trades(self, trades: pd.DataFrame) -> float:
        """Calculate worst trade return"""
        if trades is None or len(trades) == 0 or 'PnL' not in trades.columns:
            return 0.0
        
        return trades['PnL'].min() * 100
    
    def _calculate_avg_duration_from_trades(self, trades: pd.DataFrame) -> float:
        """Calculate average trade duration"""
        if trades is None or len(trades) == 0:
            return 0.0
        
        if 'Duration' in trades.columns:
            return trades['Duration'].mean()
        return 0.0
    
    # Distribution Metrics
    def _calculate_tail_ratio(self, returns: pd.Series) -> float:
        """Calculate tail ratio (95th percentile / 5th percentile)"""
        if len(returns) < 20:
            return 0.0
        
        percentile_95 = np.percentile(returns, 95)
        percentile_5 = np.percentile(returns, 5)
        
        return abs(percentile_95 / percentile_5) if percentile_5 != 0 else 0.0
    
    # Consistency Metrics
    def _calculate_monthly_win_rate(self, portfolio_value: pd.Series) -> float:
        """Calculate monthly win rate"""
        if len(portfolio_value) < 30:
            return 0.0
        
        monthly_returns = portfolio_value.resample('M').last().pct_change().dropna()
        if len(monthly_returns) == 0:
            return 0.0
        
        positive_months = (monthly_returns > 0).sum()
        return positive_months / len(monthly_returns) * 100
    
    def _calculate_recovery_factor(self, portfolio_value: pd.Series) -> float:
        """Calculate recovery factor (Net Profit / Max Drawdown)"""
        if len(portfolio_value) < 2:
            return 0.0
        
        net_profit = portfolio_value.iloc[-1] - portfolio_value.iloc[0]
        max_dd = abs(self._calculate_max_drawdown(portfolio_value))
        
        return (net_profit / portfolio_value.iloc[0] * 100) / max_dd if max_dd != 0 else 0.0
    
    def _calculate_benchmark_metrics(self, portfolio_value: pd.Series, 
                                   benchmark_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate benchmark comparison metrics"""
        try:
            # Align portfolio and benchmark data
            benchmark_prices = benchmark_data['Close'].reindex(portfolio_value.index, method='ffill')
            
            # Calculate benchmark returns
            benchmark_returns = benchmark_prices.pct_change().dropna()
            portfolio_returns = portfolio_value.pct_change().dropna()
            
            # Align returns
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) < 30:  # Need minimum data
                return {'information_ratio': 0.0, 'beta': 0.0, 'alpha': 0.0, 'correlation': 0.0}
            
            port_aligned = portfolio_returns.reindex(common_dates)
            bench_aligned = benchmark_returns.reindex(common_dates)
            
            # Calculate metrics
            excess_returns = port_aligned - bench_aligned
            information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0.0
            
            # Beta and Alpha
            covariance = np.cov(port_aligned, bench_aligned)[0, 1]
            variance = np.var(bench_aligned)
            beta = covariance / variance if variance != 0 else 0.0
            
            alpha = (port_aligned.mean() - beta * bench_aligned.mean()) * 252 * 100  # Annualized alpha
            
            # Correlation
            correlation = np.corrcoef(port_aligned, bench_aligned)[0, 1] if len(port_aligned) > 1 else 0.0
            
            return {
                'information_ratio': information_ratio,
                'beta': beta,
                'alpha': alpha,
                'correlation': correlation
            }
        
        except Exception as e:
            logging.warning(f"Error calculating benchmark metrics: {str(e)}")
            return {'information_ratio': 0.0, 'beta': 0.0, 'alpha': 0.0, 'correlation': 0.0}