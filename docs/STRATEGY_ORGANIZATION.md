# Strategy Organization Guide

## 📁 **Directory Structure**

The Edgerunner framework organizes strategies by asset class for better maintainability and scalability:

```
edgerunner/strategies/
├── __init__.py                    # Main strategy module
├── base.py                        # Base strategy class
├── manager.py                     # Strategy manager
├── runner.py                      # Strategy execution
│
├── forex/                         # 💱 Forex & Metals
│   ├── __init__.py               # Forex strategy index
│   ├── xauusd_ftmo_1h_enhanced_strategy.py
│   ├── xauusd_ftmo_1h_live_trader.py
│   └── xauusd_ftmo_1h_cloudflare.py
│
├── crypto/                        # ₿ Cryptocurrency  
│   ├── __init__.py               # Crypto strategy index
│   ├── btcusdt_ftmo_1h_strategy.py
│   ├── btcusdt_enhanced_strategy.py
│   ├── arthur_hill_trend_strategy.py
│   └── multi_confluence_momentum_strategy.py
│
├── stocks/                        # 📈 Equities & ETFs
│   ├── __init__.py               # Stock strategy index
│   ├── dynamic_stock_selection_strategy.py
│   ├── individual_stock_portfolio_strategy.py
│   ├── mtum_trend_composite_strategy.py
│   └── three_stock_trend_composite_backtest.py
│
└── indices/                       # 📊 Market Indices
    ├── __init__.py               # Index strategy index
    └── (strategies to be developed)
```

## 🎯 **Asset Class Organization**

### **🏛️ Forex Strategies** (`edgerunner/strategies/forex/`)
- **Primary Focus**: Currency pairs and precious metals
- **Broker Integration**: Primarily MT5 via webhook bridge
- **Risk Management**: FTMO-compliant (daily/overall loss limits)
- **Timeframes**: 1H, 4H for faster execution

#### Available Strategies:
- `xauusd_ftmo_1h_enhanced` - FTMO-compliant gold strategy
- `xauusd_live_trader` - Live trading implementation with webhook

#### Supported Symbols:
- XAUUSD (Gold), XAGUSD (Silver)
- EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD
- NZDUSD, USDCHF

### **₿ Crypto Strategies** (`edgerunner/strategies/crypto/`)
- **Primary Focus**: Cryptocurrency trading
- **Broker Integration**: Bybit (primary), MT5 (secondary) 
- **Risk Management**: Modified FTMO-style for crypto volatility
- **Timeframes**: 1H, 4H for momentum capture

#### Available Strategies:
- `btcusdt_ftmo_1h` - Bitcoin FTMO-style strategy
- `btcusdt_enhanced` - Enhanced multi-confirmation system
- `arthur_hill_trend` - Trend-following methodology
- `multi_confluence_momentum` - Multi-signal confluence

#### Supported Symbols:
- BTCUSDT, ETHUSDT, ADAUSDT, DOTUSDT
- LINKUSDT, SOLUSDT, AVAXUSDT, MATICUSDT, XRPUSDT

### **📈 Stock Strategies** (`edgerunner/strategies/stocks/`)
- **Primary Focus**: Individual stocks and ETFs
- **Broker Integration**: Interactive Brokers (primary)
- **Risk Management**: Portfolio-based position sizing
- **Timeframes**: Daily, Weekly for fundamental alignment

#### Available Strategies:
- `dynamic_stock_selection` - Adaptive stock selection
- `individual_stock_portfolio` - Portfolio management approach
- `mtum_trend_composite` - Momentum ETF strategy
- `three_stock_trend` - Multi-stock trend system

#### Supported Symbols:
- **Tech**: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA
- **ETFs**: SPY, QQQ, MTUM, VTI, IWM
- **Blue Chips**: JNJ, UNH, HD, PG

### **📊 Index Strategies** (`edgerunner/strategies/indices/`)
- **Primary Focus**: Market indices and futures
- **Broker Integration**: Interactive Brokers, MT5
- **Risk Management**: Index-specific volatility adjustments
- **Timeframes**: 4H, Daily for trend capture

#### Planned Strategies:
- `sp500_momentum` - S&P 500 momentum strategy
- `nasdaq_trend` - NASDAQ trend following
- `dow_jones_breakout` - Dow breakout system

## 🔄 **Strategy Usage Examples**

### **Basic Strategy Access**
```python
from edgerunner.strategies import StrategyManager
from edgerunner.strategies.forex import FOREX_STRATEGIES
from edgerunner.strategies.crypto import CRYPTO_STRATEGIES

# Initialize strategy manager
manager = StrategyManager(config)

# List available strategies by asset class
print("Forex strategies:", list(FOREX_STRATEGIES.keys()))
print("Crypto strategies:", list(CRYPTO_STRATEGIES.keys()))
```

### **Run Forex Strategy**
```python
# Run XAUUSD FTMO strategy on MT5
result = manager.start_strategy(
    strategy_name='xauusd_ftmo_1h',
    broker='mt5',
    config={
        'account_key': 'FTMO_LIVE',
        'risk_per_trade': 1.25,
        'max_daily_signals': 10
    }
)
```

