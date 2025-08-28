#!/usr/bin/env python3
"""
MT5 Integration Demo for Edgerunner Framework
Demonstrates the integration of existing MT5 EA bridge infrastructure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import asyncio
from datetime import datetime

from edgerunner.brokers.mt5_client import MT5Client, MT5WebhookConfig
from edgerunner.brokers.webhook_manager import WebhookManager
from edgerunner.utils.config import Config


def test_mt5_webhook_integration():
    """Test MT5 webhook bridge integration"""
    
    print("🚀 EDGERUNNER MT5 INTEGRATION DEMO")
    print("=" * 60)
    
    # MT5 Configuration
    mt5_config = {
        'webhook_url': 'https://tradingview-webhook.karloestrada.workers.dev',
        'account_key': 'EDGERUNNER_DEMO',
        'webhook_secret': '',
        'magic_number': 123456,
        'timeout': 10,
        
        # Position sizing
        'use_fixed_lot': False,
        'use_equity_percent': True,
        'equity_percent': 1.0,
        'max_lot_size': 0.10,
        'min_lot_size': 0.01,
        
        # Symbol mapping
        'symbol_mapping': {
            'BTCUSDT': 'BTCUSD',
            'XAUUSD': 'XAUUSD',
            'EURUSD': 'EURUSD'
        }
    }
    
    # Initialize MT5 Client
    print("\n📡 Initializing MT5 Client...")
    mt5_client = MT5Client(mt5_config)
    
    # Test webhook connection
    print("\n🔍 Testing webhook connectivity...")
    connected = mt5_client.connect()
    
    if not connected:
        print("❌ MT5 webhook connection failed")
        print("⚠️ Please ensure:")
        print("  1. Cloudflare Worker is deployed and accessible")
        print("  2. MT5 terminal is running with ftmo-bridge.mq5 EA")
        print("  3. EA is configured with correct webhook URL")
        return False
    
    # Test webhook ping
    print("\n📤 Testing webhook signal transmission...")
    ping_success = mt5_client.test_webhook_connection()
    
    if not ping_success:
        print("❌ Webhook ping failed")
        return False
    
    # Demo order placement
    print("\n💼 Demonstrating order placement...")
    
    demo_orders = [
        {
            'symbol': 'XAUUSD',
            'side': 'BUY', 
            'quantity': 1000,  # USD amount
            'order_type': 'market',
            'price': 2000.00,
            'stop_loss': 1980.00,
            'take_profit': 2040.00
        },
        {
            'symbol': 'EURUSD',
            'side': 'SELL',
            'quantity': 1500,
            'order_type': 'market', 
            'price': 1.1000,
            'stop_loss': 1.1050,
            'take_profit': 1.0950
        }
    ]
    
    placed_orders = []
    
    for i, order in enumerate(demo_orders, 1):
        print(f"\n📊 Placing demo order {i}:")
        print(f"   Symbol: {order['symbol']}")
        print(f"   Side: {order['side']}")
        print(f"   Quantity: ${order['quantity']}")
        print(f"   Price: {order['price']}")
        print(f"   Stop Loss: {order['stop_loss']}")
        print(f"   Take Profit: {order['take_profit']}")
        
        # Place order via MT5 webhook
        result = mt5_client.place_order(**order)
        
        if result['success']:
            print(f"   ✅ Order placed successfully!")
            print(f"   📍 Signal ID: {result['signal_id']}")
            placed_orders.append(result['signal_id'])
        else:
            print(f"   ❌ Order failed: {result.get('error', 'Unknown error')}")
        
        # Small delay between orders
        time.sleep(2)
    
    # Show current positions
    print(f"\n📈 Current MT5 positions: {len(mt5_client.active_signals)}")
    positions = mt5_client.get_positions()
    
    for pos in positions:
        print(f"   🎯 {pos['symbol']} {pos['side']} - Size: ${pos['size']}")
        print(f"      Entry: {pos['entry_price']}, SL: {pos['stop_loss']}, TP: {pos['take_profit']}")
    
    # Account info
    print(f"\n💼 MT5 Account Info:")
    account_info = mt5_client.get_account_info()
    for key, value in account_info.items():
        print(f"   {key}: {value}")
    
    # Demo position closing (after 10 seconds)
    if placed_orders:
        print(f"\n⏳ Waiting 10 seconds before closing demo positions...")
        time.sleep(10)
        
        print(f"\n🔄 Closing demo positions...")
        for signal_id in placed_orders:
            print(f"   Closing position: {signal_id}")
            result = mt5_client.close_position(signal_id, reason="demo_complete")
            
            if result['success']:
                print(f"   ✅ Position closed successfully")
            else:
                print(f"   ❌ Close failed: {result.get('error', 'Unknown error')}")
            
            time.sleep(1)
    
    # Final status
    print(f"\n📊 Final Status:")
    print(f"   Active signals: {len(mt5_client.active_signals)}")
    print(f"   Signal history: {len(mt5_client.signal_history)}")
    
    # Disconnect
    mt5_client.disconnect()
    
    print(f"\n✅ MT5 Integration Demo Complete!")
    print(f"🔗 Webhook URL: {mt5_config['webhook_url']}")
    print(f"🎯 Account Key: {mt5_config['account_key']}")
    
    return True


def demo_webhook_manager():
    """Demonstrate webhook manager functionality"""
    
    print("\n🌐 WEBHOOK MANAGER DEMO")
    print("=" * 40)
    
    # Mock configuration for demonstration
    webhook_config = {
        'webhooks': {
            'cloudflare_webhook': {
                'enabled': True,
                'base_url': 'https://tradingview-webhook.karloestrada.workers.dev',
                'endpoints': {
                    'enqueue': '/enqueue',
                    'dequeue': '/dequeue', 
                    'status': '/status'
                },
                'webhook_secret': '',
                'timeout_seconds': 10,
                'retry_attempts': 3
            },
            'local_webhook': {
                'enabled': False,
                'host': '0.0.0.0',
                'port': 5000
            },
            'routing': {
                'strategy_routing': {
                    'btcusdt_ftmo': {
                        'webhook': 'cloudflare_webhook',
                        'account': 'production'
                    }
                },
                'fallback': {
                    'primary': 'cloudflare_webhook',
                    'retry_on_failure': True
                }
            }
        }
    }
    
    # Create mock config object
    class MockConfig:
        def __init__(self, data):
            self._data = data
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    config = MockConfig(webhook_config)
    
    # Initialize webhook manager
    print("📡 Initializing Webhook Manager...")
    webhook_manager = WebhookManager(config)
    
    # Check webhook health
    print("\n🔍 Checking webhook health...")
    health_status = webhook_manager.check_webhook_health()
    
    for name, status in health_status.items():
        print(f"   {name}: {status['status']}")
        if 'error' in status:
            print(f"      Error: {status['error']}")
    
    # Demo signal routing
    print(f"\n📤 Testing signal routing...")
    
    demo_signal = {
        'signalId': f'demo_{int(time.time())}',
        'timestamp': datetime.now().isoformat(),
        'symbol': 'BTCUSDT',
        'event': 'entry',
        'side': 'BUY',
        'price': 50000.0,
        'sl': 48000.0,
        'tp': 52000.0,
        'qty_usd': 1000,
        'strategy': 'Demo'
    }
    
    # Route signal based on strategy
    success = webhook_manager.route_signal(demo_signal, 'btcusdt_ftmo')
    
    if success:
        print("   ✅ Signal routed successfully")
    else:
        print("   ❌ Signal routing failed")
    
    # Show queue status
    print(f"\n📊 Queue Status:")
    queue_status = webhook_manager.get_signal_queue_status()
    for key, value in queue_status.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Webhook Manager Demo Complete!")


def main():
    """Main demo function"""
    print("🎯 EDGERUNNER MT5 & WEBHOOK INTEGRATION")
    print("🔄 This demo integrates existing forex/EA infrastructure")
    print("📋 Components tested:")
    print("   • MT5 Client with webhook bridge")
    print("   • Cloudflare Worker integration")  
    print("   • Signal routing and management")
    print("   • Position tracking and closing")
    
    # Test MT5 Integration
    mt5_success = test_mt5_webhook_integration()
    
    # Test Webhook Manager
    demo_webhook_manager()
    
    print(f"\n🎉 INTEGRATION DEMO COMPLETE!")
    
    if mt5_success:
        print("✅ Ready for production deployment")
        print("\n📝 Next Steps:")
        print("1. Configure MT5 terminal with ftmo-bridge.mq5")
        print("2. Update webhook secrets in production")
        print("3. Test with live market data")
        print("4. Deploy strategies using MT5 broker")
    else:
        print("⚠️ Integration issues detected")
        print("Please check webhook connectivity and EA configuration")


if __name__ == "__main__":
    main()