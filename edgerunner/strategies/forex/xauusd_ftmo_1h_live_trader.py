#!/usr/bin/env python3
"""
1H Enhanced FTMO Live Trading Module
Extends the 1H Enhanced Strategy with webhook transmission for MT5 execution
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

class FTMO1HLiveTrader(XAUUSDFTMO1HEnhancedStrategy):
    """
    Live trading implementation of 1H Enhanced Strategy with webhook integration
    """
    
    def __init__(self, account_size=100000, challenge_phase=1, webhook_url=None, account_key="FTMO_LIVE"):
        """
        Initialize live trader
        
        Args:
            account_size: FTMO account size
            challenge_phase: FTMO challenge phase (1 or 2)
            webhook_url: Webhook URL for signal transmission
            account_key: Account identifier for webhook
        """
        super().__init__(account_size, challenge_phase, True)
        
        # Live trading settings
        self.webhook_url = webhook_url or "https://tradingview-webhook.karloestrada.workers.dev/enqueue"
        self.account_key = account_key
        self.live_mode = True
        self.last_signal_time = None
        self.signal_cooldown = 300  # 5 minutes between signals
        self.max_daily_signals = 10  # Prevent over-trading
        self.daily_signal_count = 0
        self.last_signal_date = None
        
        # Enhanced FTMO compliance for live trading
        self.max_daily_risk = 1.5  # Maximum daily risk percentage
        self.emergency_daily_limit = 0.8  # Emergency stop at 0.8% daily loss
        self.overall_emergency_limit = 5.0  # Emergency stop at 5% overall loss
        self.current_daily_pnl = 0.0
        self.daily_trades_count = 0
        self.max_daily_trades = 15  # Prevent over-trading
        
        # Signal tracking
        self.active_signals = {}
        self.signal_history = []
        
        print("🚀 FTMO 1H LIVE TRADER INITIALIZED")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"📊 Challenge Phase: {challenge_phase}")
        print(f"🔗 Webhook URL: {self.webhook_url}")
        print(f"🛡️ Enhanced FTMO Compliance: ACTIVE")
        print(f"⚠️ Daily Risk Limit: {self.max_daily_risk}%")
        print(f"🛑 Emergency Limits: {self.emergency_daily_limit}% daily, {self.overall_emergency_limit}% overall")
    
    def check_live_trading_conditions(self):
        """
        Check if live trading conditions are met
        """
        current_time = datetime.now()
        
        # Reset daily counters at start of new day
        if self.last_signal_date != current_time.date():
            self.daily_signal_count = 0
            self.current_daily_pnl = 0.0
            self.daily_trades_count = 0
            self.last_signal_date = current_time.date()
            print(f"📅 New trading day: {current_time.date()}")
        
        # Check daily signal limit
        if self.daily_signal_count >= self.max_daily_signals:
            print(f"🛑 Daily signal limit reached: {self.daily_signal_count}/{self.max_daily_signals}")
            return False
        
        # Check daily trades limit
        if self.daily_trades_count >= self.max_daily_trades:
            print(f"🛑 Daily trades limit reached: {self.daily_trades_count}/{self.max_daily_trades}")
            return False
        
        # Check signal cooldown
        if self.last_signal_time and (current_time - self.last_signal_time).seconds < self.signal_cooldown:
            remaining = self.signal_cooldown - (current_time - self.last_signal_time).seconds
            print(f"⏰ Signal cooldown: {remaining}s remaining")
            return False
        
        # Check emergency stops
        current_loss_pct = abs(self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        if current_loss_pct >= self.overall_emergency_limit:
            print(f"🛑 OVERALL EMERGENCY STOP: {current_loss_pct:.2f}% loss reached {self.overall_emergency_limit}% limit")
            return False
        
        if abs(self.current_daily_pnl) >= self.emergency_daily_limit:
            print(f"🛑 DAILY EMERGENCY STOP: {abs(self.current_daily_pnl):.2f}% loss reached {self.emergency_daily_limit}% limit")
            return False
        
        return True
    
    def get_live_market_data(self, symbol="GC=F", period="1h", lookback_hours=200):
        """
        Get live market data for analysis
        """
        try:
            print(f"📊 Fetching live {symbol} data...")
            
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=lookback_hours)
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_time.strftime("%Y-%m-%d"),
                end=end_time.strftime("%Y-%m-%d"), 
                interval="1h"
            )
            
            if df.empty:
                print("❌ No live data available")
                return None
            
            # Ensure we have enough data
            if len(df) < 100:
                print(f"⚠️ Limited data: {len(df)} periods")
                return None
            
            print(f"✅ Fetched {len(df)} 1H periods")
            print(f"📈 Latest price: ${df['Close'].iloc[-1]:.2f}")
            print(f"⏰ Latest time: {df.index[-1]}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching live data: {e}")
            return None
    
    def analyze_live_signal(self, df):
        """
        Analyze live market data for trading signals
        """
        if df is None or len(df) < 100:
            return None
        
        try:
            # Calculate 1H indicators
            df_analyzed = self.calculate_1h_trend_composite(df.copy())
            
            if df_analyzed is None or len(df_analyzed) < 50:
                return None
            
            # Get latest values (safely handle indexing)
            if len(df_analyzed) == 0:
                return None
                
            latest = df_analyzed.iloc[-1]
            current_price = float(latest['Close'])
            
            # Get trend score safely
            trend_score = latest.get('trend_composite_1h', 0)
            if pd.isna(trend_score):
                trend_score = 0
            
            trend_score = float(trend_score)
            
            # Check for signal conditions
            signal_strength = abs(trend_score)
            
            # Use lower threshold for testing
            min_strength = getattr(self, 'min_trend_strength', 2.0)
            if signal_strength < min_strength:
                print(f"📊 Signal too weak: {signal_strength:.1f} (need ≥{min_strength})")
                return None
            
            # Determine signal direction
            if trend_score >= min_strength:
                signal_type = "BUY"
                confidence = min(trend_score / 5.0, 1.0)
            elif trend_score <= -min_strength:
                signal_type = "SELL" 
                confidence = min(abs(trend_score) / 5.0, 1.0)
            else:
                return None
            
            # Calculate ATR safely
            try:
                atr_series = self.calculate_atr(df_analyzed, period=14)
                if atr_series is None or len(atr_series) == 0:
                    atr = current_price * 0.01  # 1% fallback
                else:
                    atr = float(atr_series.iloc[-1])
                    if pd.isna(atr) or atr <= 0:
                        atr = current_price * 0.01
            except Exception:
                atr = current_price * 0.01  # 1% fallback
            
            if signal_type == "BUY":
                stop_loss = current_price - (2.0 * atr)
                take_profit = current_price + (3.0 * atr)
            else:
                stop_loss = current_price + (2.0 * atr)
                take_profit = current_price - (3.0 * atr)
            
            # Calculate position size (1H enhanced approach)
            risk_distance = abs(current_price - stop_loss)
            risk_pct = min(1.25, self.max_daily_risk / 4)  # Conservative for live trading
            position_size_usd = (self.current_balance * risk_pct / 100) / risk_distance
            
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
            
            print(f"🎯 SIGNAL GENERATED:")
            print(f"   Direction: {signal_type}")
            print(f"   Price: ${current_price:.2f}")
            print(f"   Stop Loss: ${stop_loss:.2f}")
            print(f"   Take Profit: ${take_profit:.2f}")
            print(f"   Trend Score: {trend_score:.1f}")
            print(f"   Confidence: {confidence:.1%}")
            print(f"   Position Size: ${position_size_usd:.0f}")
            
            return signal
            
        except Exception as e:
            print(f"❌ Error analyzing signal: {e}")
            return None
    
    def send_webhook_signal(self, signal):
        """
        Send trading signal via webhook
        """
        if not signal or not self.webhook_url:
            return False
        
        try:
            # Format signal for MT5 EA
            webhook_payload = {
                "signalId": signal['signal_id'],
                "timestamp": signal['timestamp'],
                "account": self.account_key,
                "event": "entry",
                "symbol": "XAUUSD",  # Will be mapped to GOLD in MT5
                "side": signal['action'],
                "price": round(signal['price'], 2),
                "sl": round(signal['stop_loss'], 2),
                "tp": round(signal['take_profit'], 2),
                "qty_usd": round(signal['position_size_usd'], 0),
                "risk_pct": signal['risk_pct'],
                "confidence": round(signal['confidence'], 3),
                "trend_score": round(signal['trend_score'], 1),
                "strategy": "1H_Enhanced",
                "magic": 123457,  # Unique magic number for 1H strategy
                "ftmo_compliant": True
            }
            
            print(f"📤 Sending webhook signal...")
            print(f"🔗 URL: {self.webhook_url}")
            
            # Send HTTP POST request
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'FTMO-1H-Enhanced-Strategy/1.0'
            }
            
            response = requests.post(
                self.webhook_url,
                json=webhook_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Webhook signal sent successfully")
                
                # Update tracking
                self.last_signal_time = datetime.now()
                self.daily_signal_count += 1
                self.signal_history.append(signal)
                self.active_signals[signal['signal_id']] = signal
                
                print(f"📊 Daily signals: {self.daily_signal_count}/{self.max_daily_signals}")
                
                return True
            else:
                print(f"❌ Webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return False
    
    def send_exit_signal(self, signal_id, exit_reason="manual"):
        """
        Send exit signal for active position
        """
        if signal_id not in self.active_signals:
            print(f"⚠️ Signal ID not found: {signal_id}")
            return False
        
        try:
            original_signal = self.active_signals[signal_id]
            
            exit_payload = {
                "signalId": f"{signal_id}_exit",
                "timestamp": datetime.now().isoformat(),
                "account": self.account_key,
                "event": "exit",
                "symbol": "XAUUSD",
                "side": original_signal['action'],
                "reason": exit_reason,
                "original_signal_id": signal_id,
                "strategy": "1H_Enhanced",
                "magic": 123457
            }
            
            response = requests.post(
                self.webhook_url,
                json=exit_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Exit signal sent for {signal_id}")
                del self.active_signals[signal_id]
                return True
            else:
                print(f"❌ Exit signal failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exit signal error: {e}")
            return False
    
    def run_live_monitoring(self, interval_minutes=5):
        """
        Run continuous live monitoring and signal generation
        """
        print(f"\n🔄 Starting live monitoring (check every {interval_minutes} minutes)")
        print("=" * 80)
        
        while True:
            try:
                current_time = datetime.now()
                print(f"\n⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')} - Checking for signals...")
                
                # Check trading conditions
                if not self.check_live_trading_conditions():
                    print("⏸️ Trading conditions not met, skipping...")
                    time.sleep(interval_minutes * 60)
                    continue
                
                # Get live market data
                df = self.get_live_market_data()
                
                if df is None:
                    print("📊 No market data available")
                    time.sleep(interval_minutes * 60)
                    continue
                
                # Analyze for signals
                signal = self.analyze_live_signal(df)
                
                if signal:
                    # Send webhook signal
                    success = self.send_webhook_signal(signal)
                    
                    if success:
                        print("🎉 Signal sent successfully!")
                        self.daily_trades_count += 1
                    else:
                        print("❌ Failed to send signal")
                else:
                    print("📊 No trading signal generated")
                
                # Display status
                print(f"📈 Daily Stats: {self.daily_signal_count}/{self.max_daily_signals} signals, {self.daily_trades_count}/{self.max_daily_trades} trades")
                print(f"💰 Account: ${self.current_balance:,.2f} ({((self.current_balance/self.initial_balance-1)*100):+.2f}%)")
                print(f"🎯 Active Signals: {len(self.active_signals)}")
                
                # Wait for next check
                print(f"⏳ Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Live monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                print("⏳ Retrying in 1 minute...")
                time.sleep(60)
    
    def test_webhook_connection(self):
        """
        Test webhook connectivity
        """
        print("🔍 Testing webhook connection...")
        
        test_payload = {
            "signalId": f"test_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "account": self.account_key,
            "event": "test",
            "symbol": "XAUUSD",
            "side": "BUY",
            "price": 2000.00,
            "strategy": "1H_Enhanced_Test"
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Webhook connection successful!")
                return True
            else:
                print(f"❌ Webhook test failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook test error: {e}")
            return False

def main():
    """
    Main function for live trading
    """
    print("🚀 FTMO 1H ENHANCED LIVE TRADER")
    print("=" * 50)
    
    # Initialize live trader
    trader = FTMO1HLiveTrader(
        account_size=100000,
        challenge_phase=1,
        webhook_url="https://tradingview-webhook.karloestrada.workers.dev/enqueue",
        account_key="FTMO_1H_LIVE"
    )
    
    # Test webhook connection
    if not trader.test_webhook_connection():
        print("❌ Webhook connection failed - please check configuration")
        return
    
    print("\n🎯 Commands:")
    print("  'start' - Begin live monitoring")
    print("  'test' - Generate test signal")
    print("  'status' - Show current status")
    print("  'quit' - Exit")
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == 'start':
                trader.run_live_monitoring(interval_minutes=5)
                break
            elif command == 'test':
                df = trader.get_live_market_data()
                signal = trader.analyze_live_signal(df)
                if signal:
                    trader.send_webhook_signal(signal)
                else:
                    print("📊 No test signal generated")
            elif command == 'status':
                print(f"📈 Account: ${trader.current_balance:,.2f}")
                print(f"📊 Daily Signals: {trader.daily_signal_count}/{trader.max_daily_signals}")
                print(f"🎯 Active Signals: {len(trader.active_signals)}")
            elif command == 'quit':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()