"""
Broker Manager - Multi-Broker Connectivity
==========================================

Unified interface for managing multiple broker connections and order routing.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum


class BrokerStatus(Enum):
    """Broker connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class BrokerManager:
    """
    Multi-broker management system.
    
    Provides unified interface for connecting to and managing multiple brokers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Broker Manager.
        
        Args:
            config: Broker configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Broker instances
        self.brokers = {}
        self.broker_status = {}
        
        # Default broker
        self.default_broker = config.get('execution', {}).get('default_broker', 'interactive_brokers')
        
        # Initialize broker clients
        self._initialize_brokers()
        
    def _initialize_brokers(self):
        """Initialize broker client instances."""
        # Interactive Brokers
        if self.config.get('interactive_brokers', {}).get('enabled', False):
            try:
                from .ibkr_client import IBKRClient
                self.brokers['interactive_brokers'] = IBKRClient(
                    self.config['interactive_brokers']
                )
                self.broker_status['interactive_brokers'] = BrokerStatus.DISCONNECTED
                self.logger.info("IBKR client initialized")
            except ImportError:
                self.logger.warning("IBKR client not available")
        
        # Bybit
        if self.config.get('bybit', {}).get('enabled', False):
            try:
                from .bybit_client import BybitClient
                self.brokers['bybit'] = BybitClient(
                    self.config['bybit']
                )
                self.broker_status['bybit'] = BrokerStatus.DISCONNECTED
                self.logger.info("Bybit client initialized")
            except ImportError:
                self.logger.warning("Bybit client not available")
        
        # MetaTrader 5
        if self.config.get('mt5', {}).get('enabled', False):
            try:
                from .mt5_client import MT5Client
                self.brokers['mt5'] = MT5Client(
                    self.config['mt5']
                )
                self.broker_status['mt5'] = BrokerStatus.DISCONNECTED
                self.logger.info("MT5 client initialized")
            except ImportError:
                self.logger.warning("MT5 client not available")
    
    def connect_all(self):
        """Connect to all enabled brokers."""
        self.logger.info("Connecting to all brokers...")
        
        for broker_name, broker_client in self.brokers.items():
            try:
                self.broker_status[broker_name] = BrokerStatus.CONNECTING
                success = broker_client.connect()
                
                if success:
                    self.broker_status[broker_name] = BrokerStatus.CONNECTED
                    self.logger.info(f"Connected to {broker_name}")
                else:
                    self.broker_status[broker_name] = BrokerStatus.ERROR
                    self.logger.error(f"Failed to connect to {broker_name}")
                    
            except Exception as e:
                self.broker_status[broker_name] = BrokerStatus.ERROR
                self.logger.error(f"Error connecting to {broker_name}: {e}")
    
    def disconnect_all(self):
        """Disconnect from all brokers."""
        self.logger.info("Disconnecting from all brokers...")
        
        for broker_name, broker_client in self.brokers.items():
            try:
                broker_client.disconnect()
                self.broker_status[broker_name] = BrokerStatus.DISCONNECTED
                self.logger.info(f"Disconnected from {broker_name}")
            except Exception as e:
                self.logger.error(f"Error disconnecting from {broker_name}: {e}")
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = 'MARKET', price: float = None,
                   broker: str = None) -> Optional[str]:
        """
        Place order through specified or default broker.
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            order_type: Order type (MARKET, LIMIT, etc.)
            price: Limit price (if applicable)
            broker: Specific broker to use
            
        Returns:
            Order ID if successful
        """
        broker_name = broker or self.default_broker
        
        if broker_name not in self.brokers:
            self.logger.error(f"Broker {broker_name} not available")
            return None
            
        if self.broker_status[broker_name] != BrokerStatus.CONNECTED:
            self.logger.error(f"Broker {broker_name} not connected")
            return None
        
        try:
            broker_client = self.brokers[broker_name]
            order_id = broker_client.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=price
            )
            
            self.logger.info(f"Order placed via {broker_name}: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Error placing order via {broker_name}: {e}")
            return None
    
    def get_positions(self, broker: str = None) -> Dict[str, Any]:
        """
        Get positions from specified or all brokers.
        
        Args:
            broker: Specific broker to query
            
        Returns:
            Dictionary of positions
        """
        if broker:
            if broker in self.brokers and self.broker_status[broker] == BrokerStatus.CONNECTED:
                return self.brokers[broker].get_positions()
            return {}
        
        # Get positions from all connected brokers
        all_positions = {}
        for broker_name, broker_client in self.brokers.items():
            if self.broker_status[broker_name] == BrokerStatus.CONNECTED:
                try:
                    positions = broker_client.get_positions()
                    all_positions[broker_name] = positions
                except Exception as e:
                    self.logger.error(f"Error getting positions from {broker_name}: {e}")
        
        return all_positions
    
    def get_market_data(self, symbol: str, broker: str = None) -> Optional[Dict[str, Any]]:
        """
        Get market data for symbol.
        
        Args:
            symbol: Trading symbol
            broker: Specific broker to use
            
        Returns:
            Market data dictionary
        """
        broker_name = broker or self.default_broker
        
        if broker_name not in self.brokers:
            return None
            
        if self.broker_status[broker_name] != BrokerStatus.CONNECTED:
            return None
        
        try:
            return self.brokers[broker_name].get_market_data(symbol)
        except Exception as e:
            self.logger.error(f"Error getting market data from {broker_name}: {e}")
            return None
    
    def status(self) -> Dict[str, Any]:
        """Get broker manager status."""
        return {
            'brokers': list(self.brokers.keys()),
            'status': {name: status.value for name, status in self.broker_status.items()},
            'default_broker': self.default_broker,
            'connected_count': sum(1 for status in self.broker_status.values() 
                                 if status == BrokerStatus.CONNECTED)
        }