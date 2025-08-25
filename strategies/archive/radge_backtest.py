#!/usr/bin/env python3
"""
Nick Radge Momentum Strategy Backtesting
Monthly rebalancing to top 10 momentum stocks with realistic transaction costs
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sp500_constituents import get_sp500_symbols

class RadgeBacktester:
    """Backtest Nick Radge's momentum strategy with monthly rebalancing"""
    
    def __init__(self, 
                 initial_capital: float = 100000,
                 transaction_cost: float = 0.001,  # 0.1% per trade
                 top_n: int = 10,
                 rebalance_frequency: str = 'M'):  # Monthly
        
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.top_n = top_n
        self.rebalance_frequency = rebalance_frequency
        
        # Backtest results storage
        self.equity_curve = pd.DataFrame()
        self.trades = []
        self.holdings = []
        self.performance_metrics = {}
        
    def get_historical_data(self, 
                           symbols: List[str], 
                           start_date: str, 
                           end_date: str) -> Dict[str, pd.DataFrame]:
        """Download historical data for all symbols"""
        
        print(f"📊 Downloading historical data for {len(symbols)} stocks...")
        print(f"📅 Period: {start_date} to {end_date}")
        
        data = {}
        failed = []
        
        for i, symbol in enumerate(symbols):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(symbols)} ({i/len(symbols)*100:.1f}%)")
            
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if not df.empty and len(df) > 300:  # Need enough history for momentum calc
                    df.columns = [col.lower() for col in df.columns]
                    data[symbol] = df
                else:
                    failed.append(symbol)
                    
            except Exception as e:
                failed.append(symbol)
                continue
        
        print(f"✅ Successfully downloaded: {len(data)} stocks")
        print(f"❌ Failed: {len(failed)} stocks")
        
        return data
    
    def calculate_momentum_score(self, 
                                df: pd.DataFrame, 
                                as_of_date: pd.Timestamp,
                                nlook: int = 252,
                                skip_days: int = 21) -> Optional[float]:
        """Calculate Nick Radge momentum score as of specific date"""
        
        # Get data up to the as_of_date
        hist_data = df[df.index <= as_of_date]
        
        if len(hist_data) < nlook + skip_days:
            return None
            
        try:
            # Price now (with skip_days)
            if skip_days > 0:
                price_now = hist_data['close'].iloc[-(skip_days + 1)]
            else:
                price_now = hist_data['close'].iloc[-1]
                
            # Price then (252 days ago)
            price_then = hist_data['close'].iloc[-(nlook + skip_days)]
            
            if price_then <= 0:
                return None
                
            # Nick Radge formula
            momentum_score = (price_now / price_then) - 1
            return momentum_score
            
        except (IndexError, ValueError):
            return None
    
    def apply_filters(self, 
                     df: pd.DataFrame, 
                     as_of_date: pd.Timestamp,
                     min_price: float = 10.0,
                     min_dollar_volume: float = 1_000_000) -> bool:
        """Apply Nick Radge's filters as of specific date"""
        
        # Get recent data for filters
        recent_data = df[df.index <= as_of_date].tail(50)
        
        if len(recent_data) < 20:
            return False
            
        try:
            current_price = recent_data['close'].iloc[-1]
            
            # Price filter
            if current_price < min_price:
                return False
                
            # Volume filter (50-day average dollar volume)
            avg_volume = recent_data['volume'].mean()
            avg_price = recent_data['close'].mean()
            dollar_volume = avg_volume * avg_price
            
            if dollar_volume < min_dollar_volume:
                return False
                
            return True
            
        except Exception:
            return False
    
    def check_spy_regime(self, spy_data: pd.DataFrame, as_of_date: pd.Timestamp) -> bool:
        """Check if SPY is above 200-day MA as of specific date"""
        
        hist_data = spy_data[spy_data.index <= as_of_date]
        
        if len(hist_data) < 200:
            return True  # Default to bullish if not enough data
            
        try:
            current_price = hist_data['close'].iloc[-1]
            ma_200 = hist_data['close'].tail(200).mean()
            
            return current_price > ma_200
            
        except Exception:
            return True
    
    def rank_stocks_by_momentum(self, 
                               data: Dict[str, pd.DataFrame], 
                               spy_data: pd.DataFrame,
                               as_of_date: pd.Timestamp) -> List[Tuple[str, float]]:
        """Rank stocks by momentum as of specific date"""
        
        # Check market regime first
        bullish_regime = self.check_spy_regime(spy_data, as_of_date)
        
        if not bullish_regime:
            print(f"🔴 Bearish regime on {as_of_date.date()}, no positions taken")
            return []
        
        momentum_scores = []
        
        for symbol, df in data.items():
            # Apply filters
            if not self.apply_filters(df, as_of_date):
                continue
                
            # Calculate momentum
            momentum = self.calculate_momentum_score(df, as_of_date)
            
            if momentum is not None:
                momentum_scores.append((symbol, momentum))
        
        # Sort by momentum descending
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        
        return momentum_scores
    
    def calculate_portfolio_value(self, 
                                 holdings: Dict[str, float], 
                                 data: Dict[str, pd.DataFrame], 
                                 as_of_date: pd.Timestamp,
                                 cash: float) -> float:
        """Calculate total portfolio value as of specific date"""
        
        portfolio_value = cash
        
        for symbol, shares in holdings.items():
            if symbol in data and shares > 0:
                # Get price as of date
                hist_data = data[symbol][data[symbol].index <= as_of_date]
                if not hist_data.empty:
                    price = hist_data['close'].iloc[-1]
                    portfolio_value += shares * price
        
        return portfolio_value
    
    def run_backtest(self, 
                    start_date: str = "2023-01-01",
                    end_date: str = "2024-01-01") -> pd.DataFrame:
        """Run the complete backtest"""
        
        print(f"\n🚀 NICK RADGE MOMENTUM BACKTEST")
        print("=" * 80)
        print(f"💰 Initial Capital: ${self.initial_capital:,.0f}")
        print(f"🔄 Rebalancing: {self.rebalance_frequency}onthly")
        print(f"🎯 Top N stocks: {self.top_n}")
        print(f"💸 Transaction Cost: {self.transaction_cost:.1%}")
        print("=" * 80)
        
        # Get S&P 500 universe
        symbols = get_sp500_symbols()[:100]  # Limit for testing - remove [:100] for full universe
        
        # Download historical data
        data = self.get_historical_data(symbols, 
                                      (pd.to_datetime(start_date) - timedelta(days=400)).strftime('%Y-%m-%d'),
                                      end_date)
        
        # Get SPY data for regime filter
        spy_data = yf.Ticker("SPY").history(start=(pd.to_datetime(start_date) - timedelta(days=400)).strftime('%Y-%m-%d'), 
                                          end=end_date)
        spy_data.columns = [col.lower() for col in spy_data.columns]
        
        # Generate rebalancing dates
        date_range = pd.date_range(start=start_date, end=end_date, freq='MS')  # Month start
        
        # Initialize portfolio
        cash = self.initial_capital
        holdings = {}  # {symbol: shares}
        
        # Results tracking
        equity_curve = []
        
        print(f"\n📈 Running backtest with {len(date_range)} rebalancing periods...")
        
        for i, rebal_date in enumerate(date_range):
            print(f"\n[{i+1}/{len(date_range)}] Rebalancing on {rebal_date.date()}")
            
            # Calculate current portfolio value
            portfolio_value = self.calculate_portfolio_value(holdings, data, rebal_date, cash)
            
            # Rank stocks by momentum
            momentum_rankings = self.rank_stocks_by_momentum(data, spy_data, rebal_date)
            
            if not momentum_rankings:
                # Bearish regime - sell all and hold cash
                if holdings:
                    print("  📤 Selling all positions (bearish regime)")
                    for symbol, shares in holdings.items():
                        if symbol in data and shares > 0:
                            hist_data = data[symbol][data[symbol].index <= rebal_date]
                            if not hist_data.empty:
                                price = hist_data['close'].iloc[-1]
                                proceeds = shares * price * (1 - self.transaction_cost)
                                cash += proceeds
                                
                                self.trades.append({
                                    'date': rebal_date,
                                    'symbol': symbol,
                                    'action': 'SELL',
                                    'shares': shares,
                                    'price': price,
                                    'proceeds': proceeds
                                })
                    
                    holdings = {}
                
                # Record equity curve
                equity_curve.append({
                    'date': rebal_date,
                    'portfolio_value': cash,
                    'cash': cash,
                    'positions': 0
                })
                continue
            
            # Get top N stocks
            top_stocks = momentum_rankings[:self.top_n]
            target_symbols = {symbol for symbol, _ in top_stocks}
            
            print(f"  🎯 Top {len(top_stocks)} momentum stocks:")
            for j, (symbol, momentum) in enumerate(top_stocks[:5], 1):
                print(f"     {j}. {symbol}: {momentum:+.2%}")
            
            # Calculate target allocation per position
            target_value_per_position = portfolio_value / len(top_stocks)
            
            # Close positions not in target list
            positions_to_close = []
            for symbol in holdings.keys():
                if symbol not in target_symbols:
                    positions_to_close.append(symbol)
            
            for symbol in positions_to_close:
                shares = holdings[symbol]
                if shares > 0 and symbol in data:
                    hist_data = data[symbol][data[symbol].index <= rebal_date]
                    if not hist_data.empty:
                        price = hist_data['close'].iloc[-1]
                        proceeds = shares * price * (1 - self.transaction_cost)
                        cash += proceeds
                        
                        self.trades.append({
                            'date': rebal_date,
                            'symbol': symbol,
                            'action': 'SELL',
                            'shares': shares,
                            'price': price,
                            'proceeds': proceeds
                        })
                        
                del holdings[symbol]
                print(f"  📤 Sold {symbol}: {shares} shares @ ${price:.2f}")
            
            # Open/adjust positions for target stocks
            for symbol, momentum in top_stocks:
                if symbol not in data:
                    continue
                    
                hist_data = data[symbol][data[symbol].index <= rebal_date]
                if hist_data.empty:
                    continue
                    
                current_price = hist_data['close'].iloc[-1]
                target_shares = int(target_value_per_position / current_price)
                current_shares = holdings.get(symbol, 0)
                
                if target_shares > current_shares:
                    # Buy more shares
                    shares_to_buy = target_shares - current_shares
                    cost = shares_to_buy * current_price * (1 + self.transaction_cost)
                    
                    if cost <= cash:
                        cash -= cost
                        holdings[symbol] = target_shares
                        
                        self.trades.append({
                            'date': rebal_date,
                            'symbol': symbol,
                            'action': 'BUY',
                            'shares': shares_to_buy,
                            'price': current_price,
                            'cost': cost
                        })
                        
                        print(f"  📥 Bought {symbol}: {shares_to_buy} shares @ ${current_price:.2f}")
            
            # Calculate final portfolio value
            final_portfolio_value = self.calculate_portfolio_value(holdings, data, rebal_date, cash)
            
            # Record equity curve
            equity_curve.append({
                'date': rebal_date,
                'portfolio_value': final_portfolio_value,
                'cash': cash,
                'positions': len([s for s in holdings.values() if s > 0])
            })
            
            print(f"  💰 Portfolio Value: ${final_portfolio_value:,.0f} | Cash: ${cash:,.0f} | Positions: {len([s for s in holdings.values() if s > 0])}")
        
        # Convert to DataFrame
        self.equity_curve = pd.DataFrame(equity_curve)
        self.equity_curve.set_index('date', inplace=True)
        
        # Calculate performance metrics
        self.calculate_performance_metrics(spy_data, start_date, end_date)
        
        return self.equity_curve
    
    def calculate_performance_metrics(self, spy_data: pd.DataFrame, start_date: str, end_date: str):
        """Calculate comprehensive performance metrics"""
        
        if self.equity_curve.empty:
            return
        
        # Calculate returns
        self.equity_curve['returns'] = self.equity_curve['portfolio_value'].pct_change()
        self.equity_curve['cumulative_returns'] = (1 + self.equity_curve['returns']).cumprod() - 1
        
        # Get SPY benchmark data
        spy_benchmark = spy_data[(spy_data.index >= start_date) & (spy_data.index <= end_date)]
        spy_monthly = spy_benchmark.resample('MS').last()['close']
        spy_returns = spy_monthly.pct_change().dropna()
        spy_cumulative = (1 + spy_returns).cumprod() - 1
        
        # Performance calculations
        total_return = self.equity_curve['portfolio_value'].iloc[-1] / self.initial_capital - 1
        spy_total_return = spy_cumulative.iloc[-1] if not spy_cumulative.empty else 0
        
        # Annualized metrics
        periods = len(self.equity_curve)
        years = periods / 12  # Monthly data
        
        annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        annual_volatility = self.equity_curve['returns'].std() * np.sqrt(12)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        # Drawdown calculation
        peak = self.equity_curve['portfolio_value'].expanding().max()
        drawdown = (self.equity_curve['portfolio_value'] - peak) / peak
        max_drawdown = drawdown.min()
        
        # Store metrics
        self.performance_metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'spy_total_return': spy_total_return,
            'excess_return': total_return - spy_total_return,
            'win_rate': (self.equity_curve['returns'] > 0).sum() / len(self.equity_curve['returns']) * 100
        }
    
    def print_performance_summary(self):
        """Print comprehensive performance summary"""
        
        if not self.performance_metrics:
            print("No performance metrics available")
            return
        
        metrics = self.performance_metrics
        
        print(f"\n🏆 RADGE MOMENTUM BACKTEST RESULTS")
        print("=" * 80)
        
        print(f"📊 RETURN METRICS:")
        print(f"   Total Return:     {metrics['total_return']:+7.2%}")
        print(f"   Annual Return:    {metrics['annual_return']:+7.2%}")
        print(f"   SPY Benchmark:    {metrics['spy_total_return']:+7.2%}")
        print(f"   Excess Return:    {metrics['excess_return']:+7.2%}")
        
        print(f"\n📈 RISK METRICS:")
        print(f"   Annual Volatility: {metrics['annual_volatility']:7.2%}")
        print(f"   Sharpe Ratio:      {metrics['sharpe_ratio']:7.2f}")
        print(f"   Max Drawdown:      {metrics['max_drawdown']:7.2%}")
        print(f"   Win Rate:          {metrics['win_rate']:7.1f}%")
        
        print(f"\n💼 TRADING METRICS:")
        print(f"   Total Trades:      {len(self.trades):7.0f}")
        print(f"   Final Value:       ${self.equity_curve['portfolio_value'].iloc[-1]:,.0f}")
        print(f"   Initial Capital:   ${self.initial_capital:,.0f}")
        
        # Performance rating
        if metrics['sharpe_ratio'] > 1.5:
            rating = "🏆 EXCELLENT"
        elif metrics['sharpe_ratio'] > 1.0:
            rating = "✅ GOOD" 
        elif metrics['sharpe_ratio'] > 0.5:
            rating = "⚠️ FAIR"
        else:
            rating = "❌ POOR"
        
        print(f"\n🎯 OVERALL RATING: {rating}")
        print("=" * 80)
    
    def plot_results(self):
        """Plot equity curve and performance charts"""
        
        if self.equity_curve.empty:
            print("No results to plot")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Equity curve
        ax1.plot(self.equity_curve.index, self.equity_curve['portfolio_value'], 'b-', linewidth=2, label='Radge Strategy')
        ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        ax1.set_title('Portfolio Value Over Time')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Monthly returns
        monthly_returns = self.equity_curve['returns'] * 100
        colors = ['green' if x > 0 else 'red' for x in monthly_returns]
        ax2.bar(range(len(monthly_returns)), monthly_returns, color=colors, alpha=0.7)
        ax2.set_title('Monthly Returns')
        ax2.set_ylabel('Return (%)')
        ax2.set_xlabel('Month')
        ax2.grid(True, alpha=0.3)
        
        # Drawdown
        peak = self.equity_curve['portfolio_value'].expanding().max()
        drawdown = (self.equity_curve['portfolio_value'] - peak) / peak * 100
        ax3.fill_between(self.equity_curve.index, drawdown, 0, color='red', alpha=0.3)
        ax3.set_title('Drawdown')
        ax3.set_ylabel('Drawdown (%)')
        ax3.grid(True, alpha=0.3)
        
        # Position count
        ax4.plot(self.equity_curve.index, self.equity_curve['positions'], 'g-', linewidth=2)
        ax4.set_title('Number of Positions')
        ax4.set_ylabel('Positions')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def main():
    """Run Nick Radge momentum backtest"""
    
    # Initialize backtester
    backtester = RadgeBacktester(
        initial_capital=100000,     # $100K starting capital
        transaction_cost=0.001,     # 0.1% transaction cost
        top_n=10,                   # Top 10 momentum stocks
        rebalance_frequency='M'     # Monthly rebalancing
    )
    
    # Run 2-year backtest
    results = backtester.run_backtest(
        start_date="2022-01-01",
        end_date="2024-01-01"
    )
    
    # Print results
    backtester.print_performance_summary()
    
    # Plot results
    backtester.plot_results()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results.to_csv(f"radge_backtest_results_{timestamp}.csv")
    print(f"\n💾 Results saved to: radge_backtest_results_{timestamp}.csv")

if __name__ == "__main__":
    main()