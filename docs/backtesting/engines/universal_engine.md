# Universal Backtesting Engine Documentation

## Overview
Our custom backtesting engine built on top of backtesting.py that provides a unified interface for testing any trading strategy.

## Architecture

```
UniversalBacktestEngine
├── UniversalStrategy (Base Class)
│   ├── Risk Management Layer
│   ├── Position Sizing
│   ├── Monthly Tracking
│   └── Strategy Interface
├── Data Layer
│   ├── YFinance Integration
│   ├── Binance API
│   └── CSV Support
├── Reporting Layer
│   ├── Performance Metrics
│   ├── Monthly Summaries
│   └── JSON/Markdown Export
└── Strategy Implementations
    ├── SimpleMAStrategy
    ├── FTMOBitcoinStrategy
    └── BTCUSDTEnhancedAdapter
```

## Core Components

### 1. UniversalStrategy Base Class

```python
class UniversalStrategy(Strategy, ABC):
    """Base class all strategies inherit from"""
    
    # Risk parameters (overridable)
    risk_per_trade = 0.02
    max_daily_loss = 0.05
    max_overall_loss = 0.10
    
    # Required methods to implement
    @abstractmethod
    def strategy_init(self):
        """Initialize indicators"""
        pass
    
    @abstractmethod
    def generate_signals(self) -> int:
        """Return: 1 (long), -1 (short), 0 (no signal)"""
        pass
```

### 2. UniversalBacktestEngine

```python
class UniversalBacktestEngine:
    """Main engine that runs any strategy"""
    
    def run_backtest(
        strategy_class: type,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_cash: float = 100000,
        **strategy_params
    ) -> Dict[str, Any]
```

## Features

### Built-in Risk Management
- Daily loss limits with automatic position closing
- Overall drawdown limits
- Emergency stop system
- Position sizing (fixed, volatility-based, Kelly)

### Automatic Monthly Tracking
```python
# Automatically tracked for every strategy
monthly_summaries = [
    {
        'month': '2024-01',
        'starting_balance': 100000,
        'ending_balance': 105000,
        'pnl': 5000,
        'pnl_pct': 5.0,
        'trades': 23
    },
    # ... more months
]
```

### Multi-Source Data Support
- **YFinance**: Stocks, ETFs, Crypto
- **Binance API**: Detailed crypto data
- **CSV Import**: Custom data sources
- **Custom Functions**: Any data source

## Usage Examples

### Basic Usage

```python
from universal_backtesting_engine import UniversalBacktestEngine, UniversalStrategy

# Initialize engine
engine = UniversalBacktestEngine(data_source='yfinance')

# Run backtest
results = engine.run_backtest(
    strategy_class=MyStrategy,
    symbol='BTC-USD',
    start_date='2024-01-01',
    end_date='2024-06-01',
    initial_cash=100000,
    commission=0.001
)
```

### Creating a Custom Strategy

```python
class MyCustomStrategy(UniversalStrategy):
    # Strategy parameters
    fast_period = 20
    slow_period = 50
    rsi_period = 14
    
    def strategy_init(self):
        """Initialize indicators"""
        # EMAs
        self.ema_fast = self.I(
            lambda x: pd.Series(x).ewm(span=self.fast_period).mean(),
            self.data.Close
        )
        self.ema_slow = self.I(
            lambda x: pd.Series(x).ewm(span=self.slow_period).mean(),
            self.data.Close
        )
        
        # RSI
        close = pd.Series(self.data.Close)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / loss
        self.rsi = self.I(lambda: 100 - (100 / (1 + rs)))
    
    def generate_signals(self) -> int:
        """Generate trading signals"""
        # Trend following with momentum filter
        if self.ema_fast[-1] > self.ema_slow[-1] and self.rsi[-1] < 70:
            return 1  # Long signal
        elif self.ema_fast[-1] < self.ema_slow[-1] and self.rsi[-1] > 30:
            return -1  # Short signal
        return 0  # No signal
```

### Testing Multiple Risk Profiles

```python
# Test different configurations
risk_profiles = {
    'conservative': {'risk_per_trade': 0.01, 'max_daily_loss': 0.03},
    'moderate': {'risk_per_trade': 0.02, 'max_daily_loss': 0.05},
    'aggressive': {'risk_per_trade': 0.03, 'max_daily_loss': 0.07}
}

results = {}
for profile_name, params in risk_profiles.items():
    results[profile_name] = engine.run_backtest(
        strategy_class=MyCustomStrategy,
        symbol='BTC-USD',
        start_date='2024-01-01',
        end_date='2024-06-01',
        **params
    )
```

