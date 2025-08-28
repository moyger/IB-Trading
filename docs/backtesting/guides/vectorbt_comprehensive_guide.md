# VectorBT: Professional Backtesting Framework - Comprehensive Guide

## 🚀 What is VectorBT?

VectorBT is a **high-performance Python backtesting library** that's 100-1000x faster than traditional frameworks like backtesting.py. It's the library of choice for professional quants and algorithmic traders who need to test thousands of strategies quickly.

### Why VectorBT is Different:
- **Vectorized Operations**: Processes entire arrays at once instead of loops
- **Multi-dimensional**: Test multiple strategies/parameters simultaneously  
- **Numba Acceleration**: Machine-code speed through JIT compilation
- **Professional Features**: Monte Carlo, walk-forward, portfolio optimization

---

## 📦 Installation

### Requirements:
- Python 3.8 - 3.10 (3.11+ not fully supported yet)
- NumPy, Pandas, Numba

### Standard Installation:
```bash
pip install vectorbt
```

### Development Installation:
```bash
git clone https://github.com/polakowo/vectorbt.git
cd vectorbt
pip install -e .
```

### Docker Installation:
```bash
docker run --rm -p 8888:8888 -v "$PWD":/home/jovyan/work polakowo/vectorbt
```

---

## 🎯 Core Concepts

### 1. **Technology Stack**
- **NumPy**: Fast array operations (foundation)
- **Pandas**: Time series data handling
- **Numba**: Just-in-time compilation for speed
- **Plotly**: Interactive visualizations

### 2. **Vectorization Philosophy**
Instead of iterating through each trade:
```python
# Traditional (slow)
for i in range(len(data)):
    if condition[i]:
        execute_trade()

# VectorBT (fast)
portfolio = vbt.Portfolio.from_signals(data, entries, exits)
```

### 3. **Multi-dimensional Processing**
Test multiple strategies at once:
```python
# Test multiple MA periods simultaneously
fast_ma = vbt.MA.run(price, [10, 20, 30])  # 3 strategies at once
slow_ma = vbt.MA.run(price, [50, 100, 200])  # 3 strategies at once
# Results in 9 strategy combinations tested simultaneously!
```

---

## 💻 Basic Usage Examples

### Example 1: Simple Buy & Hold
```python
import vectorbt as vbt
import pandas as pd

# Download Bitcoin data
btc_price = vbt.YFData.download('BTC-USD', start='2020-01-01', end='2024-01-01').get('Close')

# Create portfolio from holding strategy
portfolio = vbt.Portfolio.from_holding(btc_price, init_cash=10000)

# Get performance metrics
print(f"Total Return: {portfolio.total_return():.2%}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio()}")
print(f"Max Drawdown: {portfolio.max_drawdown():.2%}")
```

### Example 2: Moving Average Crossover
```python
# Calculate moving averages
fast_ma = vbt.MA.run(btc_price, 20, short_name='fast')
slow_ma = vbt.MA.run(btc_price, 50, short_name='slow')

# Generate signals
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

# Create portfolio
portfolio = vbt.Portfolio.from_signals(
    btc_price, 
    entries, 
    exits, 
    init_cash=10000,
    fees=0.001  # 0.1% fees
)

# Display statistics
portfolio.stats()
```

### Example 3: RSI Strategy
```python
# Calculate RSI
rsi = vbt.RSI.run(btc_price, window=14)

# Generate signals
entries = rsi.rsi_crossed_below(30)  # Oversold
exits = rsi.rsi_crossed_above(70)    # Overbought

# Backtest
portfolio = vbt.Portfolio.from_signals(
    btc_price,
    entries,
    exits,
    init_cash=10000,
    size=0.95,  # Use 95% of available cash
    fees=0.001
)

# Plot results
portfolio.plot().show()
```

---

## 🔥 Advanced Features

### 1. **Parameter Optimization**
Test multiple parameters simultaneously:
```python
# Test multiple RSI periods and thresholds
windows = [10, 14, 20, 30]
entry_thresholds = [20, 25, 30, 35]
exit_thresholds = [65, 70, 75, 80]

# Run all combinations
rsi = vbt.RSI.run(btc_price, window=windows)
entries = rsi.rsi_below(entry_thresholds)
exits = rsi.rsi_above(exit_thresholds)

# This creates hundreds of strategy combinations!
portfolios = vbt.Portfolio.from_signals(btc_price, entries, exits)

# Find best parameters
best_sharpe = portfolios.sharpe_ratio().idxmax()
print(f"Best parameters: {best_sharpe}")
```

