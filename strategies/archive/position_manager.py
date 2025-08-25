import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from ib_async import IB, Contract, Order

class PositionManager:
    """Manage positions and trailing stops for Nick Radge's momentum strategy"""
    
    def __init__(self, ib: IB, portfolio_value: float = 100000):
        self.ib = ib
        self.portfolio_value = portfolio_value
        self.positions = {}
        self.positions_file = Path("radge_positions.json")
        self.load_positions()
        
    def load_positions(self):
        """Load existing positions from file"""
        if self.positions_file.exists():
            try:
                with open(self.positions_file, 'r') as f:
                    self.positions = json.load(f)
                print(f"Loaded {len(self.positions)} existing positions")
            except Exception as e:
                print(f"Error loading positions: {e}")
                self.positions = {}
        else:
            self.positions = {}
    
    def save_positions(self):
        """Save positions to file"""
        try:
            with open(self.positions_file, 'w') as f:
                json.dump(self.positions, f, indent=2, default=str)
            print(f"Saved {len(self.positions)} positions")
        except Exception as e:
            print(f"Error saving positions: {e}")
    
    def calculate_position_size(self, max_positions: int = 20):
        """
        Calculate position size using equal weighting
        Radge typically uses 5% per position (20 positions max)
        """
        position_size_percent = 100 / max_positions
        position_value = self.portfolio_value * (position_size_percent / 100)
        return position_value, position_size_percent
    
    def add_position(self, symbol: str, entry_price: float, 
                     stop_percent: float = 40, shares: int = None):
        """Add a new position with trailing stop"""
        
        if symbol in self.positions:
            print(f"Position already exists for {symbol}")
            return False
        
        # Calculate position size if shares not specified
        if shares is None:
            position_value, _ = self.calculate_position_size()
            shares = int(position_value / entry_price)
        
        self.positions[symbol] = {
            'entry_price': entry_price,
            'entry_date': datetime.now().isoformat(),
            'shares': shares,
            'highest_price': entry_price,
            'stop_percent': stop_percent,
            'stop_price': entry_price * (1 - stop_percent / 100),
            'current_price': entry_price,
            'unrealized_pnl': 0,
            'unrealized_pnl_percent': 0
        }
        
        self.save_positions()
        print(f"Added position: {symbol} - {shares} shares @ ${entry_price:.2f}")
        print(f"  Initial stop: ${self.positions[symbol]['stop_price']:.2f} ({stop_percent}%)")
        
        return True
    
    def update_position(self, symbol: str, current_price: float, stop_percent: float = None):
        """Update position with current price and adjust trailing stop"""
        
        if symbol not in self.positions:
            print(f"No position found for {symbol}")
            return False
        
        pos = self.positions[symbol]
        pos['current_price'] = current_price
        
        # Update highest price if current is higher
        if current_price > pos['highest_price']:
            pos['highest_price'] = current_price
            
            # Update trailing stop based on new high
            if stop_percent:
                pos['stop_percent'] = stop_percent
            
            new_stop = pos['highest_price'] * (1 - pos['stop_percent'] / 100)
            
            # Only move stop up, never down
            if new_stop > pos['stop_price']:
                pos['stop_price'] = new_stop
                print(f"  {symbol}: Trailing stop updated to ${new_stop:.2f}")
        
        # Calculate unrealized P&L
        pos['unrealized_pnl'] = (current_price - pos['entry_price']) * pos['shares']
        pos['unrealized_pnl_percent'] = ((current_price / pos['entry_price']) - 1) * 100
        
        self.save_positions()
        return True
    
    def check_stops(self, current_prices: dict):
        """Check if any positions have hit their stops"""
        stopped_out = []
        
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                if current_price <= pos['stop_price']:
                    stopped_out.append({
                        'symbol': symbol,
                        'stop_price': pos['stop_price'],
                        'current_price': current_price,
                        'entry_price': pos['entry_price'],
                        'shares': pos['shares'],
                        'pnl': (current_price - pos['entry_price']) * pos['shares'],
                        'pnl_percent': ((current_price / pos['entry_price']) - 1) * 100
                    })
        
        return stopped_out
    
    def remove_position(self, symbol: str):
        """Remove a position (after selling)"""
        if symbol in self.positions:
            del self.positions[symbol]
            self.save_positions()
            print(f"Removed position: {symbol}")
            return True
        return False
    
    def adjust_stops_for_regime(self, is_bullish: bool):
        """Adjust all stops based on market regime"""
        new_stop_percent = 40 if is_bullish else 10
        
        print(f"Adjusting stops to {new_stop_percent}% for {'BULLISH' if is_bullish else 'BEARISH'} regime")
        
        for symbol, pos in self.positions.items():
            if pos['stop_percent'] != new_stop_percent:
                old_stop = pos['stop_price']
                pos['stop_percent'] = new_stop_percent
                pos['stop_price'] = pos['highest_price'] * (1 - new_stop_percent / 100)
                
                # Never move stop down
                if pos['stop_price'] < old_stop:
                    pos['stop_price'] = old_stop
                else:
                    print(f"  {symbol}: Stop adjusted from ${old_stop:.2f} to ${pos['stop_price']:.2f}")
        
        self.save_positions()
    
    def get_portfolio_summary(self):
        """Get portfolio summary statistics"""
        if not self.positions:
            return {
                'num_positions': 0,
                'total_value': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0
            }
        
        total_value = sum(pos['current_price'] * pos['shares'] for pos in self.positions.values())
        total_cost = sum(pos['entry_price'] * pos['shares'] for pos in self.positions.values())
        total_pnl = total_value - total_cost
        
        return {
            'num_positions': len(self.positions),
            'total_value': total_value,
            'total_cost': total_cost,
            'total_pnl': total_pnl,
            'total_pnl_percent': (total_pnl / total_cost * 100) if total_cost > 0 else 0,
            'positions': self.positions
        }
    
    def display_positions(self):
        """Display current positions in a formatted table"""
        if not self.positions:
            print("No open positions")
            return
        
        print("\nCurrent Positions:")
        print("-" * 120)
        print(f"{'Symbol':8} {'Shares':>8} {'Entry':>10} {'Current':>10} {'High':>10} "
              f"{'Stop':>10} {'P&L':>12} {'P&L %':>8} {'Days':>6}")
        print("-" * 120)
        
        for symbol, pos in self.positions.items():
            days_held = (datetime.now() - datetime.fromisoformat(pos['entry_date'])).days
            
            print(f"{symbol:8} {pos['shares']:8} "
                  f"${pos['entry_price']:9.2f} "
                  f"${pos['current_price']:9.2f} "
                  f"${pos['highest_price']:9.2f} "
                  f"${pos['stop_price']:9.2f} "
                  f"${pos['unrealized_pnl']:11.2f} "
                  f"{pos['unrealized_pnl_percent']:7.2f}% "
                  f"{days_held:6}")
        
        summary = self.get_portfolio_summary()
        print("-" * 120)
        print(f"Total: {summary['num_positions']} positions | "
              f"Value: ${summary['total_value']:,.2f} | "
              f"P&L: ${summary['total_pnl']:,.2f} ({summary['total_pnl_percent']:.2f}%)")
    
    def create_market_order(self, symbol: str, quantity: int, action: str = "BUY"):
        """Create a market order"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        
        return contract, order

if __name__ == "__main__":
    # Test the position manager
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=5)
    
    pm = PositionManager(ib, portfolio_value=100000)
    
    # Test adding positions
    pm.add_position("AAPL", 150.00, stop_percent=40)
    pm.add_position("MSFT", 300.00, stop_percent=40)
    
    # Test updating positions
    pm.update_position("AAPL", 155.00)
    pm.update_position("MSFT", 295.00)
    
    # Display positions
    pm.display_positions()
    
    ib.disconnect()