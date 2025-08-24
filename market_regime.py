from ib_async import IB, Contract, Index
import pandas as pd
import numpy as np
from datetime import datetime

class MarketRegimeFilter:
    """Determine market regime for Nick Radge's momentum strategy"""
    
    def __init__(self, ib: IB):
        self.ib = ib
        self.spx_data = None
        self.regime = None
        
    def get_spx_contract(self):
        """Create S&P 500 index contract"""
        contract = Index()
        contract.symbol = 'SPX'
        contract.exchange = 'CBOE'
        contract.currency = 'USD'
        return contract
    
    def fetch_index_data(self, duration: str = "90 D"):
        """Fetch S&P 500 index historical data"""
        try:
            contract = self.get_spx_contract()
            
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                keepUpToDate=False
            )
            
            if not bars:
                print("Warning: Could not fetch SPX data")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': bar.date,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            } for bar in bars])
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            self.spx_data = df
            return df
            
        except Exception as e:
            print(f"Error fetching SPX data: {e}")
            return None
    
    def calculate_moving_average(self, df: pd.DataFrame, periods: int):
        """Calculate simple moving average"""
        if df is None or len(df) < periods:
            return None
            
        return df['close'].rolling(window=periods).mean()
    
    def is_bullish_regime(self, use_weekly: bool = True):
        """
        Check if market is in bullish regime
        Radge uses: SPX close > 10-week moving average
        """
        if self.spx_data is None:
            self.fetch_index_data()
            
        if self.spx_data is None or len(self.spx_data) < 50:
            print("Insufficient SPX data for regime determination")
            return None
            
        if use_weekly:
            # Convert to weekly data
            df_weekly = self.spx_data.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })
            
            if len(df_weekly) < 10:
                return None
                
            # Calculate 10-week MA
            ma_10w = df_weekly['close'].rolling(window=10).mean()
            current_close = df_weekly['close'].iloc[-1]
            current_ma = ma_10w.iloc[-1]
            
        else:
            # Use daily data with 50-day MA (approximately 10 weeks)
            ma_50d = self.calculate_moving_average(self.spx_data, 50)
            current_close = self.spx_data['close'].iloc[-1]
            current_ma = ma_50d.iloc[-1]
        
        if current_ma is None or np.isnan(current_ma):
            return None
            
        is_bullish = current_close > current_ma
        
        # Store regime info
        self.regime = {
            'is_bullish': is_bullish,
            'spx_close': current_close,
            'ma_value': current_ma,
            'distance_from_ma': ((current_close - current_ma) / current_ma) * 100,
            'timestamp': datetime.now()
        }
        
        return is_bullish
    
    def get_trailing_stop_percent(self):
        """
        Get trailing stop percentage based on market regime
        - Bullish regime: 40% trailing stop
        - Bearish regime: 10% trailing stop (tighter)
        """
        is_bullish = self.is_bullish_regime()
        
        if is_bullish is None:
            # Default to conservative if can't determine
            return 10
            
        return 40 if is_bullish else 10
    
    def get_regime_details(self):
        """Get detailed regime information"""
        if self.regime is None:
            self.is_bullish_regime()
            
        return self.regime
    
    def should_enter_positions(self):
        """Determine if new positions should be entered based on regime"""
        is_bullish = self.is_bullish_regime()
        
        # Only enter new positions in bullish regime
        return is_bullish == True  # Explicitly check for True (not None)
    
    def should_tighten_stops(self):
        """Determine if stops should be tightened (bearish regime)"""
        is_bullish = self.is_bullish_regime()
        
        # Tighten stops in bearish regime or if unable to determine
        return is_bullish != True

if __name__ == "__main__":
    # Test the market regime filter
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=3)
    
    regime_filter = MarketRegimeFilter(ib)
    
    # Check current regime
    is_bullish = regime_filter.is_bullish_regime()
    
    if is_bullish is not None:
        print(f"\nMarket Regime: {'BULLISH' if is_bullish else 'BEARISH'}")
        
        details = regime_filter.get_regime_details()
        print(f"SPX Close: {details['spx_close']:.2f}")
        print(f"10W MA: {details['ma_value']:.2f}")
        print(f"Distance from MA: {details['distance_from_ma']:.2f}%")
        print(f"Trailing Stop: {regime_filter.get_trailing_stop_percent()}%")
        print(f"Enter New Positions: {regime_filter.should_enter_positions()}")
    else:
        print("Could not determine market regime")
    
    ib.disconnect()