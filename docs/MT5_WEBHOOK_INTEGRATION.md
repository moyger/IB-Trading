# MT5 Webhook Integration Guide

## 🔄 Overview

The Edgerunner framework now integrates your existing **MetaTrader5 EA bridge infrastructure** with **Cloudflare Worker webhooks**, creating a seamless connection between algorithmic strategies and live MT5 execution.

## 🏗️ Architecture Integration

### **Existing Infrastructure** (Preserved & Integrated)
- ✅ **ftmo-bridge.mq5** - Production-ready EA with queue polling
- ✅ **Cloudflare Worker** - `https://tradingview-webhook.karloestrada.workers.dev`
- ✅ **Local Webhook Server** - Flask-based backup system
- ✅ **FTMO Compliance** - Risk management and position sizing
- ✅ **Symbol Mapping** - TradingView → MT5 broker symbols

### **New Edgerunner Components**
- 🆕 **MT5Client** - Webhook-based broker adapter  
- 🆕 **WebhookManager** - Multi-webhook routing and management
- 🆕 **Configuration Integration** - YAML-based setup
- 🆕 **Strategy Routing** - Route different strategies to different accounts

## 📊 Signal Flow

```
Edgerunner Strategy → MT5Client → Cloudflare Worker → ftmo-bridge.mq5 → MT5 Terminal
```

### **Signal Format** (Compatible with existing EA)
```json
{
  "signalId": "uuid-generated-id",
  "timestamp": "2025-01-01T12:00:00Z",
  "account": "EDGERUNNER_MT5",
  "event": "entry",        // "entry" or "exit"
  "symbol": "XAUUSD",      // MT5 broker symbol
  "side": "BUY",           // "BUY" or "SELL" 
  "price": 2000.50,
  "sl": 1980.00,           // Stop loss
  "tp": 2040.00,           // Take profit
  "qty_usd": 1000,         // Position size in USD
  "magic": 123456,         // EA magic number
  "strategy": "Edgerunner"
}
```

## ⚙️ Configuration

### **brokers.yaml**
```yaml
mt5:
  enabled: true
  webhook_url: "https://tradingview-webhook.karloestrada.workers.dev"
  account_key: "EDGERUNNER_MT5"
  webhook_secret: ""  # Set in secrets if required
  magic_number: 123456
  
  # Position sizing (matches ftmo-bridge.mq5)
  use_equity_percent: true
  equity_percent: 1.0  # 1% of equity per trade
  max_lot_size: 0.10
  min_lot_size: 0.01
  
  # Symbol mapping
  symbol_mapping:
    "BTCUSDT": "BTCUSD"
    "XAUUSD": "XAUUSD"
    "EURUSD": "EURUSD"
```

### **webhooks.yaml**
```yaml
cloudflare_webhook:
  enabled: true
  base_url: "https://tradingview-webhook.karloestrada.workers.dev"
  webhook_secret: "${CLOUDFLARE_WEBHOOK_SECRET}"
  
  accounts:
    production:
      account_key: "EDGERUNNER_PROD"
      max_daily_signals: 20
      risk_per_signal: 1.0

# Strategy routing
routing:
  strategy_routing:
    "btcusdt_ftmo":
      webhook: "cloudflare_webhook"
      account: "production"
```

## 🚀 Usage Examples

### **Basic MT5 Order Placement**
```python
from edgerunner.brokers.mt5_client import MT5Client

# Initialize
config = {
    'webhook_url': 'https://tradingview-webhook.karloestrada.workers.dev',
    'account_key': 'EDGERUNNER_MT5',
    'magic_number': 123456
}

mt5_client = MT5Client(config)

# Connect and test
if mt5_client.connect():
    # Place order
    result = mt5_client.place_order(
        symbol='XAUUSD',
        side='BUY',
        quantity=1000,  # USD
        price=2000.00,
        stop_loss=1980.00,
        take_profit=2040.00
    )
    
    if result['success']:
        print(f"Order placed: {result['signal_id']}")
        
        # Close position later
        mt5_client.close_position(result['signal_id'])
```

### **Strategy Integration**
```python
from edgerunner import EdgerunnerFramework

# Initialize framework with MT5 enabled
framework = EdgerunnerFramework(
    config_path="config/",
    environment="prod"
)

# Strategy will automatically route to MT5 via webhook
strategy_result = framework.run_strategy(
    strategy_name="btcusdt_ftmo",
    broker="mt5"  # Routes to MT5 via webhook
)
```

## 🔧 MT5 Terminal Setup

