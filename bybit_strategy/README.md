# Bybit 1H Trend Composite Strategy

A sophisticated cryptocurrency trading strategy based on the successful FTMO 68.4% win rate system, adapted and optimized for 24/7 crypto markets on Bybit exchange.

## Overview

This strategy replicates the proven FTMO trend composite approach with crypto-specific optimizations:

- **Win Rate**: Targeting 60-70% based on FTMO success
- **Risk Management**: 1.5% risk per trade with dynamic position sizing
- **Timeframe**: 1-hour charts for optimal signal quality
- **Markets**: BTC, ETH, SOL, ADA, DOT and more
- **Risk/Reward**: Minimum 1.5:1 ratio per trade

## Features

### Core Components

1. **Trend Composite Indicator**
   - Multi-timeframe EMA alignment (8, 21, 50)
   - RSI momentum confirmation
   - MACD signal validation
   - Volume analysis
   - Volatility filtering

2. **Risk Management**
   - Position sizing based on account risk
   - Dynamic risk adjustment
   - Maximum drawdown protection
   - Kelly Criterion option
   - Multiple position management

3. **API Integration**
   - Full Bybit REST API support
   - Testnet and mainnet compatibility
   - Order management with stops
   - Real-time position tracking

4. **Logging & Monitoring**
   - Trade execution logs
   - Performance metrics tracking
   - Signal history
   - Real-time position monitoring

## Installation

1. Clone the repository:
```bash
cd bybit_strategy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export BYBIT_API_KEY="your_api_key"
export BYBIT_API_SECRET="your_api_secret"
```

## Usage

### Quick Start (Testnet)

```bash
# Scan for signals (testnet, no execution)
python main.py --mode scan

# Monitor with signal execution (testnet)
python main.py --mode trade --execute

# Specific symbols only
python main.py --mode scan --symbols BTC ETH SOL
```

### Live Trading

```bash
# Live trading with execution
python main.py --mode trade --live --execute

# Conservative risk (1% per trade)
python main.py --mode trade --live --execute --risk 1.0
```

### Monitoring

```bash
# Monitor existing positions
python main.py --mode monitor
```

## Configuration

Edit `config/settings.py` to customize:

- **Risk Parameters**
  - `risk_per_trade`: 1.5% default
  - `max_daily_risk`: 5% daily limit
  - `max_positions`: 3 concurrent positions

- **Indicators**
  - EMA periods: 8, 21, 50
  - RSI period: 10
  - MACD: 8, 21, 5

- **Position Sizing**
  - ATR-based stops: 2.5x
  - Take profit: 4.0x ATR
  - Min R:R ratio: 1.5:1

## Strategy Logic

### Entry Conditions

**LONG Signal:**
- EMA 8 > EMA 21 > EMA 50
- Price above EMA 8
- RSI > 50 (preferably > 60)
- MACD above signal line
- Volume confirmation (>1.2x average)
- Trend composite score > 3.0

**SHORT Signal:**
- EMA 8 < EMA 21 < EMA 50
- Price below EMA 8
- RSI < 50 (preferably < 40)
- MACD below signal line
- Volume confirmation
- Trend composite score < -3.0

### Risk Management

1. **Position Sizing**: 
   - Based on stop loss distance
   - Maximum 25% per position
   - Account for leverage

2. **Stop Loss**: 
   - 2.5x ATR from entry
   - Adjusted for volatility

3. **Take Profit**: 
   - 4.0x ATR from entry
   - Minimum 1.5:1 R:R ratio

## Performance Metrics

The strategy tracks:
- Win rate percentage
- Sharpe ratio
- Maximum drawdown
- Daily P&L
- Risk utilization
- Average win/loss ratio

## Directory Structure

```
bybit_strategy/
├── core/
│   ├── strategy.py       # Main strategy logic
│   └── risk_manager.py   # Risk management system
├── indicators/
│   └── trend_composite.py # Technical indicators
├── api/
│   └── bybit_client.py   # Exchange integration
├── config/
│   └── settings.py        # Configuration
├── utils/
│   └── logger.py          # Logging utilities
├── logs/                  # Trading logs
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Safety Features

- **Testnet First**: Always test on testnet before live trading
- **Risk Limits**: Hard stops at 5% daily and 10% total drawdown
- **Position Limits**: Maximum 3 concurrent positions
- **Volatility Filter**: Reduces signals in extreme volatility
- **Signal Cooldown**: 4-hour minimum between signals per symbol

## Disclaimer

This strategy is for educational purposes. Cryptocurrency trading carries substantial risk. Past performance does not guarantee future results. Always test thoroughly on testnet before considering live trading.

## Support

For issues or questions, please check the logs in the `logs/` directory for detailed execution information.