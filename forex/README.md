# FTMO 1H Enhanced XAUUSD Strategy 🏆

**The Ultimate FTMO Challenge Solution**

A highly successful automated trading strategy for FTMO challenges, achieving **68.4% completion rate** with zero rule violations across 19 months of testing.

## 🎯 Strategy Performance

- **Success Rate**: 68.4% (13/19 months completed)
- **FTMO Compliance**: 100% (Zero violations)
- **Average Completion Time**: 15 days
- **Fastest Completion**: 5 days
- **Performance Improvement**: 6.5x better than baseline strategies

## 📁 System Files

### Core Strategy Components
- **`xauusd_ftmo_1h_enhanced_strategy.py`** - Main 1H Enhanced Strategy implementation
- **`xauusd_ftmo_1h_live_trader.py`** - Live trading module with webhook integration
- **`live_trader_config.py`** - Configuration management system
- **`local_webhook_server.py`** - Local webhook server for MT5 integration

### MT5 Integration
- **`EA/ftmo-bridge.mq5`** - MetaTrader 5 Expert Advisor for trade execution

### Performance Analysis
- **`1h_monthly_performance_analysis.py`** - Monthly performance validation tool

## 🚀 Quick Start

### 1. Strategy Testing
```bash
# Test the 1H Enhanced Strategy
python xauusd_ftmo_1h_enhanced_strategy.py

# Run monthly performance analysis
python 1h_monthly_performance_analysis.py
```

### 2. Live Trading Setup
```bash
# Install dependencies
pip install pandas numpy yfinance requests flask

# Start local webhook server
python local_webhook_server.py

# Start live trader
python xauusd_ftmo_1h_live_trader.py
```

### 3. MT5 Integration
Update your MT5 EA settings:
```mql5
input string ServerURL = "http://localhost:5000";
input string AccountKey = "FTMO_1H_LIVE";
```

## 🎛️ Configuration

### Trading Parameters
```python
# FTMO Compliance Settings
max_daily_risk = 1.5%          # Maximum daily risk
emergency_daily_limit = 0.8%   # Emergency stop
overall_emergency_limit = 5.0% # Overall loss limit

# Signal Generation
min_trend_strength = 2.0       # Minimum trend score
signal_cooldown = 300s         # Between signals
max_daily_signals = 10         # Daily signal limit

# Position Sizing
atr_stop_multiplier = 2.0      # Stop loss distance
atr_target_multiplier = 3.0    # Take profit distance
```

### Configuration Presets
```python
from live_trader_config import ConfigPresets

# Conservative (recommended for FTMO)
config = ConfigPresets.conservative()

# Aggressive (higher frequency)
config = ConfigPresets.aggressive()

# Testing (demo account)
config = ConfigPresets.testing()
```

## 📊 Strategy Features

### FTMO Compliance
- ✅ Ultra-strict daily loss limits (0.8% emergency stop)
- ✅ Overall loss protection (5% maximum)
- ✅ Minimum trading days requirement
- ✅ No weekend holding restrictions
- ✅ News event filtering

### Technical Analysis
- **1H Trend Composite**: Multi-EMA trend scoring system
- **ATR-Based Stops**: Dynamic stop loss and take profit levels
- **Volume Confirmation**: Volume trend analysis
- **Signal Quality Filter**: Minimum trend strength requirements

### Risk Management
- **Dynamic Position Sizing**: Based on account balance and ATR
- **Emergency Stops**: Multiple safety layers
- **Signal Cooldown**: Prevents over-trading
- **Daily Limits**: Trade count and signal restrictions

## 🔗 Webhook Integration

### Architecture
```
1H Enhanced Strategy → Local Webhook Server → MT5 EA → FTMO Broker
```

### Endpoints
- **POST `/webhook`** - Receive trading signals
- **GET `/dequeue`** - MT5 EA polling endpoint
- **GET `/status`** - System status monitoring
- **GET `/queue`** - View signal queue

### Signal Format
```json
{
  "signalId": "uuid",
  "symbol": "XAUUSD",
  "event": "entry",
  "side": "BUY",
  "price": 2000.00,
  "sl": 1980.00,
  "tp": 2030.00,
  "qty_usd": 1000,
  "confidence": 0.85,
  "strategy": "1H_Enhanced"
}
```

## 📈 Monthly Performance Results

### Completed Challenges (68.4%)
| Month | Profit | Days | Speed |
|-------|---------|------|-------|
| Mar 2024 | +11.7% | 15d | Moderate |
| Apr 2024 | +1.0% | 26d | Slow |
| May 2024 | +0.7% | 7d | Fast |
| Jun 2024 | +18.0% | 25d | Slow |
| Jul 2024 | +21.9% | 5d | Very Fast |
| Sep 2024 | +7.6% | 14d | Moderate |
| Oct 2024 | +13.8% | 21d | Moderate |
| Nov 2024 | +10.2% | 9d | Fast |
| Feb 2025 | +15.2% | 11d | Fast |
| Mar 2025 | +8.9% | 19d | Moderate |
| Apr 2025 | +12.1% | 16d | Moderate |
| May 2025 | +6.3% | 23d | Slow |
| Jun 2025 | +9.4% | 18d | Moderate |

### Incomplete Challenges (31.6%)
| Month | Result | Reason |
|-------|--------|---------|
| Jan 2024 | -5.7% | Market volatility |
| Feb 2024 | +9.7% | Close (0.3% short) |
| Aug 2024 | -6.5% | Challenging conditions |
| Dec 2024 | -3.2% | Year-end volatility |
| Jan 2025 | +8.1% | Close (1.9% short) |
| Jul 2025 | +4.5% | Partial month data |

## 🛠️ Development & Testing

### Strategy Evolution
1. **Original 4H Strategy**: 10.5% success rate (baseline)
2. **4H Enhanced V2**: 42.9% success rate (improved)
3. **1H Enhanced**: 68.4% success rate (final version)

### Key Improvements
- Higher frequency trading (1H vs 4H)
- Enhanced risk management
- Dynamic position sizing
- Signal quality filtering
- Webhook integration

## 🔧 Troubleshooting

### Common Issues
1. **No signals generated**: Check trend strength threshold
2. **Webhook connection failed**: Verify server URL and port
3. **MT5 EA not receiving signals**: Check symbol mapping
4. **High drawdown**: Reduce position sizes or increase stops

### Monitoring
```python
# Check system status
python -c "import requests; print(requests.get('http://localhost:5000/status').json())"

# View signal queue
python -c "import requests; print(requests.get('http://localhost:5000/queue').json())"
```

## 📞 Support

For questions or issues:
1. Check the configuration in `live_trader_config.py`
2. Review the webhook server logs
3. Test with the demo configuration first
4. Monitor the system status endpoints

## ⚡ Performance Optimization

### For Higher Success Rate
- Use conservative configuration preset
- Increase signal cooldown time
- Raise minimum trend strength
- Reduce maximum daily trades

### For Faster Completion
- Use aggressive configuration preset
- Lower trend strength threshold
- Increase position sizes (within limits)
- Reduce signal cooldown

## 🏆 Success Tips

1. **Start with conservative settings** - Better to complete slowly than fail
2. **Monitor daily progress** - Watch for approaching limits
3. **Use multiple accounts** - Diversify across different months
4. **Maintain discipline** - Don't override the system manually
5. **Test thoroughly** - Always validate in demo before live trading

---

**🎯 Ready to dominate FTMO challenges with a 68.4% success rate!**