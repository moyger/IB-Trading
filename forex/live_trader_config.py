#!/usr/bin/env python3
"""
Live Trading Configuration
Centralized configuration for FTMO 1H Enhanced Live Trading
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class FTMOConfig:
    """FTMO Account Configuration"""
    account_size: int = 100000
    challenge_phase: int = 1  # 1 or 2
    max_daily_risk: float = 1.5  # Maximum daily risk percentage
    emergency_daily_limit: float = 0.8  # Emergency stop at daily loss %
    overall_emergency_limit: float = 5.0  # Emergency stop at overall loss %
    max_daily_trades: int = 15
    max_daily_signals: int = 10

@dataclass 
class WebhookConfig:
    """Webhook Configuration"""
    webhook_url: str = "https://tradingview-webhook.karloestrada.workers.dev/enqueue"
    account_key: str = "FTMO_1H_LIVE"
    timeout_seconds: int = 10
    retry_attempts: int = 3
    retry_delay: int = 5

@dataclass
class TradingConfig:
    """Trading Strategy Configuration"""
    symbol: str = "GC=F"  # Gold futures for yfinance
    mt5_symbol: str = "XAUUSD"  # Symbol sent to MT5
    interval_minutes: int = 5  # How often to check for signals
    signal_cooldown: int = 300  # Minimum seconds between signals
    min_trend_strength: float = 3.0  # Minimum trend score for signal
    atr_stop_multiplier: float = 2.0  # ATR multiplier for stop loss
    atr_target_multiplier: float = 3.0  # ATR multiplier for take profit
    lookback_hours: int = 200  # Hours of data to fetch

@dataclass
class LiveTraderConfig:
    """Complete Live Trader Configuration"""
    ftmo: FTMOConfig
    webhook: WebhookConfig 
    trading: TradingConfig
    
    @classmethod
    def default(cls):
        """Create default configuration"""
        return cls(
            ftmo=FTMOConfig(),
            webhook=WebhookConfig(),
            trading=TradingConfig()
        )
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            ftmo=FTMOConfig(
                account_size=int(os.getenv('FTMO_ACCOUNT_SIZE', 100000)),
                challenge_phase=int(os.getenv('FTMO_CHALLENGE_PHASE', 1)),
                max_daily_risk=float(os.getenv('FTMO_MAX_DAILY_RISK', 1.5)),
                emergency_daily_limit=float(os.getenv('FTMO_EMERGENCY_DAILY_LIMIT', 0.8)),
                overall_emergency_limit=float(os.getenv('FTMO_OVERALL_EMERGENCY_LIMIT', 5.0))
            ),
            webhook=WebhookConfig(
                webhook_url=os.getenv('WEBHOOK_URL', "https://tradingview-webhook.karloestrada.workers.dev/enqueue"),
                account_key=os.getenv('WEBHOOK_ACCOUNT_KEY', "FTMO_1H_LIVE"),
                timeout_seconds=int(os.getenv('WEBHOOK_TIMEOUT', 10))
            ),
            trading=TradingConfig(
                interval_minutes=int(os.getenv('TRADING_INTERVAL_MINUTES', 5)),
                signal_cooldown=int(os.getenv('TRADING_SIGNAL_COOLDOWN', 300)),
                min_trend_strength=float(os.getenv('TRADING_MIN_TREND_STRENGTH', 3.0))
            )
        )

# Pre-configured setups for different scenarios
class ConfigPresets:
    """Pre-configured setups for different trading scenarios"""
    
    @staticmethod
    def conservative():
        """Conservative trading setup"""
        config = LiveTraderConfig.default()
        config.ftmo.max_daily_risk = 1.0
        config.ftmo.emergency_daily_limit = 0.6  
        config.ftmo.max_daily_trades = 10
        config.trading.min_trend_strength = 3.5
        config.trading.signal_cooldown = 600  # 10 minutes
        return config
    
    @staticmethod
    def aggressive():
        """More aggressive trading setup"""
        config = LiveTraderConfig.default()
        config.ftmo.max_daily_risk = 2.0
        config.ftmo.max_daily_trades = 20
        config.trading.min_trend_strength = 2.5
        config.trading.signal_cooldown = 180  # 3 minutes
        return config
    
    @staticmethod
    def testing():
        """Testing/demo setup"""
        config = LiveTraderConfig.default()
        config.ftmo.account_size = 10000
        config.webhook.account_key = "FTMO_1H_TEST"
        config.trading.interval_minutes = 1  # Check every minute
        config.trading.min_trend_strength = 2.0
        return config

def print_config(config: LiveTraderConfig):
    """Print configuration in readable format"""
    print("🔧 LIVE TRADER CONFIGURATION")
    print("=" * 50)
    
    print("\n💼 FTMO Settings:")
    print(f"  Account Size: ${config.ftmo.account_size:,}")
    print(f"  Challenge Phase: {config.ftmo.challenge_phase}")
    print(f"  Max Daily Risk: {config.ftmo.max_daily_risk}%")
    print(f"  Emergency Daily Limit: {config.ftmo.emergency_daily_limit}%")
    print(f"  Overall Emergency Limit: {config.ftmo.overall_emergency_limit}%")
    print(f"  Max Daily Trades: {config.ftmo.max_daily_trades}")
    print(f"  Max Daily Signals: {config.ftmo.max_daily_signals}")
    
    print("\n🔗 Webhook Settings:")
    print(f"  URL: {config.webhook.webhook_url}")
    print(f"  Account Key: {config.webhook.account_key}")
    print(f"  Timeout: {config.webhook.timeout_seconds}s")
    print(f"  Retry Attempts: {config.webhook.retry_attempts}")
    
    print("\n📈 Trading Settings:")
    print(f"  Symbol: {config.trading.symbol} → {config.trading.mt5_symbol}")
    print(f"  Check Interval: {config.trading.interval_minutes} minutes")
    print(f"  Signal Cooldown: {config.trading.signal_cooldown}s")
    print(f"  Min Trend Strength: {config.trading.min_trend_strength}")
    print(f"  Stop Loss: {config.trading.atr_stop_multiplier}x ATR")
    print(f"  Take Profit: {config.trading.atr_target_multiplier}x ATR")
    print(f"  Lookback: {config.trading.lookback_hours} hours")

if __name__ == "__main__":
    """Demo configuration options"""
    print("🎯 CONFIGURATION PRESETS:")
    print("\n1. Conservative (Safe FTMO approach)")
    conservative = ConfigPresets.conservative()
    print_config(conservative)
    
    print("\n" + "="*80)
    print("2. Aggressive (Higher frequency)")
    aggressive = ConfigPresets.aggressive()
    print_config(aggressive)
    
    print("\n" + "="*80)
    print("3. Testing (Demo account)")
    testing = ConfigPresets.testing()
    print_config(testing)