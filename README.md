# Edgerunner Trading Framework

🚀 **Production-grade algorithmic trading framework** with multi-venue execution, advanced risk management, and institutional-grade backtesting.

## 📁 Project Structure

```
.
├── edgerunner/              # 🚀 Core trading framework
│   ├── alpha/               # Signal generation
│   ├── strategies/          # Strategy implementations
│   ├── execution/           # Order management
│   ├── brokers/             # Broker connectivity
│   ├── risk/                # Risk management
│   ├── backtest/            # Backtesting engines
│   ├── monitor/             # System monitoring
│   └── reports/             # Report generation
│
├── config/                  # ⚙️ Configuration files
│   ├── brokers.yaml        # Broker settings
│   ├── risk.yaml           # Risk parameters
│   ├── strategy.yaml       # Strategy configs
│   └── environments/       # Environment configs
│
├── data/                    # 📊 Data storage
│   ├── raw/                # Raw market data
│   ├── processed/          # Processed datasets
│   └── cache/              # Data cache
│
├── examples/                # 📚 Example scripts
├── tests/                   # 🧪 Test suite
├── notebooks/               # 📓 Research notebooks
├── docs/                    # 📖 Documentation
├── logs/                    # 📝 Application logs
└── reports/                 # 📈 Generated reports
```

## ⚡ Quick Start

1. **Clone and setup:**
```bash
git clone <repository-url>
cd IB-TRADING
pip install -r requirements_edgerunner.txt
```

2. **Configure:**
```bash
cp .env.sample .env
# Edit .env with your credentials
```

3. **Run:**
```python
from edgerunner import EdgerunnerFramework

framework = EdgerunnerFramework(
    config_path="config/",
    environment="dev"
)
framework.start()
```

## 📊 Key Features

- **Multi-Broker Support**: IBKR, Bybit, MT5
- **Advanced Risk Management**: Kelly criterion, VaR, circuit breakers
- **Professional Reporting**: Interactive HTML with dark/light themes
- **FTMO Compliance**: For proprietary trading
- **Production Ready**: Monitoring, alerts, logging

## 📚 Documentation

- [Quick Start Guide](examples/quick_start.py)
- [Framework Documentation](README_EDGERUNNER.md)
- [API Reference](docs/api/)
- [Strategy Development](docs/strategies/)

## 🚧 Development Status

✅ **Completed:**
- Core framework architecture
- HTML visualization with Plotly
- Risk management system
- Multi-broker support structure

🔄 **In Progress:**
- Strategy implementations
- Live trading connectors
- Advanced backtesting features

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This software is for educational purposes. Trading involves substantial risk of loss.