### **Run Crypto Strategy**
```python
# Run BTCUSDT strategy on Bybit
result = manager.start_strategy(
    strategy_name='btcusdt_enhanced',
    broker='bybit',
    config={
        'leverage': 1,  # Spot trading
        'risk_per_trade': 2.0
    }
)
```

### **Multi-Asset Portfolio**
```python
# Run strategies across asset classes
strategies = [
    {'name': 'xauusd_ftmo_1h', 'broker': 'mt5', 'allocation': 0.4},
    {'name': 'btcusdt_enhanced', 'broker': 'bybit', 'allocation': 0.3},
    {'name': 'mtum_momentum', 'broker': 'interactive_brokers', 'allocation': 0.3}
]

for strategy in strategies:
    manager.start_strategy(**strategy)
```

## ⚙️ **Configuration Structure**

### **Strategy Configuration** (`config/strategies.yaml`)
```yaml
# Asset class organization
forex:
  xauusd_ftmo_1h:
    name: "XAUUSD FTMO 1H Enhanced"
    broker: "mt5"
    symbol: "XAUUSD"
    timeframe: "1h"
    risk:
      max_daily_loss_pct: 5.0
      max_risk_per_trade: 2.0

crypto:
  btcusdt_enhanced:
    name: "BTCUSDT Enhanced"
    broker: "bybit"
    symbol: "BTCUSDT"
    timeframe: "4h"
```

### **Broker Routing** (`config/webhooks.yaml`)
```yaml
routing:
  strategy_routing:
    "xauusd_ftmo_1h":
      webhook: "cloudflare_webhook"
      account: "FTMO_LIVE"
    
    "btcusdt_enhanced":
      webhook: "bybit_api"
      account: "CRYPTO_LIVE"
```

## 🔗 **Broker Integration**

### **Asset Class → Broker Mapping**
| Asset Class | Primary Broker | Secondary | Integration |
|-------------|----------------|-----------|-------------|
| **Forex** | MT5 | Interactive Brokers | Webhook Bridge |
| **Crypto** | Bybit | MT5 | REST API / Webhook |
| **Stocks** | Interactive Brokers | - | TWS API |
| **Indices** | Interactive Brokers | MT5 | TWS API / Webhook |

### **Symbol Mapping**
Each asset class handles symbol mapping automatically:
```python
# Forex (Edgerunner → MT5)
"XAUUSD" → "XAUUSD"  # Direct mapping
"EURUSD" → "EURUSD"  # Direct mapping

# Crypto (Edgerunner → Bybit/MT5)  
"BTCUSDT" → "BTCUSDT" (Bybit) / "BTCUSD" (MT5)
"ETHUSDT" → "ETHUSDT" (Bybit) / "ETHUSD" (MT5)

# Stocks (Edgerunner → IBKR)
"AAPL" → "AAPL"  # Direct mapping
"SPY" → "SPY"    # Direct mapping
```

## 📈 **Performance Tracking**

### **Asset Class Metrics**
Each asset class tracks specific performance metrics:

- **Forex**: FTMO compliance, daily/overall drawdown
- **Crypto**: Volatility-adjusted returns, correlation with BTC
- **Stocks**: Alpha/Beta vs SPY, sector allocation
- **Indices**: Benchmark tracking, regime detection

### **Monitoring Dashboard**
```python
# Get performance by asset class
performance = manager.get_performance_summary()

print(f"Forex P&L: {performance['forex']['total_pnl']}")
print(f"Crypto P&L: {performance['crypto']['total_pnl']}")
print(f"Stocks P&L: {performance['stocks']['total_pnl']}")
```

## 🚀 **Adding New Strategies**

### **1. Choose Asset Class**
Place new strategy in appropriate folder:
- Forex/metals → `forex/`
- Cryptocurrencies → `crypto/`
- Stocks/ETFs → `stocks/`
- Indices/futures → `indices/`

### **2. Inherit Base Strategy**
```python
from edgerunner.strategies.base import BaseStrategy

class NewForexStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.asset_class = "forex"
        self.broker = "mt5"
    
    def generate_signals(self, data):
        # Strategy logic
        pass
```

### **3. Register Strategy**
Add to appropriate `__init__.py`:
```python
# In forex/__init__.py
from .new_forex_strategy import NewForexStrategy

FOREX_STRATEGIES = {
    'new_forex_strategy': NewForexStrategy,
    # ... existing strategies
}
```

### **4. Configure Strategy**
Add to `config/strategies.yaml`:
```yaml
forex:
  new_forex_strategy:
    name: "New Forex Strategy"
    enabled: true
    broker: "mt5"
    # ... configuration
```

## 🎯 **Benefits of Asset Class Organization**

✅ **Clear Separation** - Easy to find and maintain strategies  
✅ **Broker Optimization** - Each asset class uses optimal broker  
✅ **Risk Management** - Asset-specific risk models  
✅ **Symbol Mapping** - Automatic broker symbol translation  
✅ **Performance Tracking** - Asset class specific metrics  
✅ **Scalability** - Easy to add new strategies and asset classes  
✅ **Configuration** - Organized settings by asset type  

---

**Your strategies are now organized for professional trading across multiple asset classes! 🚀**