"""
Backtesting Engine for Bybit 1H Trend Composite Strategy
Tests strategy performance from January 2024 to July 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import ccxt

@dataclass
class Trade:
    """Backtesting trade record"""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str  # 'long' or 'short'
    entry_price: float
    exit_price: float
    size: float
    stop_loss: float
    take_profit: float
    pnl: float
    pnl_pct: float
    commission: float
    slippage: float
    exit_reason: str  # 'tp', 'sl', 'signal', 'eod'
    trend_score: float
    confidence: float

@dataclass
class BacktestResults:
    """Backtesting results summary"""
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Performance metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    
    # Trade analysis
    avg_win: float
    avg_loss: float
    avg_win_pct: float
    avg_loss_pct: float
    risk_reward_ratio: float
    profit_factor: float
    
    # Monthly returns
    monthly_returns: Dict[str, float]
    
    # Per symbol performance
    symbol_performance: Dict[str, Dict]
    
    # Trade list
    trades: List[Trade]

class BacktestEngine:
    """
    Backtesting engine for the Bybit strategy
    """
    
    def __init__(self, config=None):
        """Initialize backtesting engine"""
        
        # Configuration
        self.config = config
        
        # Backtesting parameters
        self.start_date = '2024-01-01'
        self.end_date = '2025-07-31'
        self.initial_capital = 10000
        self.commission_rate = 0.0006  # 0.06% taker fee
        self.slippage_pct = 0.05  # 0.05% slippage
        
        # Risk parameters (from strategy)
        self.risk_per_trade = 1.5  # 1.5% risk per trade
        self.max_positions = 3
        self.min_rr_ratio = 1.5  # Minimum risk/reward
        
        # Strategy parameters
        self.sl_atr_multiplier = 2.5
        self.tp_atr_multiplier = 4.0
        self.min_trend_strength = 3.0
        
        # Backtesting state
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # Data storage
        self.market_data = {}
        
        # Initialize exchange for data fetching
        self.exchange = ccxt.bybit({
            'enableRateLimit': True,
            'options': {'defaultType': 'linear'}
        })
    
    def fetch_historical_data(self, symbol: str, timeframe: str = '1h') -> pd.DataFrame:
        """
        Fetch historical data for backtesting
        """
        print(f"📊 Fetching historical data for {symbol}...")
        
        try:
            # Convert dates to timestamps
            start_ts = int(pd.Timestamp(self.start_date).timestamp() * 1000)
            end_ts = int(pd.Timestamp(self.end_date).timestamp() * 1000)
            
            all_data = []
            current_ts = start_ts
            
            # Fetch data in chunks (max 1000 candles per request)
            while current_ts < end_ts:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=current_ts,
                    limit=1000
                )
                
                if not ohlcv:
                    break
                
                all_data.extend(ohlcv)
                
                # Update timestamp for next batch
                if ohlcv:
                    current_ts = ohlcv[-1][0] + 1
                else:
                    break
                
                # Avoid hitting rate limits
                import time
                time.sleep(0.1)
            
            # Convert to DataFrame
            df = pd.DataFrame(all_data, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Remove duplicates and sort
            df = df[~df.index.duplicated(keep='first')]
            df = df.sort_index()
            
            # Filter to date range
            df = df[self.start_date:self.end_date]
            
            print(f"✅ Fetched {len(df)} candles for {symbol}")
            print(f"   Date range: {df.index[0]} to {df.index[-1]}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for backtesting
        """
        # Import indicator calculator
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from indicators.trend_composite import TrendComposite
        
        calculator = TrendComposite()
        df = calculator.calculate_composite(df)
        
        return df
    
    def simulate_trade(self, signal_time: datetime, df: pd.DataFrame, 
                      direction: str, symbol: str) -> Optional[Trade]:
        """
        Simulate a trade execution
        """
        try:
            # Get entry data
            entry_idx = df.index.get_loc(signal_time)
            entry_data = df.iloc[entry_idx]
            
            # Entry price with slippage
            entry_price = entry_data['Close']
            if direction == 'long':
                entry_price *= (1 + self.slippage_pct / 100)
            else:
                entry_price *= (1 - self.slippage_pct / 100)
            
            # Calculate stops
            atr = entry_data['atr']
            
            if direction == 'long':
                stop_loss = entry_price - (self.sl_atr_multiplier * atr)
                take_profit = entry_price + (self.tp_atr_multiplier * atr)
            else:
                stop_loss = entry_price + (self.sl_atr_multiplier * atr)
                take_profit = entry_price - (self.tp_atr_multiplier * atr)
            
            # Check risk/reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            if reward / risk < self.min_rr_ratio:
                return None
            
            # Calculate position size
            risk_amount = self.current_capital * (self.risk_per_trade / 100)
            risk_pct = risk / entry_price
            position_value = risk_amount / risk_pct
            position_size = position_value / entry_price
            
            # Entry commission
            entry_commission = position_value * self.commission_rate
            
            # Simulate trade execution
            for i in range(entry_idx + 1, len(df)):
                current_data = df.iloc[i]
                current_time = df.index[i]
                
                # Check stop loss
                if direction == 'long':
                    if current_data['Low'] <= stop_loss:
                        exit_price = stop_loss
                        exit_reason = 'sl'
                        break
                    elif current_data['High'] >= take_profit:
                        exit_price = take_profit
                        exit_reason = 'tp'
                        break
                else:  # short
                    if current_data['High'] >= stop_loss:
                        exit_price = stop_loss
                        exit_reason = 'sl'
                        break
                    elif current_data['Low'] <= take_profit:
                        exit_price = take_profit
                        exit_reason = 'tp'
                        break
                
                # Check for opposing signal
                if current_data.get('trend_direction'):
                    if (direction == 'long' and current_data['trend_direction'] == 'SHORT') or \
                       (direction == 'short' and current_data['trend_direction'] == 'LONG'):
                        exit_price = current_data['Close']
                        exit_reason = 'signal'
                        break
            else:
                # Exit at end of data
                exit_price = df.iloc[-1]['Close']
                exit_reason = 'eod'
                current_time = df.index[-1]
            
            # Apply slippage to exit
            if direction == 'long':
                exit_price *= (1 - self.slippage_pct / 100)
            else:
                exit_price *= (1 + self.slippage_pct / 100)
            
            # Calculate P&L
            if direction == 'long':
                pnl_pct = (exit_price - entry_price) / entry_price
            else:
                pnl_pct = (entry_price - exit_price) / entry_price
            
            pnl = pnl_pct * position_value
            
            # Exit commission
            exit_commission = position_value * self.commission_rate
            total_commission = entry_commission + exit_commission
            
            # Net P&L
            net_pnl = pnl - total_commission
            
            # Create trade record
            trade = Trade(
                entry_time=signal_time,
                exit_time=current_time,
                symbol=symbol,
                side=direction,
                entry_price=entry_price,
                exit_price=exit_price,
                size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                pnl=net_pnl,
                pnl_pct=pnl_pct * 100,
                commission=total_commission,
                slippage=self.slippage_pct,
                exit_reason=exit_reason,
                trend_score=entry_data.get('trend_score', 0),
                confidence=entry_data.get('confidence', 0)
            )
            
            return trade
            
        except Exception as e:
            print(f"Error simulating trade: {e}")
            return None
    
    def run_backtest(self, symbols: List[str]) -> BacktestResults:
        """
        Run complete backtest for specified symbols
        """
        print("\n" + "=" * 70)
        print("🚀 STARTING BACKTEST")
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Symbols: {', '.join(symbols)}")
        print("=" * 70)
        
        # Fetch and prepare data for all symbols
        print("\n📊 FETCHING HISTORICAL DATA...")
        for symbol in symbols:
            df = self.fetch_historical_data(symbol)
            if not df.empty:
                df = self.calculate_indicators(df)
                self.market_data[symbol] = df
        
        if not self.market_data:
            print("❌ No data available for backtesting")
            return None
        
        # Run backtest simulation
        print("\n🔄 RUNNING BACKTEST SIMULATION...")
        all_signals = []
        
        # Collect all signals from all symbols
        for symbol, df in self.market_data.items():
            # Find all buy/sell signals
            long_signals = df[df['trend_direction'] == 'LONG'].index.tolist()
            short_signals = df[df['trend_direction'] == 'SHORT'].index.tolist()
            
            for signal_time in long_signals:
                all_signals.append((signal_time, symbol, 'long'))
            
            for signal_time in short_signals:
                all_signals.append((signal_time, symbol, 'short'))
        
        # Sort signals by time
        all_signals.sort(key=lambda x: x[0])
        
        print(f"📊 Found {len(all_signals)} total signals")
        
        # Process signals chronologically
        open_positions = {}
        
        for signal_time, symbol, direction in all_signals:
            # Check if we already have a position in this symbol
            if symbol in open_positions:
                continue
            
            # Check max positions limit
            if len(open_positions) >= self.max_positions:
                continue
            
            # Check if we have enough capital
            if self.current_capital < 1000:  # Minimum capital threshold
                continue
            
            # Simulate trade
            df = self.market_data[symbol]
            trade = self.simulate_trade(signal_time, df, direction, symbol)
            
            if trade:
                # Track position
                open_positions[symbol] = trade
                
                # Update when trade closes
                if trade.exit_time:
                    # Update capital
                    self.current_capital += trade.pnl
                    self.trades.append(trade)
                    
                    # Record equity
                    self.equity_curve.append({
                        'time': trade.exit_time,
                        'capital': self.current_capital,
                        'trade_num': len(self.trades)
                    })
                    
                    # Remove from open positions
                    if symbol in open_positions:
                        del open_positions[symbol]
        
        print(f"✅ Executed {len(self.trades)} trades")
        
        # Calculate results
        results = self.calculate_results()
        
        return results
    
    def calculate_results(self) -> BacktestResults:
        """
        Calculate comprehensive backtest results
        """
        if not self.trades:
            print("❌ No trades to analyze")
            return None
        
        # Basic statistics
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        
        total_return = self.current_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        # Average win/loss
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        avg_win_pct = np.mean([t.pnl_pct for t in winning_trades]) if winning_trades else 0
        avg_loss_pct = np.mean([t.pnl_pct for t in losing_trades]) if losing_trades else 0
        
        # Risk reward ratio
        risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Profit factor
        gross_profit = sum([t.pnl for t in winning_trades]) if winning_trades else 0
        gross_loss = abs(sum([t.pnl for t in losing_trades])) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Create equity curve DataFrame
        equity_df = pd.DataFrame(self.equity_curve)
        if not equity_df.empty:
            equity_df.set_index('time', inplace=True)
            
            # Calculate returns
            equity_df['returns'] = equity_df['capital'].pct_change()
            equity_df['cumulative_returns'] = (1 + equity_df['returns']).cumprod() - 1
            
            # Calculate drawdown
            equity_df['cum_max'] = equity_df['capital'].cummax()
            equity_df['drawdown'] = (equity_df['capital'] - equity_df['cum_max']) / equity_df['cum_max']
            
            max_drawdown = equity_df['drawdown'].min() * 100
            
            # Sharpe ratio (annualized)
            returns = equity_df['returns'].dropna()
            if len(returns) > 1:
                sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252 * 24)  # Hourly to annual
            else:
                sharpe_ratio = 0
            
            # Sortino ratio
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252 * 24)
            else:
                sortino_ratio = sharpe_ratio
            
            # Calmar ratio
            years = (pd.Timestamp(self.end_date) - pd.Timestamp(self.start_date)).days / 365
            annual_return = (total_return_pct / years) if years > 0 else 0
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        else:
            max_drawdown = 0
            sharpe_ratio = 0
            sortino_ratio = 0
            calmar_ratio = 0
        
        # Monthly returns
        monthly_returns = self.calculate_monthly_returns()
        
        # Per symbol performance
        symbol_performance = self.calculate_symbol_performance()
        
        # Create results
        results = BacktestResults(
            start_date=self.start_date,
            end_date=self.end_date,
            initial_capital=self.initial_capital,
            final_capital=self.current_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=abs(max_drawdown),
            max_drawdown_duration=0,  # TODO: Calculate
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_win_pct=avg_win_pct,
            avg_loss_pct=avg_loss_pct,
            risk_reward_ratio=risk_reward,
            profit_factor=profit_factor,
            monthly_returns=monthly_returns,
            symbol_performance=symbol_performance,
            trades=self.trades
        )
        
        return results
    
    def calculate_monthly_returns(self) -> Dict[str, float]:
        """Calculate monthly returns"""
        monthly_returns = {}
        
        if not self.trades:
            return monthly_returns
        
        # Group trades by month
        trades_df = pd.DataFrame([asdict(t) for t in self.trades])
        trades_df['month'] = pd.to_datetime(trades_df['exit_time']).dt.to_period('M')
        
        monthly_pnl = trades_df.groupby('month')['pnl'].sum()
        
        for month, pnl in monthly_pnl.items():
            monthly_returns[str(month)] = pnl
        
        return monthly_returns
    
    def calculate_symbol_performance(self) -> Dict[str, Dict]:
        """Calculate per-symbol performance"""
        symbol_perf = {}
        
        for symbol in set(t.symbol for t in self.trades):
            symbol_trades = [t for t in self.trades if t.symbol == symbol]
            
            if symbol_trades:
                winning = [t for t in symbol_trades if t.pnl > 0]
                
                symbol_perf[symbol] = {
                    'total_trades': len(symbol_trades),
                    'win_rate': len(winning) / len(symbol_trades),
                    'total_pnl': sum(t.pnl for t in symbol_trades),
                    'avg_pnl': np.mean([t.pnl for t in symbol_trades]),
                    'best_trade': max(t.pnl for t in symbol_trades),
                    'worst_trade': min(t.pnl for t in symbol_trades)
                }
        
        return symbol_perf