### 2. **Multi-Asset Portfolio**
```python
# Download multiple assets
symbols = ['BTC-USD', 'ETH-USD', 'BNB-USD']
data = vbt.YFData.download(symbols, start='2022-01-01').get('Close')

# Apply strategy to all assets
fast_ma = vbt.MA.run(data, 20)
slow_ma = vbt.MA.run(data, 50)
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

# Create multi-asset portfolio
portfolio = vbt.Portfolio.from_signals(
    data, 
    entries, 
    exits,
    init_cash=10000,
    cash_sharing=True,  # Share cash across assets
    call_seq='auto'     # Optimize execution order
)
```

### 3. **Custom Indicators with Numba**
```python
from numba import njit
import numpy as np

@njit
def custom_indicator_nb(close, period):
    """Custom indicator compiled with Numba for speed"""
    out = np.empty_like(close)
    for i in range(close.shape[0]):
        if i < period:
            out[i] = np.nan
        else:
            # Your custom calculation
            out[i] = np.std(close[i-period:i]) / np.mean(close[i-period:i])
    return out

# Use custom indicator
custom_values = custom_indicator_nb(btc_price.values, 20)
```

---

## 📊 Performance Comparison

### VectorBT vs Traditional Frameworks

| Operation | VectorBT | Backtesting.py | Backtrader |
|-----------|----------|----------------|------------|
| 1,000 backtests | 0.5 sec | 50 sec | 120 sec |
| 10,000 backtests | 5 sec | 500 sec | Timeout |
| Parameter optimization | Native | Manual loops | Limited |
| Multi-asset | Native | Complex | Supported |
| Memory usage | Low | Medium | High |

---

## 🎯 Migrating from Backtesting.py to VectorBT

### Backtesting.py Strategy:
```python
from backtesting import Strategy

class MyStrategy(Strategy):
    def init(self):
        self.ma = self.I(SMA, self.data.Close, 20)
    
    def next(self):
        if self.data.Close[-1] > self.ma[-1]:
            self.buy()
        elif self.data.Close[-1] < self.ma[-1]:
            self.sell()
```

### Equivalent in VectorBT:
```python
# Much simpler and faster!
ma = vbt.MA.run(price, 20)
entries = price > ma.ma
exits = price < ma.ma
portfolio = vbt.Portfolio.from_signals(price, entries, exits)
```

---

## 💡 Best Practices

### 1. **Data Preparation**
```python
# Always check data quality
data = vbt.YFData.download('BTC-USD')
close = data.get('Close')

# Handle missing data
close = close.fillna(method='ffill')

# Ensure proper datetime index
close.index = pd.to_datetime(close.index)
```

### 2. **Memory Management**
```python
# For large datasets, process in chunks
chunk_size = 10000
portfolios = []

for i in range(0, len(params), chunk_size):
    chunk_params = params[i:i+chunk_size]
    pf = vbt.Portfolio.from_signals(data, entries[chunk_params], exits[chunk_params])
    portfolios.append(pf)

# Combine results
combined = vbt.Portfolio.row_stack(*portfolios)
```

### 3. **Performance Optimization**
```python
# Use built-in indicators when possible
# Built-in (fast)
ma = vbt.MA.run(price, 20)

# Custom (slower)
ma_custom = price.rolling(20).mean()

# Use broadcasting for parameter testing
windows = np.arange(10, 100, 10).reshape(-1, 1)  # Column vector
entries = vbt.MA.run(price, windows).ma_crossed_above(price)
```

---

## 🚀 Production-Ready Example

