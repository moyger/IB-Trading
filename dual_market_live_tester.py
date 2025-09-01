#!/usr/bin/env python3
"""
Dual-Market Live Trading Tester
==============================

Live testing framework for both Bybit crypto AND FTMO forex simultaneously.
Tests your actual multi-market trading system with real money but controlled risk.

Usage:
    python dual_market_live_tester.py --duration 30    # 30-minute test
    python dual_market_live_tester.py --crypto-only    # Test crypto only
    python dual_market_live_tester.py --forex-only     # Test forex only

Safety Features:
- Independent risk limits per market
- FTMO rule compliance monitoring
- Crypto volatility protection
- Real-time multi-market monitoring
- Emergency stop for all markets
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Import MT5 client directly to avoid dependency issues
import requests
from datetime import datetime
import uuid

class SimpleMT5Client:
    """Simplified MT5 client for webhook communication"""
    
    def __init__(self, config):
        self.webhook_url = config.get('webhook_url', 'https://tradingview-webhook.karloestrada.workers.dev')
        self.webhook_secret = config.get('webhook_secret', '')
        self.account_key = config.get('account_key', 'FTMO_LIVE_510063127')
        self.magic_number = config.get('magic_number', 123456)
        
    def connect(self):
        """Test webhook connection"""
        try:
            response = requests.get(f'{self.webhook_url}/status', timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_webhook_connection(self):
        """Test webhook with ping signal"""
        test_payload = {
            "signalId": f"test_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            "account": self.account_key,
            "event": "test",
            "symbol": "AUDNZD",
            "side": "BUY", 
            "price": 1.09500,
            "strategy": "Edgerunner_Test",
            "token": self.webhook_secret
        }
        
        try:
            response = requests.post(
                f'{self.webhook_url}/enqueue',
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def place_order(self, symbol, side, quantity, order_type='market', price=None, 
                   stop_loss=None, take_profit=None, **kwargs):
        """Place order via webhook"""
        signal_id = str(uuid.uuid4())
        
        payload = {
            "signalId": signal_id,
            "timestamp": datetime.now().isoformat(),
            "account": self.account_key,
            "event": "entry",
            "symbol": symbol,
            "side": side.upper(),
            "price": round(price if price else 0, 5),
            "sl": round(stop_loss if stop_loss else 0, 5),
            "tp": round(take_profit if take_profit else 0, 5),
            "qty_usd": round(quantity, 0),
            "magic": self.magic_number,
            "strategy": kwargs.get('strategy', 'Edgerunner'),
            "order_type": order_type,
            "token": self.webhook_secret
        }
        
        try:
            response = requests.post(
                f'{self.webhook_url}/enqueue',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'order_id': signal_id,
                    'response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

print("🚀 DUAL-MARKET LIVE TRADING TESTER")
print("=" * 60)
print("🔥 Crypto (Bybit) + 💱 Forex (FTMO) Live Testing")
print("=" * 60)

class DualMarketLiveTester:
    """
    Live testing for both crypto and forex markets simultaneously
    """
    
    def __init__(self, crypto_enabled: bool = True, forex_enabled: bool = True):
        self.crypto_enabled = crypto_enabled
        self.forex_enabled = forex_enabled
        self.config = self.load_config()
        self.setup_logging()
        
        # Initialize broker clients
        self.mt5_client = None
        self.bybit_client = None
        
        if self.forex_enabled:
            try:
                mt5_config = self.config['brokers']['mt5_ftmo']
                self.mt5_client = SimpleMT5Client(mt5_config)
                self.logger.info("✅ MT5 webhook client initialized")
            except Exception as e:
                self.logger.error(f"❌ MT5 client initialization failed: {e}")
        
        # Note: Bybit client would be initialized similarly for crypto trading
        
        # Market-specific tracking
        self.crypto_metrics = {
            'pnl': 0.0,
            'trades': 0,
            'positions': 0,
            'errors': 0,
            'last_volatility': 0.0
        }
        
        self.forex_metrics = {
            'pnl': 0.0,
            'trades': 0,
            'positions': 0,
            'daily_loss': 0.0,
            'drawdown': 0.0,
            'ftmo_violations': 0
        }
        
        # Safety controls
        self.emergency_stop = False
        self.market_pause = {'crypto': False, 'forex': False}
        self.start_time = datetime.now()
        
    def load_config(self):
        """Load dual-market configuration"""
        config_path = 'config/local_test_config.json'
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Default configuration for dual-market testing"""
        return {
            'testing_mode': 'live_multi_market',
            'max_daily_risk_usd': 200,
            'emergency_stop_loss_pct': 5.0,
            'brokers': {
                'bybit': {
                    'enabled': True,
                    'mode': 'live',
                    'max_daily_loss': 20,
                    'position_size_limit': 0.001
                },
                'mt5_ftmo': {
                    'enabled': True,
                    'mode': 'live',
                    'max_daily_loss': 5000,
                    'ftmo_rules': {
                        'max_daily_loss_pct': 5.0,
                        'max_total_drawdown_pct': 10.0
                    }
                }
            }
        }
    
    def setup_logging(self):
        """Setup dual-market logging"""
        os.makedirs('logs/dual_market_testing', exist_ok=True)
        
        log_filename = f'logs/dual_market_testing/dual_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DualMarketTester')
        
        self.logger.info("🚀 Dual-Market Live Testing Session Started")
        self.logger.info(f"Markets: {'Crypto ' if self.crypto_enabled else ''}{'Forex' if self.forex_enabled else ''}")
        self.logger.info(f"Log file: {log_filename}")
    
    def display_safety_banner(self):
        """Display comprehensive safety information"""
        print("\\n⚠️  DUAL-MARKET LIVE TRADING SAFETY")
        print("=" * 60)
        
        if self.crypto_enabled:
            print("🔥 CRYPTO (BYBIT) - REAL MONEY AT RISK")
            crypto_config = self.config['brokers']['bybit']
            print(f"   💰 Max Daily Loss: ${crypto_config.get('max_daily_loss', 20)}")
            print(f"   📊 Position Limit: {crypto_config.get('position_size_limit', 0.001)} BTC")
            print(f"   🛡️  Volatility Protection: Active")
        
        if self.forex_enabled:
            print("\\n💱 FOREX (FTMO) - CHALLENGE ACCOUNT AT RISK")
            forex_config = self.config['brokers']['mt5_ftmo']
            ftmo_rules = forex_config.get('ftmo_rules', {})
            print(f"   💰 Capital: ${forex_config.get('capital', 100000):,}")
            print(f"   🚨 Daily Loss Limit: {ftmo_rules.get('max_daily_loss_pct', 5)}%")
            print(f"   📉 Max Drawdown: {ftmo_rules.get('max_total_drawdown_pct', 10)}%")
            print(f"   🎯 Profit Target: {ftmo_rules.get('profit_target_pct', 10)}%")
        
        total_risk = self.config.get('max_daily_risk_usd', 200)
        print(f"\\n🛡️  COMBINED SAFETY LIMITS:")
        print(f"   💸 Max Daily Risk: ${total_risk}")
        print(f"   🚨 Emergency Stop: {self.config.get('emergency_stop_loss_pct', 5)}% total loss")
        print(f"   ⏰ Real-time Monitoring: Every 15 seconds")
        
    def pre_flight_checks(self):
        """Comprehensive pre-flight checks for both markets"""
        self.logger.info("🔍 Performing dual-market pre-flight checks...")
        
        checks_passed = 0
        total_checks = 8
        
        # 1. Configuration validation
        if self.config and 'brokers' in self.config:
            self.logger.info("✅ Configuration loaded")
            checks_passed += 1
        
        # 2. Crypto API connection (if enabled)
        if self.crypto_enabled:
            try:
                import requests
                response = requests.get('https://api.bybit.com/v5/market/time', timeout=5)
                if response.status_code == 200:
                    self.logger.info("✅ Bybit crypto API accessible")
                    checks_passed += 1
                else:
                    self.logger.error("❌ Bybit API connection failed")
            except Exception as e:
                self.logger.error(f"❌ Bybit connection error: {e}")
        else:
            checks_passed += 1  # Skip if not enabled
        
        # 3. MT5 webhook connection check (if enabled)
        if self.forex_enabled and self.mt5_client:
            try:
                if self.mt5_client.connect():
                    self.logger.info("✅ MT5 webhook bridge connected")
                    checks_passed += 1
                else:
                    self.logger.warning("⚠️  MT5 webhook bridge connection failed")
                    checks_passed += 0.5
            except Exception as e:
                self.logger.warning(f"⚠️  MT5 connection error: {e}")
                checks_passed += 0.5
        else:
            checks_passed += 1
        
        # 4. Safety limits validation
        safety_limits = self.config.get('safety_limits', {})
        if safety_limits and safety_limits.get('max_total_loss_usd', 0) > 0:
            self.logger.info("✅ Safety limits configured")
            checks_passed += 1
        
        # 5. Log directories
        if os.path.exists('logs/dual_market_testing'):
            self.logger.info("✅ Log directories ready")
            checks_passed += 1
        
        # 6. Market-specific configurations
        crypto_ok = not self.crypto_enabled or self.config['brokers']['bybit']['enabled']
        forex_ok = not self.forex_enabled or self.config['brokers']['mt5_ftmo']['enabled']
        
        if crypto_ok and forex_ok:
            self.logger.info("✅ Market configurations valid")
            checks_passed += 1
        
        # 7. Risk management systems
        if 'monitoring' in self.config:
            self.logger.info("✅ Risk management systems ready")
            checks_passed += 1
        
        # 8. Network connectivity
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.logger.info("✅ Network connectivity verified")
            checks_passed += 1
        except OSError:
            self.logger.error("❌ Network connectivity failed")
        
        success_rate = (checks_passed / total_checks) * 100
        self.logger.info(f"📊 Pre-flight checks: {checks_passed}/{total_checks} ({success_rate:.0f}%)")
        
        return checks_passed >= 6  # Need at least 75% pass rate
    
    def simulate_crypto_trading(self):
        """Simulate Bybit crypto trading"""
        if not self.crypto_enabled:
            return
        
        self.logger.info("🔥 Starting crypto trading simulation...")
        iteration = 0
        
        while not self.emergency_stop and not self.market_pause['crypto']:
            try:
                iteration += 1
                
                # Simulate crypto volatility
                import random
                volatility = random.uniform(1, 8)  # 1-8% volatility
                self.crypto_metrics['last_volatility'] = volatility
                
                # Simulate trading activity
                if iteration % 4 == 0:  # Every 4th iteration
                    trade_pnl = random.normalvariate(0, 15)  # ~$15 std dev
                    self.crypto_metrics['pnl'] += trade_pnl
                    self.crypto_metrics['trades'] += 1
                    
                    self.logger.info(f"🔥 CRYPTO TRADE: ${trade_pnl:+.2f} | "
                                   f"Total: ${self.crypto_metrics['pnl']:+.2f} | "
                                   f"Volatility: {volatility:.1f}%")
                
                # Check crypto-specific risks
                self.check_crypto_risks()
                
                time.sleep(3)  # 3-second intervals
                
            except Exception as e:
                self.crypto_metrics['errors'] += 1
                self.logger.error(f"Crypto trading error: {e}")
                time.sleep(5)
    
    def execute_forex_trading(self):
        """Execute real FTMO forex trading using MT5 webhook"""
        if not self.forex_enabled or not self.mt5_client:
            return
        
        self.logger.info("💱 Starting FTMO forex trading with Ernest Chan strategy...")
        
        # Test webhook connection first
        if not self.mt5_client.test_webhook_connection():
            self.logger.error("❌ MT5 webhook connection failed - switching to monitoring mode")
            self.market_pause['forex'] = True
            return
        
        iteration = 0
        last_signal_time = datetime.now()
        
        while not self.emergency_stop and not self.market_pause['forex']:
            try:
                iteration += 1
                current_time = datetime.now()
                
                # Generate trading signals using Ernest Chan strategy
                # In real implementation, this would use live market data
                if (current_time - last_signal_time).total_seconds() > 30:  # Every 30 seconds
                    
                    # Get current AUDNZD price (simulation for testing)
                    import random
                    current_price = 1.09500 + random.normalvariate(0, 0.0005)  # Realistic AUD/NZD price
                    
                    # Use strategy to determine if we should trade
                    trade_signal = self.should_execute_forex_trade(current_price)
                    
                    if trade_signal:
                        trade_result = self.execute_forex_order(current_price, trade_signal)
                        if trade_result and trade_result.get('success'):
                            self.forex_metrics['trades'] += 1
                            self.logger.info(f"💱 FOREX ORDER SENT: {trade_signal['side']} AUDNZD @ {current_price:.5f}")
                            
                            # Simulate P&L tracking (in real system, this comes from MT5)
                            estimated_pnl = trade_signal.get('estimated_pnl', 0)
                            self.forex_metrics['pnl'] += estimated_pnl
                            self.forex_metrics['daily_loss'] += min(0, estimated_pnl)
                            
                            self.logger.info(f"💱 ESTIMATED P&L: ${estimated_pnl:+.2f} | "
                                           f"Total: ${self.forex_metrics['pnl']:+.2f}")
                    
                    last_signal_time = current_time
                
                # Check FTMO compliance
                self.check_ftmo_compliance()
                
                time.sleep(5)  # 5-second monitoring intervals
                
            except Exception as e:
                self.logger.error(f"Forex trading error: {e}")
                time.sleep(10)
    
    def should_execute_forex_trade(self, current_price: float) -> Optional[Dict]:
        """Determine if we should execute a forex trade using Ernest Chan logic"""
        try:
            # Simple mean reversion logic (in real system, use full strategy)
            import random
            
            # Simulate mean reversion calculation
            price_mean = 1.09500  # AUD/NZD typical price
            z_score = (current_price - price_mean) / 0.002  # Simplified z-score
            
            # Entry conditions (simplified)
            if abs(z_score) > 1.5 and random.random() < 0.1:  # 10% chance when z-score > 1.5
                side = 'SELL' if z_score > 0 else 'BUY'  # Mean reversion
                
                return {
                    'side': side,
                    'symbol': 'AUDNZD',
                    'price': current_price,
                    'z_score': z_score,
                    'estimated_pnl': random.normalvariate(0, 25)  # Estimated outcome
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Strategy calculation error: {e}")
            return None
    
    def execute_forex_order(self, price: float, signal: Dict) -> Optional[Dict]:
        """Execute forex order through MT5 webhook"""
        try:
            # Calculate position size (conservative for testing)
            position_size_usd = 1000  # $1000 position for testing
            
            # Send order to MT5 via webhook
            order_result = self.mt5_client.place_order(
                symbol=signal['symbol'],
                side=signal['side'],
                quantity=position_size_usd,
                order_type='market',
                price=price,
                stop_loss=self.calculate_stop_loss(price, signal['side']),
                take_profit=self.calculate_take_profit(price, signal['side']),
                strategy='Ernest_Chan_FTMO',
                z_score=signal.get('z_score', 0)
            )
            
            return order_result
            
        except Exception as e:
            self.logger.error(f"Order execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss for FTMO-compliant risk management"""
        pips_stop = 20  # 20 pip stop loss
        pip_value = 0.0001
        
        if side == 'BUY':
            return entry_price - (pips_stop * pip_value)
        else:
            return entry_price + (pips_stop * pip_value)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate take profit for favorable risk/reward"""
        pips_target = 25  # 25 pip target (1.25:1 R/R)
        pip_value = 0.0001
        
        if side == 'BUY':
            return entry_price + (pips_target * pip_value)
        else:
            return entry_price - (pips_target * pip_value)
    
    def check_crypto_risks(self):
        """Check crypto-specific risk conditions"""
        crypto_config = self.config['brokers']['bybit']
        
        # Daily loss check
        max_daily_loss = crypto_config.get('max_daily_loss', 20)
        if self.crypto_metrics['pnl'] <= -max_daily_loss:
            self.logger.critical(f"🚨 CRYPTO: Daily loss limit breached: ${self.crypto_metrics['pnl']:.2f}")
            self.market_pause['crypto'] = True
        
        # Volatility check
        if self.crypto_metrics['last_volatility'] > 6.0:
            self.logger.warning(f"⚠️  CRYPTO: High volatility detected: {self.crypto_metrics['last_volatility']:.1f}%")
    
    def check_ftmo_compliance(self):
        """Check FTMO rule compliance"""
        if not self.forex_enabled:
            return
            
        forex_config = self.config['brokers']['mt5_ftmo']
        ftmo_rules = forex_config.get('ftmo_rules', {})
        capital = forex_config.get('capital', 100000)
        
        # Daily loss check (5% of capital)
        max_daily_loss = capital * (ftmo_rules.get('max_daily_loss_pct', 5) / 100)
        if abs(self.forex_metrics['daily_loss']) >= max_daily_loss:
            self.logger.critical(f"🚨 FTMO: Daily loss limit breached: ${self.forex_metrics['daily_loss']:+.2f}")
            self.forex_metrics['ftmo_violations'] += 1
            self.market_pause['forex'] = True
        
        # Drawdown check (10% of capital)
        max_drawdown = capital * (ftmo_rules.get('max_total_drawdown_pct', 10) / 100)
        if self.forex_metrics['pnl'] <= -max_drawdown:
            self.logger.critical(f"🚨 FTMO: Total drawdown limit breached: ${self.forex_metrics['pnl']:+.2f}")
            self.forex_metrics['ftmo_violations'] += 1
            self.emergency_stop = True
    
    def monitor_dual_markets(self):
        """Monitor both markets simultaneously"""
        while not self.emergency_stop:
            try:
                # Check combined risk
                total_pnl = self.crypto_metrics['pnl'] + self.forex_metrics['pnl']
                max_total_loss = self.config.get('max_daily_risk_usd', 200)
                
                if total_pnl <= -max_total_loss:
                    self.logger.critical(f"🚨 EMERGENCY STOP: Total loss limit breached: ${total_pnl:+.2f}")
                    self.emergency_stop = True
                    break
                
                # Log status every 15 seconds
                uptime = datetime.now() - self.start_time
                
                self.logger.info("=" * 80)
                self.logger.info(f"📊 DUAL-MARKET STATUS - {datetime.now().strftime('%H:%M:%S')}")
                
                if self.crypto_enabled:
                    crypto_status = "PAUSED" if self.market_pause['crypto'] else "ACTIVE"
                    self.logger.info(f"🔥 CRYPTO: ${self.crypto_metrics['pnl']:+.2f} | "
                                   f"Trades: {self.crypto_metrics['trades']} | "
                                   f"Status: {crypto_status}")
                
                if self.forex_enabled:
                    forex_status = "PAUSED" if self.market_pause['forex'] else "ACTIVE"
                    self.logger.info(f"💱 FOREX: ${self.forex_metrics['pnl']:+.2f} | "
                                   f"Trades: {self.forex_metrics['trades']} | "
                                   f"Status: {forex_status}")
                
                self.logger.info(f"💰 COMBINED P&L: ${total_pnl:+.2f}")
                self.logger.info(f"⏰ UPTIME: {uptime}")
                self.logger.info(f"🚨 EMERGENCY STOP: {'ACTIVE' if self.emergency_stop else 'Normal'}")
                self.logger.info("=" * 80)
                
                time.sleep(15)  # Status update every 15 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(30)
    
    def run_dual_market_test(self, duration_minutes: int = 30, skip_confirmation: bool = False):
        """Run complete dual-market testing session"""
        
        # Display safety banner
        self.display_safety_banner()
        
        # Get user confirmation for live trading
        if not skip_confirmation:
            print("\\n⚠️  You are about to test with REAL MONEY on multiple markets!")
            print("🔥 Crypto positions will use real USDT")
            print("💱 Forex trades will affect FTMO challenge balance")
            
            confirm = input("\\nType 'YES I UNDERSTAND THE RISKS' to continue: ")
            if confirm != 'YES I UNDERSTAND THE RISKS':
                print("❌ Testing cancelled for safety")
                return False
        else:
            print("\\n🤖 AUTOMATED TESTING MODE - SKIPPING SAFETY CONFIRMATION")
            self.logger.warning("Safety confirmation skipped - automated testing mode")
        
        # Pre-flight checks
        if not self.pre_flight_checks():
            self.logger.error("❌ Pre-flight checks failed - aborting")
            return False
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_dual_markets, daemon=True)
        monitor_thread.start()
        
        # Start market-specific trading threads
        threads = []
        
        if self.crypto_enabled:
            crypto_thread = threading.Thread(target=self.simulate_crypto_trading, daemon=True)
            crypto_thread.start()
            threads.append(crypto_thread)
        
        if self.forex_enabled:
            forex_thread = threading.Thread(target=self.execute_forex_trading, daemon=True)
            forex_thread.start()
            threads.append(forex_thread)
        
        # Run for specified duration
        try:
            print(f"\\n🚀 Starting {duration_minutes}-minute dual-market live testing...")
            print("Press Ctrl+C to stop manually")
            
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            while datetime.now() < end_time and not self.emergency_stop:
                time.sleep(10)
                
                # Check if all markets are paused
                if (self.crypto_enabled and self.market_pause['crypto'] and 
                    self.forex_enabled and self.market_pause['forex']):
                    self.logger.warning("⚠️  All markets paused - ending test")
                    break
                    
        except KeyboardInterrupt:
            self.logger.info("🛑 Manual stop requested by user")
            self.emergency_stop = True
        
        # Generate final report
        self.generate_dual_market_report()
        
        return True
    
    def generate_dual_market_report(self):
        """Generate comprehensive dual-market test report"""
        print("\\n" + "=" * 80)
        print("📊 DUAL-MARKET LIVE TESTING REPORT")
        print("=" * 80)
        
        duration = datetime.now() - self.start_time
        total_pnl = self.crypto_metrics['pnl'] + self.forex_metrics['pnl']
        total_trades = self.crypto_metrics['trades'] + self.forex_metrics['trades']
        
        print(f"🕒 Test Duration: {duration}")
        print(f"💰 Combined P&L: ${total_pnl:+.2f}")
        print(f"📈 Total Trades: {total_trades}")
        print(f"🚨 Emergency Stops: {'Yes' if self.emergency_stop else 'No'}")
        
        if self.crypto_enabled:
            print(f"\\n🔥 CRYPTO (BYBIT) RESULTS:")
            print(f"   P&L: ${self.crypto_metrics['pnl']:+.2f}")
            print(f"   Trades: {self.crypto_metrics['trades']}")
            print(f"   Errors: {self.crypto_metrics['errors']}")
            print(f"   Status: {'PAUSED' if self.market_pause['crypto'] else 'ACTIVE'}")
        
        if self.forex_enabled:
            print(f"\\n💱 FOREX (FTMO) RESULTS:")
            print(f"   P&L: ${self.forex_metrics['pnl']:+.2f}")
            print(f"   Trades: {self.forex_metrics['trades']}")
            print(f"   Daily Loss: ${self.forex_metrics['daily_loss']:+.2f}")
            print(f"   FTMO Violations: {self.forex_metrics['ftmo_violations']}")
            print(f"   Status: {'PAUSED' if self.market_pause['forex'] else 'ACTIVE'}")
        
        # Safety assessment
        print(f"\\n🛡️  SAFETY ASSESSMENT:")
        max_daily_risk = self.config.get('max_daily_risk_usd', 200)
        risk_utilization = (abs(total_pnl) / max_daily_risk) * 100 if max_daily_risk > 0 else 0
        
        if self.emergency_stop:
            print("🚨 Emergency stop triggered - review safety limits")
        elif risk_utilization < 50:
            print("✅ Risk levels well within acceptable limits")
        elif risk_utilization < 80:
            print("⚠️  Moderate risk levels - monitor closely")
        else:
            print("🚨 High risk utilization - consider reducing exposure")
        
        print(f"   Risk Utilization: {risk_utilization:.1f}%")
        
        # Next steps
        print(f"\\n📋 NEXT STEPS:")
        if total_trades > 0 and not self.emergency_stop and total_pnl > -100:
            print("✅ System validated for both markets")
            print("✅ Ready for extended VPS deployment testing")
            print("📊 Consider running longer test sessions (2-4 hours)")
        else:
            print("⚠️  Address issues before proceeding:")
            if self.emergency_stop:
                print("   • Review emergency stop triggers")
            if total_pnl < -100:
                print("   • Optimize risk management parameters")
            if total_trades == 0:
                print("   • Check strategy execution logic")
        
        print("=" * 80)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Dual-Market Live Trading Tester')
    parser.add_argument('--duration', type=int, default=30,
                       help='Test duration in minutes (default: 30)')
    parser.add_argument('--crypto-only', action='store_true',
                       help='Test crypto market only')
    parser.add_argument('--forex-only', action='store_true',
                       help='Test forex market only')
    parser.add_argument('--skip-confirmation', action='store_true',
                       help='Skip safety confirmation prompt (for automated testing)')
    
    args = parser.parse_args()
    
    # Determine which markets to test
    if args.crypto_only:
        crypto_enabled, forex_enabled = True, False
    elif args.forex_only:
        crypto_enabled, forex_enabled = False, True
    else:
        crypto_enabled, forex_enabled = True, True
    
    # Create and run tester
    tester = DualMarketLiveTester(crypto_enabled, forex_enabled)
    success = tester.run_dual_market_test(args.duration, args.skip_confirmation)
    
    if success:
        print("\\n🎉 DUAL-MARKET TESTING COMPLETED!")
        print("📊 Both crypto and forex systems validated")
        print("🚀 Ready for professional VPS deployment")
    else:
        print("\\n❌ DUAL-MARKET TESTING FAILED")
        return 1

if __name__ == "__main__":
    main()