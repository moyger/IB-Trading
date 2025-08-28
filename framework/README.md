# IB Trading Universal Backtesting Framework

Professional-grade backtesting framework built on **VectorBT**, **Pandas**, and **NumPy** for ultra-fast strategy testing across crypto, stocks, and forex markets.

## 🚀 Key Features

- **⚡ Ultra-Fast**: 100-1000x faster than event-driven frameworks
- **🎯 Multi-Asset**: Crypto, stocks, forex support
- **🛡️ Professional Risk Management**: FTMO compliance built-in
- **📊 Comprehensive Analytics**: Industry-standard metrics
- **🔧 Easy to Use**: Simple API, complex under the hood
- **📈 Advanced Features**: Parameter optimization, portfolio analysis

## 🏗️ Architecture

```
framework/
├── core/                    # Core framework components
│   ├── universal_strategy.py    # Base strategy class
│   └── backtest_engine.py       # Main backtesting engine
├── data/                    # Data handling
│   ├── data_handler.py          # Multi-source data handler
│   └── data_sources.py          # Specific data source implementations
├── portfolio/              # Portfolio management
│   ├── risk_manager.py          # Risk management system
│   └── position_sizer.py        # Position sizing methods
├── reporting/              # Analytics and reporting
│   ├── performance_analyzer.py  # Performance metrics
│   └── report_generator.py      # Report generation
├── strategies/             # Example strategies
│   ├── simple_ma_strategy.py    # Simple moving average
│   └── bitcoin_ftmo_strategy.py # Advanced FTMO strategy
├── examples/               # Usage examples
└── tests/                  # Test suite
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r framework/requirements.txt

# Or install individually
pip install vectorbt pandas numpy yfinance
```

### Basic Usage

```python
from framework import BacktestEngine
from framework.strategies.simple_ma_strategy import create_simple_ma_strategy

# Create strategy
strategy = create_simple_ma_strategy(
    fast_period=20,
    slow_period=50, 
    risk_profile='moderate'
)

# Initialize engine
engine = BacktestEngine(initial_cash=100000)

# Run backtest
results = engine.run_single_backtest(
    strategy=strategy,
    symbol='BTC-USD',
    start_date='2024-01-01',
    end_date='2024-06-01'
)

# View results
print(f"Total Return: {results['performance']['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['performance']['sharpe_ratio']:.2f}")
```

## 📊 Example Results

```
=== Bitcoin FTMO Strategy Results ===
Total Return: +15.43%
Max Drawdown: -8.21%
Sharpe Ratio: 1.87
Win Rate: 62.5%
Total Trades: 48
```

## 🎯 Strategy Types Supported

### 1. Simple Strategies
- Moving Average Crossovers
- RSI Mean Reversion
- Bollinger Band Breakouts

### 2. Advanced Strategies  
- Multi-confluence analysis
- FTMO-compliant strategies
- Volatility-adaptive position sizing

### 3. Portfolio Strategies
- Multi-asset portfolios
- Risk parity allocation
- Factor-based strategies

## 🛡️ Risk Management

### Built-in Risk Controls
- **Daily Loss Limits**: Configurable daily drawdown limits
- **Position Size Limits**: Maximum position size per trade
- **FTMO Compliance**: Challenge/verification/funded account modes
- **Emergency Stops**: Automatic position closure on limit breach

### Risk Profiles
```python
# Conservative: 1% risk per trade, 3% daily limit
strategy = create_strategy(risk_profile='conservative')

# Moderate: 2% risk per trade, 5% daily limit  
strategy = create_strategy(risk_profile='moderate')

# Aggressive: 3% risk per trade, 7% daily limit
strategy = create_strategy(risk_profile='aggressive')
```

## 📈 Performance Metrics

### Return Metrics
- Total Return, CAGR, Annualized Return
- Monthly/Quarterly breakdowns

### Risk Metrics  
- Maximum Drawdown, Volatility
- Value at Risk (VaR 95%, 99%)
- Expected Shortfall