```python
import vectorbt as vbt
import numpy as np
import pandas as pd
from datetime import datetime

class ProfessionalStrategy:
    """Production-ready VectorBT strategy"""
    
    def __init__(self, symbols, start_date, end_date, init_cash=100000):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.init_cash = init_cash
        
    def fetch_data(self):
        """Fetch and prepare data"""
        self.data = vbt.YFData.download(
            self.symbols, 
            start=self.start_date,
            end=self.end_date,
            missing_index='drop'
        )
        self.close = self.data.get('Close')
        return self.close
    
    def generate_signals(self):
        """Generate entry and exit signals"""
        # Multiple timeframes
        fast_ma = vbt.MA.run(self.close, 20)
        slow_ma = vbt.MA.run(self.close, 50)
        
        # RSI for momentum
        rsi = vbt.RSI.run(self.close, 14)
        
        # Combine conditions
        trend_up = fast_ma.ma > slow_ma.ma
        momentum_good = (rsi.rsi > 30) & (rsi.rsi < 70)
        
        # Entry: Trend up + good momentum + MA crossover
        self.entries = fast_ma.ma_crossed_above(slow_ma.ma) & trend_up & momentum_good
        
        # Exit: MA crossdown or RSI extreme
        self.exits = fast_ma.ma_crossed_below(slow_ma.ma) | (rsi.rsi > 80)
        
        return self.entries, self.exits
    
    def run_backtest(self):
        """Execute backtest with risk management"""
        portfolio = vbt.Portfolio.from_signals(
            self.close,
            self.entries,
            self.exits,
            init_cash=self.init_cash,
            size=0.95,  # Use 95% of available cash
            fees=0.001,  # 0.1% fees
            slippage=0.001,  # 0.1% slippage
            freq='1D'
        )
        return portfolio
    
    def optimize_parameters(self):
        """Parameter optimization"""
        # Test multiple MA periods
        fast_windows = [10, 15, 20, 25, 30]
        slow_windows = [40, 50, 60, 70, 80]
        
        # Create parameter grid
        fast_ma = vbt.MA.run(self.close, fast_windows, param_product=True)
        slow_ma = vbt.MA.run(self.close, slow_windows, param_product=True)
        
        entries = fast_ma.ma_crossed_above(slow_ma.ma)
        exits = fast_ma.ma_crossed_below(slow_ma.ma)
        
        # Run all combinations
        portfolios = vbt.Portfolio.from_signals(
            self.close,
            entries,
            exits,
            init_cash=self.init_cash
        )
        
        # Find best combination
        best_sharpe = portfolios.sharpe_ratio().idxmax()
        return portfolios[best_sharpe]
    
    def analyze_results(self, portfolio):
        """Comprehensive analysis"""
        print("=== PERFORMANCE METRICS ===")
        print(f"Total Return: {portfolio.total_return():.2%}")
        print(f"Annual Return: {portfolio.annualized_return():.2%}")
        print(f"Sharpe Ratio: {portfolio.sharpe_ratio():.2f}")
        print(f"Sortino Ratio: {portfolio.sortino_ratio():.2f}")
        print(f"Max Drawdown: {portfolio.max_drawdown():.2%}")
        print(f"Win Rate: {portfolio.win_rate():.2%}")
        print(f"Total Trades: {portfolio.count()}")
        
        # Plot results
        fig = portfolio.plot()
        fig.show()
        
        return portfolio.stats()

# Usage
strategy = ProfessionalStrategy(
    symbols=['BTC-USD', 'ETH-USD'],
    start_date='2022-01-01',
    end_date='2024-01-01',
    init_cash=100000
)

# Run strategy
data = strategy.fetch_data()
entries, exits = strategy.generate_signals()
portfolio = strategy.run_backtest()
stats = strategy.analyze_results(portfolio)
```

---

## 📚 Key Takeaways

### VectorBT Advantages:
✅ **100-1000x faster** than traditional frameworks
✅ **Multi-dimensional testing** - test thousands of parameters at once
✅ **Professional features** - Monte Carlo, walk-forward, optimization
✅ **Memory efficient** - handles large datasets
✅ **Production ready** - used by professional quants

### When to Use VectorBT:
- Parameter optimization (testing many combinations)
- Multi-asset portfolios
- High-frequency strategies
- Large-scale research
- Production trading systems

### When NOT to Use VectorBT:
- Learning backtesting basics (use backtesting.py)
- Simple single strategies
- When you need event-by-event debugging
- Complex order types (use event-driven frameworks)

---

## 🔗 Resources

- **Official Documentation**: https://vectorbt.dev/
- **GitHub Repository**: https://github.com/polakowo/vectorbt
- **VectorBT PRO**: https://vectorbt.pro/ (Commercial version)
- **Community Forum**: Discord and GitHub Discussions
- **Tutorial Videos**: YouTube "VectorBT Tutorial"

---

*Note: VectorBT is the industry standard for professional algorithmic trading in Python. While it has a steeper learning curve than backtesting.py, the performance gains and professional features make it essential for serious quantitative trading.*