## Report Generation

### Automatic Reports Include:

1. **Performance Metrics**
   - Total Return
   - Sharpe Ratio
   - Sortino Ratio
   - Maximum Drawdown
   - Win Rate
   - Profit Factor

2. **Monthly Summaries**
   - Month-by-month P&L
   - Running balance
   - Trade counts
   - Visual indicators

3. **Trade Analysis**
   - Average trade return
   - Best/worst trades
   - Average duration
   - Exit reasons

### Export Formats

```python
# JSON export (for further analysis)
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

# Markdown report (for documentation)
generate_markdown_report(results, 'report.md')

# Terminal display (for quick review)
engine.print_report(results)
```

## Advanced Features

### Custom Data Sources

```python
def custom_data_fetcher(symbol, start, end, interval, **kwargs):
    """Custom data source function"""
    # Your data fetching logic
    return pd.DataFrame({
        'Open': [...],
        'High': [...],
        'Low': [...],
        'Close': [...],
        'Volume': [...]
    })

engine = UniversalBacktestEngine(data_source=custom_data_fetcher)
```

### Position Sizing Methods

```python
class AdvancedStrategy(UniversalStrategy):
    position_sizing_method = 'volatility_based'  # or 'fixed', 'kelly'
    
    def calculate_position_size(self, signal: int) -> float:
        """Custom position sizing logic"""
        if self.position_sizing_method == 'volatility_based':
            atr = self.data.ATR[-1]
            volatility_factor = atr / self.data.Close[-1]
            return 0.95 * (1 - volatility_factor * 10)
        return 0.95
```

## Performance Considerations

### Current Performance
- **Speed**: Moderate (backtesting.py based)
- **Memory**: Efficient for single strategies
- **Scalability**: Limited by event-driven architecture

### Optimization Tips
1. Pre-calculate indicators in `strategy_init()`
2. Use simple conditions in `generate_signals()`
3. Minimize state tracking
4. Batch parameter testing

## Limitations

### Current Limitations
1. **Speed**: ~50x slower than VectorBT
2. **Vectorization**: Not supported (event-driven)
3. **Multi-asset**: Limited support
4. **Options/Futures**: Not implemented

### Planned Improvements
1. VectorBT integration for speed
2. Multi-asset portfolio support
3. Advanced order types
4. Real-time paper trading

## Migration Path

### To VectorBT
```python
# Current (Universal Engine)
class MyStrategy(UniversalStrategy):
    def generate_signals(self):
        if self.ema_fast[-1] > self.ema_slow[-1]:
            return 1

# Future (VectorBT)
entries = ema_fast.crossed_above(ema_slow)
portfolio = vbt.Portfolio.from_signals(close, entries)
```

## File Structure

```
crypto/
├── universal_backtesting_engine.py    # Main engine
├── test_universal_engine.py           # Test examples
├── test_enhanced_strategy_universal.py # Strategy adapter
└── generate_backtest_report.py        # Report generation
```

## Best Practices

1. **Always inherit from UniversalStrategy**
2. **Implement both required methods**
3. **Use built-in risk management**
4. **Test with multiple parameters**
5. **Review monthly summaries**
6. **Export reports for documentation**

## Example Strategies

### Available Implementations
1. **SimpleMAStrategy** - Basic moving average crossover
2. **FTMOBitcoinStrategy** - Complex FTMO-compliant strategy
3. **BTCUSDTEnhancedAdapter** - Multi-confluence strategy

### Creating New Strategies
1. Copy an existing strategy as template
2. Modify indicators in `strategy_init()`
3. Adjust signals in `generate_signals()`
4. Test with different parameters
5. Document performance

## Troubleshooting

### Common Issues

**Issue**: Strategy not generating trades
- Check signal generation logic
- Verify data is available
- Review risk limits

**Issue**: Poor performance
- Test different parameters
- Check transaction costs
- Review exit logic

**Issue**: Memory errors
- Reduce data period
- Simplify indicators
- Use data sampling

## Future Development

### Roadmap
1. **Q3 2024**: VectorBT integration
2. **Q4 2024**: Multi-asset support
3. **Q1 2025**: Live paper trading
4. **Q2 2025**: Production deployment

### Contributing
1. Test thoroughly with multiple datasets
2. Maintain backward compatibility
3. Document new features
4. Include example usage

---

*Last Updated: August 2025*
*Location: `/crypto/universal_backtesting_engine.py`*