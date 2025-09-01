# 📚 Edgerunner Trading Framework Documentation

Welcome to the comprehensive documentation for the Edgerunner multi-broker trading system. This documentation covers everything from strategy implementation to production deployment.

## 📋 Quick Navigation

### 🚀 **Getting Started**
- [Framework Overview](architecture/FRAMEWORK_GUIDE.md) - Core architecture and components
- [Commands Reference](guides/commands.md) - Available commands and usage

### 🔧 **Deployment & Setup**
- [VPS Deployment Guide](deployment/VPS_DEPLOYMENT_GUIDE.md) - Complete VPS setup instructions
- [Live Trading Setup](deployment/LIVE_TRADING_SETUP_GUIDE.md) - Production deployment checklist
- [Local Live Testing](testing/LOCAL_LIVE_TESTING_GUIDE.md) - Test live trading safely before VPS

### 🎯 **Trading Strategies**
- [Strategy Organization](strategies/STRATEGY_ORGANIZATION.md) - How strategies are structured
- [Arthur Hill MTF Strategy](strategies/ARTHUR_HILL_MTF_STRATEGY_GUIDE.md) - Multi-timeframe crypto strategy
- [Ernest Chan Mean Reversion](strategies/ERNEST_CHAN_STRATEGY_PLACEMENT.md) - FTMO forex strategy
- [FTMO Mean Reversion Guide](strategies/FTMO_MEAN_REVERSION_GUIDE.md) - Detailed FTMO implementation

### 🧪 **Testing & Validation**
- [Local Live Testing Guide](testing/LOCAL_LIVE_TESTING_GUIDE.md) - 4-phase local testing system
- [Minimal Risk Testing](testing/MINIMAL_RISK_LIVE_TEST_GUIDE.md) - Safe live trading validation
- [Simulation-Based Backtesting](backtesting/simulation_based_backtesting.md) - Ernest Chan methodology

### 🔗 **Integrations**
- [Notion Integration](guides/NOTION_INTEGRATION_GUIDE.md) - Connect with Notion for tracking
- [MT5 Webhook Integration](guides/MT5_WEBHOOK_INTEGRATION.md) - MetaTrader 5 connectivity

### 📊 **Analysis & Results**
- [Backtest Results](analysis/BACKTEST_RESULTS.md) - Historical performance analysis
- [Monthly Holdings Analysis](analysis/MONTHLY_HOLDINGS_ANALYSIS.md) - Portfolio analysis
- [MTUM Trading Plan](analysis/MTUM_AUTOMATED_TRADING_PLAN.md) - Momentum strategy analysis

---

## 🏗️ **System Architecture**

The Edgerunner framework supports multi-broker trading across:

| Broker | Market | Capital | Primary Strategies |
|--------|--------|---------|-------------------|
| **IBKR** | Stocks | $50,000 | Nick Radge Momentum |
| **Bybit** | Crypto | $25,000 | Arthur Hill MTF, BTC Enhanced |
| **FTMO MT5** | Forex | $100,000 | Ernest Chan Mean Reversion, XAUUSD |

**Total Portfolio: $175,000**

## 🛡️ **Safety Features**

- ✅ **Multi-phase testing system** (Paper → Micro → Demo → Live)
- ✅ **Real-time risk monitoring** with emergency stops
- ✅ **FTMO compliance** for challenge requirements  
- ✅ **Professional validation** (Academic + Institutional scoring)
- ✅ **Comprehensive logging** and performance tracking

## 🎯 **Key Features**

### **Ernest Chan Methodology**
- Simulation-based backtesting to prevent overfitting
- Statistical significance testing 
- Monte Carlo parameter optimization
- Time series modeling (AR, GARCH, Regime-Switching)

### **Professional Risk Management**
- Individual broker capital allocation
- Dynamic position sizing with Kelly criterion
- Multi-level safety stops and limits
- Real-time performance monitoring

### **Production-Ready**
- VPS deployment scripts and guides
- Local testing framework before going live
- Multi-broker API integration
- Professional logging and alerting

---

## 📖 **Documentation Categories**

### 📂 [Analysis](analysis/)
Performance analysis, backtest results, and trading plans

### 📂 [Architecture](architecture/)  
System design, framework guides, and core concepts

### 📂 [API](api/)
API documentation and integration guides

### 📂 [Backtesting](backtesting/)
Backtesting frameworks, validation methods, and results

### 📂 [Deployment](deployment/)
VPS setup, live trading deployment, and production guides

### 📂 [Guides](guides/)
Integration guides, commands reference, and how-to documentation

### 📂 [Strategies](strategies/)
Strategy implementations, guides, and performance analysis

### 📂 [Testing](testing/)
Testing frameworks, validation procedures, and safety protocols

---

## 🚀 **Quick Start**

1. **Read the Framework Guide**: Start with [Framework Overview](architecture/FRAMEWORK_GUIDE.md)

2. **Set Up Local Testing**: Follow [Local Live Testing Guide](testing/LOCAL_LIVE_TESTING_GUIDE.md)

3. **Deploy to Production**: Use [VPS Deployment Guide](deployment/VPS_DEPLOYMENT_GUIDE.md)

4. **Monitor Performance**: Track results with built-in monitoring tools

---

## 🆘 **Support & Resources**

- **Strategy Questions**: See individual strategy guides in `/strategies`
- **Technical Issues**: Check `/guides` for troubleshooting
- **Deployment Help**: Review `/deployment` documentation
- **Testing Problems**: Follow `/testing` protocols

---

## 📝 **Documentation Standards**

All documentation follows these standards:
- ✅ **Clear headings** and navigation
- ✅ **Code examples** with explanations
- ✅ **Safety warnings** where appropriate
- ✅ **Step-by-step instructions**
- ✅ **Expected outcomes** and validation steps

---

## 🎉 **Latest Updates**

- **Ernest Chan Strategy Integration** - Professional mean reversion strategy for FTMO
- **Local Live Testing System** - 4-phase testing before VPS deployment
- **Multi-Broker Deployment** - Unified system for IBKR, Bybit, and FTMO
- **Enhanced Safety Systems** - Real-time monitoring and emergency stops

---

*Last Updated: September 2025*  
*System Version: Multi-Broker v2.0*

**Ready for professional algorithmic trading! 🚀**