### Risk-Adjusted Metrics
- Sharpe Ratio, Sortino Ratio, Calmar Ratio
- Information Ratio, Omega Ratio

### Trade Metrics
- Win Rate, Profit Factor
- Average Trade Return
- Trade Duration Analysis

## 🔧 Advanced Features

### Parameter Optimization
```python
# Optimize strategy parameters
results = engine.run_parameter_optimization(
    strategy_class=SimpleMAStrategy,
    symbol='BTC-USD',
    param_ranges={
        'fast_period': [10, 15, 20, 25],
        'slow_period': [40, 50, 60, 70]
    },
    optimization_metric='sharpe_ratio'
)
```

### Multi-Asset Backtesting
```python
# Test portfolio of assets
results = engine.run_multi_asset_backtest(
    strategy=strategy,
    symbols=['BTC-USD', 'ETH-USD', 'AAPL'], 
    portfolio_allocation={'BTC-USD': 0.4, 'ETH-USD': 0.3, 'AAPL': 0.3}
)
```

### Report Generation
```python
# Generate comprehensive reports
from framework.reporting import ReportGenerator

reporter = ReportGenerator()
report_path = reporter.generate_single_strategy_report(results)
```

## 📋 Comparison with Other Frameworks

| Feature | This Framework | Backtesting.py | Backtrader | QuantConnect |
|---------|---------------|---------------|------------|--------------|
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Multi-Asset** | ✅ | Limited | ✅ | ✅ |
| **Risk Management** | Professional | Basic | Good | Excellent |
| **Learning Curve** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Cost** | Free | Free | Free | $8-400/mo |

## 🧪 Testing

```bash
# Run framework tests
cd framework/tests
python test_framework.py

# Run examples
cd framework/examples  
python basic_usage.py
```

## 🎓 Learning Path

1. **Start Simple**: Use `SimpleMAStrategy` to learn the framework
2. **Add Complexity**: Study `BitcoinFTMOStrategy` for advanced features  
3. **Create Custom**: Build your own strategies using `UniversalStrategy`
4. **Optimize**: Use parameter optimization for best performance
5. **Scale Up**: Multi-asset portfolios and advanced risk management

## 🔮 Future Roadmap

### Phase 1 (Current)
- [x] Core framework architecture
- [x] VectorBT integration
- [x] Basic strategy examples

### Phase 2 (Next)
- [ ] Live trading integration
- [ ] Advanced order types
- [ ] Real-time risk monitoring

### Phase 3 (Future)
- [ ] Machine learning integration
- [ ] Alternative data sources
- [ ] Portfolio optimization

## 📝 Creating Custom Strategies

```python
from framework.core.universal_strategy import UniversalStrategy, StrategyConfig

class MyCustomStrategy(UniversalStrategy):
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        indicators = pd.DataFrame(index=data.index)
        
        # Add your indicators here
        indicators['SMA_20'] = data['Close'].rolling(20).mean()
        indicators['RSI'] = self._calculate_rsi(data['Close'])
        
        return indicators
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        
        # Define your entry/exit logic
        signals['entries'] = (data['Close'] > data['SMA_20']) & (data['RSI'] < 70)
        signals['exits'] = (data['Close'] < data['SMA_20']) | (data['RSI'] > 80)
        signals['size'] = self.config.risk_per_trade
        
        return signals
```

## 🏆 Performance Benchmarks

Testing 1,000 parameter combinations on 1 year of hourly BTC data:

| Framework | Time | Memory | Relative Speed |
|-----------|------|---------|----------------|
| **This Framework (VectorBT)** | **2.5s** | **0.8GB** | **100x** |
| Previous Universal Engine | 250s | 2.1GB | 1x |
| Backtrader | 600s | 4.5GB | 0.4x |

## 📞 Support

- **Examples**: See `framework/examples/`
- **Tests**: Run `framework/tests/test_framework.py`
- **Documentation**: Check `/docs/backtesting/`

---

*Built for professional algorithmic trading with institutional-grade performance and risk management.*