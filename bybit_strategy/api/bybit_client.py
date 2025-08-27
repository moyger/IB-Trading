"""
Bybit API Client Module
Handles all interactions with Bybit exchange
"""

import ccxt
import time
import hmac
import hashlib
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass

@dataclass
class Position:
    """Position data structure"""
    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    mark_price: float
    pnl: float
    pnl_pct: float
    margin: float
    leverage: int
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class Order:
    """Order data structure"""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    order_type: str  # 'limit' or 'market'
    price: float
    quantity: float
    status: str
    filled: float
    remaining: float
    timestamp: datetime

class BybitClient:
    """
    Bybit API Client
    Handles all exchange interactions
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 testnet: bool = True, config=None):
        """Initialize Bybit client"""
        
        self.testnet = testnet
        self.config = config
        
        # Initialize CCXT exchange
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': testnet,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'linear',  # USDT perpetual
                'adjustForTimeDifference': True,
            }
        })
        
        # Set up endpoints
        if testnet:
            self.base_url = 'https://api-testnet.bybit.com'
            self.ws_url = 'wss://stream-testnet.bybit.com/v5/public/linear'
        else:
            self.base_url = 'https://api.bybit.com'
            self.ws_url = 'wss://stream.bybit.com/v5/public/linear'
        
        # Connection state
        self.connected = False
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # 100ms between requests
        
        # Cache
        self.market_cache = {}
        self.balance_cache = {}
        self.cache_expiry = 60  # seconds
        
        print(f"Bybit client initialized ({'Testnet' if testnet else 'Mainnet'})")
    
    def test_connection(self) -> bool:
        """Test connection to Bybit"""
        try:
            self.exchange.fetch_time()
            self.connected = True
            print("✅ Bybit connection successful")
            return True
        except Exception as e:
            print(f"❌ Bybit connection failed: {e}")
            self.connected = False
            return False
    
    def get_account_balance(self, currency: str = 'USDT') -> Dict:
        """Get account balance"""
        try:
            self._rate_limit()
            
            # Check cache
            cache_key = f'balance_{currency}'
            if cache_key in self.balance_cache:
                cached_time, cached_data = self.balance_cache[cache_key]
                if time.time() - cached_time < self.cache_expiry:
                    return cached_data
            
            # Fetch fresh balance
            balance = self.exchange.fetch_balance()
            
            result = {
                'currency': currency,
                'free': balance[currency]['free'],
                'used': balance[currency]['used'],
                'total': balance[currency]['total'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Update cache
            self.balance_cache[cache_key] = (time.time(), result)
            
            return result
            
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', 
                       limit: int = 200) -> pd.DataFrame:
        """Fetch OHLCV market data"""
        try:
            self._rate_limit()
            
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data"""
        try:
            self._rate_limit()
            ticker = self.exchange.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['baseVolume'],
                'change_24h': ticker['percentage'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low']
            }
            
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            return None
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book data"""
        try:
            self._rate_limit()
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            
            return {
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': orderbook['timestamp'],
                'spread': orderbook['asks'][0][0] - orderbook['bids'][0][0] if orderbook['bids'] and orderbook['asks'] else 0
            }
            
        except Exception as e:
            print(f"Error fetching orderbook: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   amount: float, price: float = None, 
                   stop_loss: float = None, take_profit: float = None) -> Optional[Order]:
        """Place an order on Bybit"""
        try:
            self._rate_limit()
            
            # Validate inputs
            if side not in ['buy', 'sell']:
                raise ValueError(f"Invalid side: {side}")
            
            if order_type not in ['market', 'limit']:
                raise ValueError(f"Invalid order type: {order_type}")
            
            # Create order parameters
            params = {}
            
            # Add stop loss if provided
            if stop_loss:
                params['stopLoss'] = stop_loss
            
            # Add take profit if provided
            if take_profit:
                params['takeProfit'] = take_profit
            
            # Place order
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount, params)
            else:
                if not price:
                    raise ValueError("Price required for limit order")
                order = self.exchange.create_limit_order(symbol, side, amount, price, params)
            
            # Create Order object
            return Order(
                order_id=order['id'],
                symbol=order['symbol'],
                side=order['side'],
                order_type=order['type'],
                price=order['price'] or 0,
                quantity=order['amount'],
                status=order['status'],
                filled=order['filled'],
                remaining=order['remaining'],
                timestamp=datetime.fromtimestamp(order['timestamp'] / 1000)
            )
            
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            self._rate_limit()
            self.exchange.cancel_order(order_id, symbol)
            print(f"Order {order_id} cancelled")
            return True
            
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return False
    
    def get_open_orders(self, symbol: str = None) -> List[Order]:
        """Get all open orders"""
        try:
            self._rate_limit()
            orders = self.exchange.fetch_open_orders(symbol)
            
            result = []
            for order in orders:
                result.append(Order(
                    order_id=order['id'],
                    symbol=order['symbol'],
                    side=order['side'],
                    order_type=order['type'],
                    price=order['price'] or 0,
                    quantity=order['amount'],
                    status=order['status'],
                    filled=order['filled'],
                    remaining=order['remaining'],
                    timestamp=datetime.fromtimestamp(order['timestamp'] / 1000)
                ))
            
            return result
            
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return []
    
    def get_positions(self, symbol: str = None) -> List[Position]:
        """Get current positions"""
        try:
            self._rate_limit()
            
            # Fetch positions
            positions = self.exchange.fetch_positions(symbol)
            
            result = []
            for pos in positions:
                if pos['contracts'] > 0:  # Only include open positions
                    result.append(Position(
                        symbol=pos['symbol'],
                        side=pos['side'],
                        size=pos['contracts'],
                        entry_price=pos['entryPrice'] or 0,
                        mark_price=pos['markPrice'] or 0,
                        pnl=pos['unrealizedPnl'] or 0,
                        pnl_pct=pos['percentage'] or 0,
                        margin=pos['initialMargin'] or 0,
                        leverage=pos['leverage'] or 1,
                        stop_loss=pos.get('stopLoss'),
                        take_profit=pos.get('takeProfit')
                    ))
            
            return result
            
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def close_position(self, symbol: str, reduce_only: bool = True) -> bool:
        """Close a position"""
        try:
            self._rate_limit()
            
            # Get current position
            positions = self.get_positions(symbol)
            if not positions:
                print(f"No position found for {symbol}")
                return False
            
            position = positions[0]
            
            # Determine close side
            close_side = 'sell' if position.side == 'long' else 'buy'
            
            # Place closing order
            params = {'reduceOnly': reduce_only}
            order = self.exchange.create_market_order(
                symbol, close_side, position.size, params
            )
            
            print(f"Position closed: {order['id']}")
            return True
            
        except Exception as e:
            print(f"Error closing position: {e}")
            return False
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for a symbol"""
        try:
            self._rate_limit()
            
            # Bybit-specific leverage setting
            self.exchange.set_leverage(leverage, symbol)
            print(f"Leverage set to {leverage}x for {symbol}")
            return True
            
        except Exception as e:
            print(f"Error setting leverage: {e}")
            return False
    
    def get_funding_rate(self, symbol: str) -> Dict:
        """Get funding rate for a symbol"""
        try:
            self._rate_limit()
            
            # Fetch funding rate
            ticker = self.exchange.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'funding_rate': ticker.get('fundingRate', 0),
                'funding_timestamp': ticker.get('fundingDatetime'),
                'next_funding_time': ticker.get('nextFundingDatetime')
            }
            
        except Exception as e:
            print(f"Error fetching funding rate: {e}")
            return None
    
    def get_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        try:
            self._rate_limit()
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            
            result = []
            for trade in trades:
                result.append({
                    'id': trade['id'],
                    'timestamp': trade['timestamp'],
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'price': trade['price'],
                    'amount': trade['amount'],
                    'cost': trade['cost']
                })
            
            return result
            
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return []
    
    def get_market_info(self, symbol: str) -> Dict:
        """Get market information for a symbol"""
        try:
            if symbol not in self.market_cache:
                self.exchange.load_markets()
                self.market_cache = self.exchange.markets
            
            market = self.market_cache.get(symbol, {})
            
            return {
                'symbol': symbol,
                'base': market.get('base'),
                'quote': market.get('quote'),
                'min_order_size': market.get('limits', {}).get('amount', {}).get('min'),
                'max_order_size': market.get('limits', {}).get('amount', {}).get('max'),
                'tick_size': market.get('precision', {}).get('price'),
                'lot_size': market.get('precision', {}).get('amount'),
                'maker_fee': market.get('maker'),
                'taker_fee': market.get('taker')
            }
            
        except Exception as e:
            print(f"Error fetching market info: {e}")
            return None
    
    def _rate_limit(self):
        """Apply rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def calculate_position_size(self, symbol: str, risk_amount: float, 
                               entry_price: float, stop_price: float) -> float:
        """Calculate position size based on risk"""
        try:
            # Get market info
            market_info = self.get_market_info(symbol)
            if not market_info:
                return 0
            
            # Calculate risk distance
            risk_distance = abs(entry_price - stop_price) / entry_price
            
            # Calculate position value
            position_value = risk_amount / risk_distance
            
            # Convert to contracts
            position_size = position_value / entry_price
            
            # Apply limits
            min_size = market_info.get('min_order_size', 0.001)
            max_size = market_info.get('max_order_size', float('inf'))
            
            position_size = max(min_size, min(position_size, max_size))
            
            # Round to lot size
            lot_size = market_info.get('lot_size', 6)
            position_size = round(position_size, lot_size)
            
            return position_size
            
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return 0