### **1. Install ftmo-bridge.mq5**
1. Copy `archive/forex/EA/ftmo-bridge.mq5` to MT5 `Experts` folder
2. Compile in MetaEditor
3. Attach to any chart (symbol doesn't matter)

### **2. EA Configuration**
```
ServerURL: https://tradingview-webhook.karloestrada.workers.dev
AccountKey: EDGERUNNER_MT5
MaxRiskPct: 0.5
PollMs: 1000

UseEquityPercent: true
EquityPercent: 1.0
MaxLotSize: 0.10
MinLotSize: 0.01
```

### **3. Verify Connection**
- EA should show "FTMO Bridge EA started" in terminal
- Check webhook connectivity in Expert tab
- Monitor for "Signal processed" messages

## 🛡️ Risk Management Features

### **FTMO Compliance** (Built into EA)
- ✅ Daily risk limits (1.5% default)
- ✅ Emergency stops (0.8% daily, 5% overall)
- ✅ Maximum daily trades (15 default)
- ✅ Signal cooldown (5 minutes)
- ✅ Duplicate signal prevention

### **Position Sizing Options**
1. **Fixed Lot** - Use fixed lot size (0.01, 0.02, etc.)
2. **Equity Percentage** - Risk % of equity per trade
3. **USD Amount** - Position size based on USD value
4. **Risk-Based** - Calculate lot size from stop distance

## 📈 Monitoring & Health Checks

### **Webhook Health**
```python
from edgerunner.brokers.webhook_manager import WebhookManager

webhook_manager = WebhookManager(config)

# Check all webhook health
health = webhook_manager.check_webhook_health()
print(f"Cloudflare status: {health['cloudflare']['status']}")

# Test connectivity
success = mt5_client.test_webhook_connection()
```

### **Signal Queue Status**
```python
# Check queue status
status = webhook_manager.get_signal_queue_status()
print(f"Queue size: {status['queue_size']}")
print(f"Active signals: {status['active_signals']}")
```

## 🔄 Signal Routing

### **Strategy-Based Routing**
Different strategies can route to different MT5 accounts:

```yaml
routing:
  strategy_routing:
    "conservative_strategy":
      webhook: "cloudflare_webhook"
      account: "CONSERVATIVE_ACCOUNT"
      
    "aggressive_strategy":
      webhook: "cloudflare_webhook" 
      account: "AGGRESSIVE_ACCOUNT"
```

### **Fallback System**
If primary webhook fails, automatically try backup:

```yaml
fallback:
  primary: "cloudflare_webhook"
  secondary: "local_webhook"
  retry_on_failure: true
```

## 🚨 Troubleshooting

### **Common Issues**

1. **"MT5 webhook connection failed"**
   - Check Cloudflare Worker URL accessibility
   - Verify internet connection
   - Test webhook URL in browser

2. **"Signal not processed by EA"**
   - Ensure EA is running and attached to chart
   - Check AccountKey matches configuration
   - Verify Allow WebRequest is enabled in MT5

3. **"Invalid lot size calculated"**
   - Check symbol minimum/maximum lot sizes
   - Verify equity percentage settings
   - Review stop loss distance calculation

### **Debug Steps**
1. Test webhook with `examples/mt5_integration_demo.py`
2. Check MT5 Expert tab for EA messages
3. Verify Cloudflare Worker logs (if accessible)
4. Monitor signal queue status

## 📋 Production Checklist

- [ ] **MT5 Terminal** running with ftmo-bridge.mq5
- [ ] **Cloudflare Worker** accessible and responding
- [ ] **Account keys** configured correctly
- [ ] **Symbol mapping** matches broker symbols  
- [ ] **Risk limits** set appropriately
- [ ] **Webhook secrets** configured (if using authentication)
- [ ] **Internet connection** stable for webhook calls
- [ ] **MT5 AutoTrading** enabled
- [ ] **WebRequest** allowed for EA URL

## 🎯 Integration Benefits

✅ **Preserves Existing Infrastructure** - No changes to proven EA or Cloudflare Worker  
✅ **FTMO Compliant** - Built-in risk management for prop trading  
✅ **Multi-Strategy Support** - Route different strategies to different accounts  
✅ **Robust Error Handling** - Retry logic and fallback systems  
✅ **Real-time Monitoring** - Health checks and queue status  
✅ **Production Ready** - Thoroughly tested webhook bridge  

## 🔗 Related Files

- **MT5 Client**: `edgerunner/brokers/mt5_client.py`
- **Webhook Manager**: `edgerunner/brokers/webhook_manager.py`
- **EA Bridge**: `archive/forex/EA/ftmo-bridge.mq5`
- **Configuration**: `config/brokers.yaml`, `config/webhooks.yaml`
- **Demo**: `examples/mt5_integration_demo.py`

---

**Your existing MT5 infrastructure is now seamlessly integrated with the Edgerunner framework! 🚀**