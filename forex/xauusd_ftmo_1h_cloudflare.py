#!/usr/bin/env python3
"""
FTMO 1H Enhanced Strategy - Cloudflare Worker Edition
Production-ready live trading with your Cloudflare Worker webhook
"""

import pandas as pd
import numpy as np
import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

from xauusd_ftmo_1h_enhanced_strategy import XAUUSDFTMO1HEnhancedStrategy
from cloudflare_config import CloudflarePresets, CloudflareWebhookConfig

class FTMO1HCloudflareTrader(XAUUSDFTMO1HEnhancedStrategy):
    """
    Production live trader using Cloudflare Worker webhook
    """
    
    def __init__(self, config=None):
        """Initialize with Cloudflare configuration"""
        
        # Use provided config or default to production
        if config is None:
            config = CloudflarePresets.production()
        
        self.config = config
        self.webhook_config = config.webhook
        
        # Initialize parent strategy
        super().__init__(
            account_size=config.account_size,
            challenge_phase=config.challenge_phase,
            enable_economic_filter=True
        )
        
        # Live trading settings from config
        self.min_trend_strength = config.min_trend_strength
        self.signal_cooldown = config.signal_cooldown
        self.max_daily_signals = config.max_daily_signals
        self.max_daily_trades = config.max_daily_trades
        
        # Tracking
        self.last_signal_time = None
        self.daily_signal_count = 0
        self.last_signal_date = None
        self.active_signals = {}
        self.signal_history = []
        
        print("🌐 FTMO 1H CLOUDFLARE TRADER INITIALIZED")
        print(f"💼 Account Size: ${config.account_size:,}")
        print(f"📊 Challenge Phase: {config.challenge_phase}")
        print(f"🔗 Cloudflare Worker: {self.webhook_config.base_url}")
        print(f"🎯 Account Key: {self.webhook_config.account_key}")
        print(f"⚠️ Daily Risk Limit: {config.max_daily_risk}%")
        print(f"🛑 Emergency Limits: {config.emergency_daily_limit}% daily, {config.overall_emergency_limit}% overall")
    
    def check_trading_conditions(self):
        """Check if trading conditions are met"""
        current_time = datetime.now()
        
        # Reset daily counters
        if self.last_signal_date != current_time.date():
            self.daily_signal_count = 0
            self.last_signal_date = current_time.date()
            print(f"📅 New trading day: {current_time.date()}")
        
        # Check limits
        if self.daily_signal_count >= self.max_daily_signals:
            print(f"🛑 Daily signal limit reached: {self.daily_signal_count}/{self.max_daily_signals}")
            return False
        
        # Check cooldown
        if self.last_signal_time and (current_time - self.last_signal_time).seconds < self.signal_cooldown:
            remaining = self.signal_cooldown - (current_time - self.last_signal_time).seconds
            print(f"⏰ Signal cooldown: {remaining}s remaining")
            return False
        
        return True
    
    def send_signal_to_cloudflare(self, signal):
        """Send trading signal to Cloudflare Worker"""
        try:
            # Prepare signal payload for Cloudflare Worker
            payload = {
                "signalId": signal.get('signal_id', str(uuid.uuid4())),
                "timestamp": signal.get('timestamp', datetime.now().isoformat()),
                "account": self.webhook_config.account_key,
                "token": self.webhook_config.webhook_secret,  # Required authentication
                "event": "entry",
                "symbol": "XAUUSD",
                "side": signal['action'],  # BUY or SELL
                "price": round(signal['price'], 2),
                "sl": round(signal['stop_loss'], 2),
                "tp": round(signal['take_profit'], 2),
                "qty_usd": round(signal.get('position_size_usd', 1000), 0),
                "risk_pct": signal.get('risk_pct', 1.0),
                "confidence": round(signal['confidence'], 3),
                "trend_score": round(signal['trend_score'], 1),
                "strategy": "1H_Enhanced_Cloudflare",
                "magic": 123457
            }
            
            print(f"📤 Sending signal to Cloudflare Worker...")
            print(f"🔗 URL: {self.webhook_config.get_enqueue_url()}")
            print(f"📊 Signal: {payload['side']} @ ${payload['price']}")
            
            # Send to Cloudflare Worker
            response = requests.post(
                self.webhook_config.get_enqueue_url(),
                json=payload,
                headers=self.webhook_config.get_headers(),
                timeout=self.webhook_config.timeout_seconds
            )
            
            if response.status_code == 200:
                print("✅ Signal sent successfully to Cloudflare!")
                result = response.json()
                print(f"📊 Response: {result}")
                
                # Update tracking
                self.last_signal_time = datetime.now()
                self.daily_signal_count += 1
                self.signal_history.append(signal)
                self.active_signals[signal['signal_id']] = signal
                
                return True
            else:
                print(f"❌ Cloudflare returned: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to Cloudflare: {e}")
            return False
    
    def analyze_and_send_signal(self):
        """Analyze market and send signal if conditions are met"""
        try:
            # Check trading conditions
            if not self.check_trading_conditions():
                return False
            
            # Get live market data
            print(f"📊 Fetching live XAUUSD data...")
            df = self.get_live_market_data()
            
            if df is None or len(df) < 100:
                print("❌ Insufficient market data")
                return False
            
            # Calculate indicators
            df_analyzed = self.calculate_1h_trend_composite(df.copy())
            
            if df_analyzed is None or len(df_analyzed) < 50:
                print("❌ Failed to calculate indicators")
                return False
            
            # Get latest values
            latest = df_analyzed.iloc[-1]
            current_price = float(latest['Close'])
            trend_score = float(latest.get('trend_composite_1h', 0))
            
            # Check for signal
            signal_strength = abs(trend_score)
            
            if signal_strength < self.min_trend_strength:
                print(f"📊 No signal: strength {signal_strength:.1f} < {self.min_trend_strength}")
                return False
            
            # Determine direction
            if trend_score >= self.min_trend_strength:
                signal_type = "BUY"
                confidence = min(trend_score / 5.0, 1.0)
            elif trend_score <= -self.min_trend_strength:
                signal_type = "SELL"
                confidence = min(abs(trend_score) / 5.0, 1.0)
            else:
                return False
            
            # Calculate stops and targets
            atr = self.calculate_atr(df_analyzed, period=14).iloc[-1]
            
            if signal_type == "BUY":
                stop_loss = current_price - (self.config.atr_stop_multiplier * atr)
                take_profit = current_price + (self.config.atr_target_multiplier * atr)
            else:
                stop_loss = current_price + (self.config.atr_stop_multiplier * atr)
                take_profit = current_price - (self.config.atr_target_multiplier * atr)
            
            # Calculate position size
            risk_distance = abs(current_price - stop_loss)
            risk_pct = self.config.base_risk_pct
            position_size_usd = (self.current_balance * risk_pct / 100) / risk_distance
            
            # Create signal
            signal = {
                'timestamp': datetime.now().isoformat(),
                'signal_id': str(uuid.uuid4()),
                'symbol': 'XAUUSD',
                'action': signal_type,
                'price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trend_score': trend_score,
                'confidence': confidence,
                'atr': atr,
                'position_size_usd': position_size_usd,
                'risk_pct': risk_pct,
                'signal_strength': signal_strength
            }
            
            print(f"🎯 SIGNAL GENERATED: {signal_type}")
            
            # Send to Cloudflare
            return self.send_signal_to_cloudflare(signal)
            
        except Exception as e:
            print(f"❌ Error in signal analysis: {e}")
            return False
    
    def get_live_market_data(self, symbol="GC=F", lookback_hours=200):
        """Get live Gold futures data from yfinance"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=lookback_hours)
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_time.strftime("%Y-%m-%d"),
                end=end_time.strftime("%Y-%m-%d"),
                interval="1h"
            )
            
            if df.empty:
                print("❌ No market data available")
                return None
            
            print(f"✅ Fetched {len(df)} 1H periods")
            print(f"📈 Latest price: ${df['Close'].iloc[-1]:.2f}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            return None
    
    def run_live_monitoring(self, check_interval_minutes=5):
        """Run continuous monitoring and signal generation"""
        print(f"\n🔄 STARTING LIVE MONITORING")
        print(f"⏰ Checking every {check_interval_minutes} minutes")
        print(f"🌐 Sending signals to: {self.webhook_config.base_url}")
        print("=" * 60)
        
        while True:
            try:
                current_time = datetime.now()
                print(f"\n⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Analyze and potentially send signal
                signal_sent = self.analyze_and_send_signal()
                
                if signal_sent:
                    print(f"🎉 Signal sent! Daily count: {self.daily_signal_count}/{self.max_daily_signals}")
                else:
                    print(f"📊 No signal. Daily count: {self.daily_signal_count}/{self.max_daily_signals}")
                
                # Display status
                print(f"💰 Account: ${self.current_balance:,.2f} ({((self.current_balance/self.initial_balance-1)*100):+.2f}%)")
                print(f"🎯 Active Signals: {len(self.active_signals)}")
                
                # Wait for next check
                print(f"⏳ Next check in {check_interval_minutes} minutes...")
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Live monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring: {e}")
                print("⏳ Retrying in 1 minute...")
                time.sleep(60)
    
    def test_cloudflare_connection(self):
        """Test Cloudflare Worker connectivity"""
        print("🔍 Testing Cloudflare Worker connection...")
        
        test_payload = {
            "signalId": f"test_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "account": self.webhook_config.account_key,
            "event": "test",
            "symbol": "XAUUSD",
            "side": "BUY",
            "price": 2000.00,
            "strategy": "1H_Enhanced_Test"
        }
        
        try:
            response = requests.post(
                self.webhook_config.get_enqueue_url(),
                json=test_payload,
                headers=self.webhook_config.get_headers(),
                timeout=self.webhook_config.timeout_seconds
            )
            
            if response.status_code == 200:
                print("✅ Cloudflare Worker connection successful!")
                print(f"📊 Response: {response.json()}")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

def main():
    """Main function for Cloudflare live trading"""
    print("🌐 FTMO 1H ENHANCED - CLOUDFLARE EDITION")
    print("=" * 60)
    
    # Select configuration
    print("\n📊 Select Configuration:")
    print("1. Production (Live FTMO)")
    print("2. Testing (Demo)")
    print("3. Conservative (Safe mode)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    configs = {
        "1": CloudflarePresets.production(),
        "2": CloudflarePresets.testing(),
        "3": CloudflarePresets.conservative()
    }
    
    config = configs.get(choice, CloudflarePresets.testing())
    
    # Initialize trader
    trader = FTMO1HCloudflareTrader(config)
    
    # Test connection
    if not trader.test_cloudflare_connection():
        print("❌ Cannot connect to Cloudflare Worker")
        print("Please check your configuration and try again")
        return
    
    print("\n🎯 Options:")
    print("1. Start live monitoring")
    print("2. Test signal generation")
    print("3. Check current market conditions")
    print("0. Exit")
    
    while True:
        try:
            option = input("\nSelect option (0-3): ").strip()
            
            if option == "0":
                print("👋 Goodbye!")
                break
            elif option == "1":
                interval = input("Check interval in minutes (default 5): ").strip()
                interval = int(interval) if interval else 5
                trader.run_live_monitoring(interval)
            elif option == "2":
                print("📊 Testing signal generation...")
                trader.analyze_and_send_signal()
            elif option == "3":
                df = trader.get_live_market_data()
                if df is not None:
                    print(f"📈 Current Gold price: ${df['Close'].iloc[-1]:.2f}")
                    print(f"📊 24h change: {((df['Close'].iloc[-1]/df['Close'].iloc[-24]-1)*100):+.2f}%")
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()