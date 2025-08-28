#!/usr/bin/env python3
"""
MetaTrader5 Broker Client with Webhook Bridge Integration
Integrates existing EA bridge infrastructure into Edgerunner framework
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
from dataclasses import dataclass

from .adapter import BrokerAdapter


@dataclass
class MT5WebhookConfig:
    """MT5 Webhook configuration"""
    base_url: str = "https://tradingview-webhook.karloestrada.workers.dev"
    enqueue_endpoint: str = "/enqueue"
    dequeue_endpoint: str = "/dequeue" 
    status_endpoint: str = "/status"
    webhook_secret: str = ""
    account_key: str = "EDGERUNNER_MT5"
    timeout_seconds: int = 10
    retry_attempts: int = 3
    
    def get_enqueue_url(self) -> str:
        return f"{self.base_url}{self.enqueue_endpoint}"
    
    def get_status_url(self) -> str:
        return f"{self.base_url}{self.status_endpoint}"


class MT5Client(BrokerAdapter):
    """
    MetaTrader5 broker client using webhook bridge to EA
    Integrates existing ftmo-bridge.mq5 infrastructure
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.name = "MetaTrader5"
        
        # Initialize webhook configuration
        self.webhook_config = MT5WebhookConfig(
            base_url=config.get('webhook_url', 'https://tradingview-webhook.karloestrada.workers.dev'),
            account_key=config.get('account_key', 'EDGERUNNER_MT5'),
            webhook_secret=config.get('webhook_secret', ''),
            timeout_seconds=config.get('timeout', 10)
        )
        
        # MT5 specific settings
        self.magic_number = config.get('magic_number', 123456)
        self.symbol_mapping = self._load_symbol_mapping(config.get('symbol_mapping', {}))
        
        # Position sizing configuration
        self.use_fixed_lot = config.get('use_fixed_lot', False)
        self.fixed_lot_size = config.get('fixed_lot_size', 0.01)
        self.use_equity_percent = config.get('use_equity_percent', True)
        self.equity_percent = config.get('equity_percent', 1.0)
        self.max_lot_size = config.get('max_lot_size', 0.10)
        self.min_lot_size = config.get('min_lot_size', 0.01)
        
        # Signal tracking
        self.active_signals = {}
        self.signal_history = []
        
        print(f"MT5 Client initialized with webhook: {self.webhook_config.base_url}")
    
    def _load_symbol_mapping(self, custom_mapping: Dict) -> Dict:
        """Load symbol mapping for MT5 broker"""
        default_mapping = {
            # Crypto symbols
            'BTCUSDT': 'BTCUSD',
            'ETHUSDT': 'ETHUSD', 
            'XRPUSDT': 'XRPUSD',
            'ADAUSDT': 'ADAUSD',
            
            # Forex pairs
            'EURUSD': 'EURUSD',
            'GBPUSD': 'GBPUSD',
            'USDJPY': 'USDJPY',
            
            # Metals
            'XAUUSD': 'XAUUSD',  # Gold
            'XAGUSD': 'XAGUSD',  # Silver
            
            # Indices  
            'SPX500': 'SP500',
            'US30': 'DJ30',
            'NAS100': 'NAS100'
        }
        
        # Merge custom mapping
        default_mapping.update(custom_mapping)
        return default_mapping
    
    def connect(self) -> bool:
        """Test connection to MT5 webhook bridge"""
        try:
            print("Testing MT5 webhook connection...")
            
            response = requests.get(
                self.webhook_config.get_status_url(),
                timeout=self.webhook_config.timeout_seconds
            )
            
            if response.status_code == 200:
                print("MT5 webhook bridge connected")
                return True
            elif response.status_code == 404:
                # Try enqueue endpoint to test connectivity
                test_response = requests.get(
                    self.webhook_config.get_enqueue_url(),
                    timeout=self.webhook_config.timeout_seconds
                )
                connected = test_response.status_code in [200, 405]  # 405 = Method not allowed (normal for GET on POST endpoint)
                
                if connected:
                    print("MT5 webhook bridge reachable")
                else:
                    print(f"MT5 webhook bridge unreachable: {test_response.status_code}")
                    
                return connected
            else:
                print(f"MT5 webhook connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5 (webhook-based, no persistent connection)"""
        print("MT5 client disconnected")
    
    def get_account_info(self) -> Dict:
        """Get MT5 account information (limited via webhook)"""
        return {
            'broker': 'MetaTrader5',
            'account_key': self.webhook_config.account_key,
            'connection_type': 'webhook_bridge',
            'webhook_url': self.webhook_config.base_url,
            'active_signals': len(self.active_signals)
        }
    
    def get_positions(self) -> List[Dict]:
        """Get current positions (tracked locally via signals)"""
        positions = []
        
        for signal_id, signal in self.active_signals.items():
            positions.append({
                'signal_id': signal_id,
                'symbol': signal['symbol'],
                'side': signal['side'],
                'size': signal.get('qty_usd', 0),
                'entry_price': signal.get('price', 0),
                'stop_loss': signal.get('sl', 0),
                'take_profit': signal.get('tp', 0),
                'timestamp': signal.get('timestamp', '')
            })
        
        return positions
    
    def get_balance(self) -> float:
        """Get account balance (not available via webhook)"""
        # Note: Real balance would need to be fetched via MT5 terminal or additional API
        print("Balance not available via webhook - implement MT5 terminal integration")
        return 0.0
    
    def map_symbol(self, symbol: str) -> str:
        """Map Edgerunner symbol to MT5 broker symbol"""
        return self.symbol_mapping.get(symbol, symbol)
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = 'market', price: float = None,
                   stop_loss: float = None, take_profit: float = None,
                   **kwargs) -> Dict:
        """
        Place order via webhook to MT5 EA
        """
        try:
            # Map symbol
            mt5_symbol = self.map_symbol(symbol)
            
            # Generate signal ID
            signal_id = str(uuid.uuid4())
            
            # Prepare webhook payload for MT5 EA
            webhook_payload = {
                "signalId": signal_id,
                "timestamp": datetime.now().isoformat(),
                "account": self.webhook_config.account_key,
                "event": "entry",
                "symbol": mt5_symbol,
                "side": side.upper(),
                "price": round(price if price else 0, 5),
                "sl": round(stop_loss if stop_loss else 0, 5),
                "tp": round(take_profit if take_profit else 0, 5),
                "qty_usd": round(quantity if isinstance(quantity, (int, float)) else 1000, 0),
                "magic": self.magic_number,
                "strategy": "Edgerunner",
                "order_type": order_type,
                **kwargs  # Additional parameters
            }
            
            print(f"Sending MT5 order: {side} {mt5_symbol}")
            
            # Send to webhook
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Edgerunner-MT5-Client/1.0'
            }
            
            # Add authentication if configured
            if self.webhook_config.webhook_secret:
                webhook_payload['token'] = self.webhook_config.webhook_secret
            
            response = requests.post(
                self.webhook_config.get_enqueue_url(),
                json=webhook_payload,
                headers=headers,
                timeout=self.webhook_config.timeout_seconds
            )
            
            if response.status_code == 200:
                print("MT5 order sent successfully")
                
                # Track signal
                self.active_signals[signal_id] = webhook_payload
                self.signal_history.append(webhook_payload)
                
                return {
                    'success': True,
                    'order_id': signal_id,
                    'signal_id': signal_id,
                    'status': 'sent_to_mt5',
                    'timestamp': webhook_payload['timestamp']
                }
            else:
                print(f"MT5 order failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'signal_id': signal_id
                }
                
        except Exception as e:
            print(f"MT5 order error: {e}")
            return {
                'success': False,
                'error': str(e),
                'signal_id': signal_id if 'signal_id' in locals() else None
            }
    
    def close_position(self, position_id: str, **kwargs) -> Dict:
        """
        Close position via webhook exit signal
        """
        try:
            if position_id not in self.active_signals:
                return {
                    'success': False,
                    'error': f'Position {position_id} not found'
                }
            
            original_signal = self.active_signals[position_id]
            
            exit_payload = {
                "signalId": f"{position_id}_exit",
                "timestamp": datetime.now().isoformat(),
                "account": self.webhook_config.account_key,
                "event": "exit",
                "symbol": original_signal['symbol'],
                "side": original_signal['side'],
                "original_signal_id": position_id,
                "magic": self.magic_number,
                "strategy": "Edgerunner",
                "reason": kwargs.get('reason', 'manual_close')
            }
            
            response = requests.post(
                self.webhook_config.get_enqueue_url(),
                json=exit_payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.webhook_config.timeout_seconds
            )
            
            if response.status_code == 200:
                print(f"MT5 position close signal sent: {position_id}")
                
                # Remove from active signals
                del self.active_signals[position_id]
                
                return {
                    'success': True,
                    'position_id': position_id,
                    'status': 'exit_signal_sent'
                }
            else:
                print(f"MT5 exit signal failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            print(f"MT5 close position error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', 
                       bars: int = 100) -> Optional[pd.DataFrame]:
        """
        Get market data (MT5 via webhook doesn't provide this directly)
        This would need integration with MT5 terminal or external data source
        """
        print("Market data not available via MT5 webhook - use external data source")
        return None
    
    def test_webhook_connection(self) -> bool:
        """Test webhook connectivity with ping signal"""
        test_payload = {
            "signalId": f"test_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "account": self.webhook_config.account_key,
            "event": "test",
            "symbol": "EURUSD",
            "side": "BUY", 
            "price": 1.0000,
            "strategy": "Edgerunner_Test"
        }
        
        try:
            response = requests.post(
                self.webhook_config.get_enqueue_url(),
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.webhook_config.timeout_seconds
            )
            
            success = response.status_code == 200
            print(f"MT5 webhook test: {response.status_code} ({'SUCCESS' if success else 'FAILED'})")
            
            return success
            
        except Exception as e:
            print(f"MT5 webhook test error: {e}")
            return False