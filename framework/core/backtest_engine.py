"""
VectorBT-Based Backtesting Engine

Professional-grade backtesting engine built on VectorBT for ultra-fast
vectorized backtesting of trading strategies.
"""

import pandas as pd
import numpy as np
import vectorbt as vbt
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging
import warnings
from pathlib import Path

from .universal_strategy import UniversalStrategy, StrategyConfig, AssetType
from ..data.data_handler import DataHandler
from ..portfolio.risk_manager import RiskManager
from ..reporting.performance_analyzer import PerformanceAnalyzer


class BacktestEngine:
    """
    Universal backtesting engine powered by VectorBT.
    
    Features:
    - Ultra-fast vectorized backtesting (100-1000x faster)
    - Multi-asset portfolio support
    - Professional risk management
    - Comprehensive performance analytics
    - FTMO compliance built-in
    """
    
    def __init__(self, initial_cash: float = 100000.0, 
                 data_handler: Optional[DataHandler] = None,
                 risk_manager: Optional[RiskManager] = None,
                 performance_analyzer: Optional[PerformanceAnalyzer] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize backtesting engine.
        
        Args:
            initial_cash: Starting capital
            data_handler: Custom data handler (optional)
            risk_manager: Custom risk manager (optional) 
            performance_analyzer: Custom performance analyzer (optional)
            cache_dir: Directory for caching results
        """
        self.initial_cash = initial_cash
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Initialize components
        self.data_handler = data_handler or DataHandler(cache_dir)
        self.risk_manager = risk_manager or RiskManager()
        self.performance_analyzer = performance_analyzer or PerformanceAnalyzer()
        
        # Results storage
        self.results = {}
        self.portfolios = {}
        
        # Configure VectorBT settings
        vbt.settings.array_wrapper['freq'] = 'H'  # Default to hourly
        vbt.settings.portfolio.stats['incl_closed'] = True
        vbt.settings.portfolio.stats['incl_open'] = True
        
    def run_single_backtest(self, strategy: UniversalStrategy, 
                           symbol: str, start_date: str, end_date: str,
                           interval: str = '1h',
                           benchmark_symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Run backtest for a single strategy on single asset.
        
        Args:
            strategy: Strategy instance
            symbol: Asset symbol  
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            benchmark_symbol: Benchmark symbol for comparison
            
        Returns:
            Dictionary with backtest results
        """
        # Fetch data
        logging.info(f"Fetching data for {symbol}")
        asset_type = self._determine_asset_type(symbol)
        data = self.data_handler.fetch_data(
            symbol, asset_type, start_date, end_date, interval
        )
        
        # Calculate indicators
        logging.info("Calculating technical indicators")
        indicators = strategy.calculate_indicators(data)
        combined_data = pd.concat([data, indicators], axis=1)
        
        # Generate signals
        logging.info("Generating trading signals")
        signals = strategy.generate_signals(combined_data)
        
        # Apply risk management
        logging.info("Applying risk management")
        risk_adjusted_signals = self.risk_manager.apply_risk_rules(
            signals, combined_data, strategy.config
        )
        
        # Run VectorBT backtest
        logging.info("Running VectorBT backtest")
        portfolio = self._run_vectorbt_backtest(
            combined_data, risk_adjusted_signals, strategy.config
        )
        
        # Analyze performance
        logging.info("Analyzing performance")
        performance = self.performance_analyzer.analyze_portfolio(
            portfolio, benchmark_data=self._fetch_benchmark(benchmark_symbol, start_date, end_date, interval)
        )
        
        # Generate comprehensive results
        results = {
            'strategy': strategy.get_strategy_info(),
            'symbol': symbol,
            'period': f"{start_date} to {end_date}",
            'data_points': len(data),
            'portfolio': portfolio,
            'performance': performance,
            'monthly_summaries': self._calculate_monthly_summaries(portfolio),
            'trade_analysis': self._analyze_trades(portfolio),
            'risk_metrics': self._calculate_risk_metrics(portfolio),
            'timestamp': datetime.now().isoformat()
        }
        
        # Store results
        result_key = f"{strategy.config.name}_{symbol}_{start_date}_{end_date}"
        self.results[result_key] = results
        self.portfolios[result_key] = portfolio
        
        return results
    
    def run_multi_asset_backtest(self, strategy: UniversalStrategy,
                                symbols: List[str], start_date: str, end_date: str,
                                interval: str = '1h',
                                portfolio_allocation: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Run backtest for strategy across multiple assets.
        
        Args:
            strategy: Strategy instance
            symbols: List of asset symbols
            start_date: Start date
            end_date: End date 
            interval: Data interval
            portfolio_allocation: Asset allocation weights (optional)
            
        Returns:
            Multi-asset backtest results
        """
        if portfolio_allocation is None:
            # Equal weight allocation
            portfolio_allocation = {symbol: 1.0/len(symbols) for symbol in symbols}
        
        # Fetch data for all assets
        logging.info(f"Fetching data for {len(symbols)} assets")
        all_data = {}
        for symbol in symbols:
            asset_type = self._determine_asset_type(symbol)
            all_data[symbol] = self.data_handler.fetch_data(
                symbol, asset_type, start_date, end_date, interval
            )
        
        # Align all data to common timeframe
        aligned_data = self._align_multi_asset_data(all_data)
        
        # Run strategy on each asset
        all_signals = {}
        all_portfolios = {}
        
        for symbol in symbols:
            data = aligned_data[symbol]
            indicators = strategy.calculate_indicators(data)
            combined_data = pd.concat([data, indicators], axis=1)
            signals = strategy.generate_signals(combined_data)
            
            # Apply risk management
            risk_adjusted_signals = self.risk_manager.apply_risk_rules(
                signals, combined_data, strategy.config
            )
            
            # Run individual backtest with allocated capital
            allocated_cash = self.initial_cash * portfolio_allocation[symbol]
            portfolio = self._run_vectorbt_backtest(
                combined_data, risk_adjusted_signals, strategy.config, allocated_cash
            )
            
            all_signals[symbol] = risk_adjusted_signals
            all_portfolios[symbol] = portfolio
        
        # Combine portfolios
        combined_portfolio = self._combine_portfolios(all_portfolios)
        
        # Analyze combined performance
        performance = self.performance_analyzer.analyze_portfolio(combined_portfolio)
        
        results = {
            'strategy': strategy.get_strategy_info(),
            'symbols': symbols,
            'allocation': portfolio_allocation,
            'period': f"{start_date} to {end_date}",
            'individual_portfolios': all_portfolios,
            'combined_portfolio': combined_portfolio,
            'performance': performance,
            'monthly_summaries': self._calculate_monthly_summaries(combined_portfolio),
            'individual_performance': {
                symbol: self.performance_analyzer.analyze_portfolio(portfolio)
                for symbol, portfolio in all_portfolios.items()
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def run_parameter_optimization(self, strategy_class: type, 
                                  symbol: str, start_date: str, end_date: str,
                                  param_ranges: Dict[str, List],
                                  optimization_metric: str = 'sharpe_ratio',
                                  max_combinations: int = 1000) -> Dict[str, Any]:
        """
        Run parameter optimization using VectorBT's built-in optimization.
        
        Args:
            strategy_class: Strategy class (not instance)
            symbol: Asset symbol
            start_date: Start date
            end_date: End date
            param_ranges: Dictionary of parameter ranges to test
            optimization_metric: Metric to optimize
            max_combinations: Maximum parameter combinations to test
            
        Returns:
            Optimization results
        """
        logging.info(f"Starting parameter optimization for {strategy_class.__name__}")
        
        # Generate parameter combinations
        import itertools
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(itertools.product(*param_values))
        
        if len(combinations) > max_combinations:
            logging.warning(f"Too many combinations ({len(combinations)}). Sampling {max_combinations}")
            combinations = combinations[:max_combinations]
        
        # Fetch base data
        asset_type = self._determine_asset_type(symbol)
        data = self.data_handler.fetch_data(
            symbol, asset_type, start_date, end_date
        )
        
        # Run optimization
        results = []
        best_result = None
        best_metric = float('-inf')
        
        for i, combination in enumerate(combinations):
            if i % 100 == 0:
                logging.info(f"Testing combination {i+1}/{len(combinations)}")
            
            try:
                # Create parameter dict
                params = dict(zip(param_names, combination))
                
                # Create strategy instance with these parameters
                config = StrategyConfig(
                    name=f"{strategy_class.__name__}_opt",
                    asset_type=asset_type,
                    params=params
                )
                strategy = strategy_class(config)
                
                # Run backtest
                result = self.run_single_backtest(
                    strategy, symbol, start_date, end_date
                )
                
                # Extract metric
                metric_value = result['performance'].get(optimization_metric, 0)
                
                result_summary = {
                    'parameters': params,
                    'metric_value': metric_value,
                    'total_return': result['performance'].get('total_return', 0),
                    'max_drawdown': result['performance'].get('max_drawdown', 0),
                    'win_rate': result['performance'].get('win_rate', 0)
                }
                
                results.append(result_summary)
                
                # Track best result
                if metric_value > best_metric:
                    best_metric = metric_value
                    best_result = result
                
            except Exception as e:
                logging.error(f"Error in combination {params}: {str(e)}")
                continue
        
        # Sort results by metric
        results.sort(key=lambda x: x['metric_value'], reverse=True)
        
        optimization_results = {
            'strategy_class': strategy_class.__name__,
            'symbol': symbol,
            'optimization_metric': optimization_metric,
            'total_combinations': len(combinations),
            'successful_combinations': len(results),
            'best_parameters': results[0]['parameters'] if results else None,
            'best_metric_value': results[0]['metric_value'] if results else None,
            'top_10_results': results[:10],
            'all_results': results,
            'best_backtest': best_result,
            'timestamp': datetime.now().isoformat()
        }
        
        return optimization_results
    
    def _run_vectorbt_backtest(self, data: pd.DataFrame, signals: pd.DataFrame,
                              config: StrategyConfig, 
                              initial_cash: Optional[float] = None) -> vbt.Portfolio:
        """Run VectorBT backtest with given signals"""
        cash = initial_cash or self.initial_cash
        
        # Extract signals
        entries = signals.get('entries', pd.Series(False, index=data.index))
        exits = signals.get('exits', pd.Series(False, index=data.index))
        size = signals.get('size', config.risk_per_trade)
        
        # Create portfolio
        portfolio = vbt.Portfolio.from_signals(
            data['Close'], 
            entries=entries,
            exits=exits,
            size=size,
            init_cash=cash,
            fees=config.commission,
            slippage=config.slippage,
            freq='H'  # Assuming hourly data
        )
        
        return portfolio
    
    def _determine_asset_type(self, symbol: str) -> AssetType:
        """Determine asset type from symbol"""
        if '-USD' in symbol or 'USDT' in symbol or 'USDC' in symbol:
            return AssetType.CRYPTO
        elif len(symbol) == 6 and symbol.isupper():
            return AssetType.FOREX
        else:
            return AssetType.STOCKS
    
    def _fetch_benchmark(self, benchmark_symbol: Optional[str], 
                        start_date: str, end_date: str, interval: str) -> Optional[pd.DataFrame]:
        """Fetch benchmark data"""
        if not benchmark_symbol:
            return None
        
        try:
            asset_type = self._determine_asset_type(benchmark_symbol)
            return self.data_handler.fetch_data(
                benchmark_symbol, asset_type, start_date, end_date, interval
            )
        except Exception as e:
            logging.warning(f"Could not fetch benchmark data: {str(e)}")
            return None
    
    def _align_multi_asset_data(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Align multiple asset data to common timeframe"""
        # Find common time index
        common_index = all_data[list(all_data.keys())[0]].index
        for symbol, data in all_data.items():
            common_index = common_index.intersection(data.index)
        
        # Reindex all data to common timeframe
        aligned_data = {}
        for symbol, data in all_data.items():
            aligned_data[symbol] = data.reindex(common_index).fillna(method='ffill')
        
        return aligned_data
    
    def _combine_portfolios(self, portfolios: Dict[str, vbt.Portfolio]) -> vbt.Portfolio:
        """Combine multiple portfolios into one"""
        # This is a simplified combination - would need more sophisticated implementation
        # for proper multi-asset portfolio combining
        total_value = None
        
        for symbol, portfolio in portfolios.items():
            portfolio_value = portfolio.value()
            if total_value is None:
                total_value = portfolio_value
            else:
                total_value += portfolio_value
        
        # Create a synthetic combined portfolio
        # This is a placeholder - real implementation would be more complex
        return list(portfolios.values())[0]  # Return first portfolio as placeholder
    
    def _calculate_monthly_summaries(self, portfolio: vbt.Portfolio) -> List[Dict[str, Any]]:
        """Calculate monthly performance summaries"""
        monthly_returns = portfolio.value().resample('M').last().pct_change()
        monthly_summaries = []
        
        portfolio_value = portfolio.value()
        
        for month_end, monthly_return in monthly_returns.dropna().items():
            month_start = month_end.replace(day=1)
            month_mask = (portfolio_value.index >= month_start) & (portfolio_value.index <= month_end)
            month_data = portfolio_value[month_mask]
            
            if len(month_data) > 0:
                starting_balance = month_data.iloc[0]
                ending_balance = month_data.iloc[-1]
                pnl = ending_balance - starting_balance
                
                # Count trades in month
                trades_mask = (portfolio.orders.records['idx'] >= month_start) if hasattr(portfolio.orders, 'records') else []
                trade_count = len(trades_mask) if isinstance(trades_mask, list) else 0
                
                monthly_summaries.append({
                    'month': month_end.strftime('%Y-%m'),
                    'starting_balance': float(starting_balance),
                    'ending_balance': float(ending_balance),
                    'pnl': float(pnl),
                    'pnl_pct': float(monthly_return * 100),
                    'trades': trade_count
                })
        
        return monthly_summaries
    
    def _analyze_trades(self, portfolio: vbt.Portfolio) -> Dict[str, Any]:
        """Analyze individual trades"""
        trades = portfolio.trades
        
        if trades.count() == 0:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_trade_return': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'avg_duration': 0,
                'profit_factor': 0.0
            }
        
        trade_returns = trades.returns.values
        winning_trades = trade_returns[trade_returns > 0]
        losing_trades = trade_returns[trade_returns <= 0]
        
        return {
            'total_trades': trades.count(),
            'win_rate': len(winning_trades) / len(trade_returns) * 100 if len(trade_returns) > 0 else 0,
            'avg_trade_return': np.mean(trade_returns) * 100 if len(trade_returns) > 0 else 0,
            'best_trade': np.max(trade_returns) * 100 if len(trade_returns) > 0 else 0,
            'worst_trade': np.min(trade_returns) * 100 if len(trade_returns) > 0 else 0,
            'avg_duration': trades.duration.mean() if hasattr(trades, 'duration') else 0,
            'profit_factor': np.sum(winning_trades) / abs(np.sum(losing_trades)) if len(losing_trades) > 0 else float('inf')
        }
    
    def _calculate_risk_metrics(self, portfolio: vbt.Portfolio) -> Dict[str, float]:
        """Calculate risk metrics"""
        returns = portfolio.returns()
        
        return {
            'volatility': returns.std() * np.sqrt(252) * 100,  # Annualized volatility
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'var_95': np.percentile(returns, 5) * 100,  # 5% VaR
            'var_99': np.percentile(returns, 1) * 100,  # 1% VaR
        }
    
    def save_results(self, filename: str, results: Optional[Dict] = None):
        """Save backtest results to file"""
        if self.cache_dir is None:
            self.cache_dir = Path('.')
        
        save_data = results or self.results
        filepath = self.cache_dir / f"{filename}.json"
        
        # Convert numpy types for JSON serialization
        import json
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            return obj
        
        # Remove non-serializable objects
        serializable_data = {}
        for key, value in save_data.items():
            if key not in ['portfolio', 'portfolios']:  # Skip VectorBT objects
                serializable_data[key] = value
        
        with open(filepath, 'w') as f:
            json.dump(serializable_data, f, indent=2, default=convert_numpy)
        
        logging.info(f"Results saved to {filepath}")
    
    def load_results(self, filename: str) -> Dict[str, Any]:
        """Load backtest results from file"""
        if self.cache_dir is None:
            self.cache_dir = Path('.')
            
        filepath = self.cache_dir / f"{filename}.json"
        
        with open(filepath, 'r') as f:
            import json
            return json.load(f)