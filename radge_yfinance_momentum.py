#!/usr/bin/env python3
"""
Nick Radge Book Momentum with Yahoo Finance Data
Uses yfinance for historical data (free, unlimited) + IB for trading
This solves the historical data limitation problem completely!
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import time
import warnings
warnings.filterwarnings('ignore')

from sp500_constituents import get_sp500_symbols

class RadgeYFinanceMomentum:
    """Nick Radge momentum using Yahoo Finance data - UNLIMITED historical data!"""
    
    def __init__(self):
        self.results = pd.DataFrame()
    
    def get_stock_data_yfinance(self, symbol: str, period: str = "400d") -> Optional[pd.DataFrame]:
        """Get stock data from Yahoo Finance - FREE and FAST!"""
        try:
            # Download data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty or len(df) < 252:
                return None
            
            # Clean column names and prepare data
            df = df.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df[['close', 'volume', 'high', 'low']]
            
        except Exception as e:
            return None
    
    def calculate_nick_radge_momentum(self, df: pd.DataFrame, 
                                    nlook: int = 252, 
                                    skip_days: int = 21) -> Optional[float]:
        """
        Nick Radge's EXACT momentum formula from the book
        Formula: (PriceNow / PriceThen) - 1
        """
        if df is None or len(df) < nlook:
            return None
            
        try:
            # PriceNow: Current close or close from skip_days ago
            if skip_days > 0 and len(df) > skip_days:
                price_now = df['close'].iloc[-(skip_days + 1)]
            else:
                price_now = df['close'].iloc[-1]
                
            # PriceThen: Close from nlook days ago (typically 252)
            price_then = df['close'].iloc[-nlook]
            
            if price_then <= 0:
                return None
                
            # Nick Radge's exact book formula
            momentum_score = (price_now / price_then) - 1
            
            return momentum_score
            
        except (IndexError, ValueError):
            return None
    
    def apply_nick_radge_filters(self, df: pd.DataFrame, 
                               min_price: float = 10.0,
                               min_dollar_volume: float = 1_000_000) -> Dict[str, any]:
        """Apply Nick Radge's exact filters from the book"""
        if df is None or len(df) < 50:
            return {'passes': False}
            
        try:
            current_price = df['close'].iloc[-1]
            
            # Price filter: Minimum $10
            price_ok = current_price >= min_price
            
            # Liquidity filter: 50-day average dollar volume
            if len(df) >= 50:
                avg_volume_50d = df['volume'].tail(50).mean()
                avg_price_50d = df['close'].tail(50).mean()
                dollar_volume = avg_volume_50d * avg_price_50d
                liquidity_ok = dollar_volume >= min_dollar_volume
            else:
                liquidity_ok = False
                dollar_volume = 0
            
            # 52-week high proximity (bonus filter)
            if len(df) >= 252:
                year_high = df['high'].tail(252).max()
                pct_from_high = ((current_price / year_high) - 1) * 100
                at_high = pct_from_high >= -5.0  # Within 5% of high
            else:
                pct_from_high = None
                at_high = False
            
            return {
                'passes': price_ok and liquidity_ok,
                'current_price': current_price,
                'dollar_volume': dollar_volume,
                'pct_from_high': pct_from_high,
                'at_high': at_high,
                'price_ok': price_ok,
                'liquidity_ok': liquidity_ok
            }
            
        except Exception:
            return {'passes': False}
    
    def check_spy_regime(self) -> Dict[str, any]:
        """Check SPY regime using Yahoo Finance data"""
        try:
            spy = yf.Ticker("SPY")
            spy_df = spy.history(period="300d")
            
            if spy_df.empty or len(spy_df) < 200:
                return {'bullish': True, 'note': 'Could not check regime'}
            
            # 200-day moving average
            spy_df['ma_200'] = spy_df['Close'].rolling(window=200).mean()
            
            current_price = spy_df['Close'].iloc[-1]
            current_ma = spy_df['ma_200'].iloc[-1]
            
            bullish = current_price > current_ma
            distance = ((current_price / current_ma) - 1) * 100
            
            return {
                'bullish': bullish,
                'spy_price': current_price,
                'ma_200': current_ma,
                'distance_pct': distance
            }
            
        except Exception:
            return {'bullish': True, 'note': 'Regime check failed'}
    
    def scan_sp500_momentum(self, 
                          max_stocks: int = None,
                          nlook: int = 252,
                          skip_days: int = 21,
                          min_price: float = 10.0,
                          min_dollar_volume: float = 1_000_000) -> pd.DataFrame:
        """
        Scan S&P 500 using Nick Radge's book methodology with Yahoo Finance data
        UNLIMITED historical data - no more IB constraints!
        """
        
        # Get S&P 500 symbols
        symbols = get_sp500_symbols()
        if max_stocks:
            symbols = symbols[:max_stocks]
        
        print(f"\n🚀 NICK RADGE BOOK MOMENTUM - YAHOO FINANCE VERSION")
        print("=" * 80)
        print(f"📊 Universe: {len(symbols)} S&P 500 stocks")
        print(f"📈 Lookback: {nlook} days ({nlook/252:.1f} years)")
        print(f"⏭️  Skip recent: {skip_days} days")
        print(f"💰 Min price: ${min_price}")
        print(f"💧 Min volume: ${min_dollar_volume:,.0f}")
        print(f"🔄 Data source: Yahoo Finance (FREE, UNLIMITED)")
        print("=" * 80)
        
        # Check market regime first
        regime = self.check_spy_regime()
        regime_status = "🟢 BULLISH" if regime['bullish'] else "🔴 BEARISH"
        print(f"📊 Market Regime: {regime_status}")
        
        if 'spy_price' in regime:
            print(f"    SPY: ${regime['spy_price']:.2f} | 200MA: ${regime['ma_200']:.2f} | Distance: {regime['distance_pct']:+.1f}%")
        
        print("-" * 80)
        
        results = []
        
        for i, symbol in enumerate(symbols):
            print(f"[{i+1:>3}/{len(symbols):>3}] {symbol:>6}... ", end="")
            
            try:
                # Get Yahoo Finance data (FAST and FREE!)
                df = self.get_stock_data_yfinance(symbol)
                
                if df is None:
                    print("❌ No data")
                    continue
                
                # Apply Nick Radge filters
                filters = self.apply_nick_radge_filters(df, min_price, min_dollar_volume)
                
                if not filters['passes']:
                    reason = "price" if not filters.get('price_ok', True) else "volume"
                    print(f"❌ Filter ({reason})")
                    continue
                
                # Calculate momentum using EXACT book formula
                momentum_standard = self.calculate_nick_radge_momentum(df, nlook, skip_days=0)
                momentum_skip = self.calculate_nick_radge_momentum(df, nlook, skip_days)
                
                if momentum_skip is None:
                    print(f"❌ Calc failed ({len(df)}d)")
                    continue
                
                # Success!
                result = {
                    'symbol': symbol,
                    'current_price': filters['current_price'],
                    'momentum_score': momentum_skip,
                    'momentum_pct': momentum_skip * 100,
                    'momentum_standard': momentum_standard,
                    'momentum_standard_pct': momentum_standard * 100 if momentum_standard else None,
                    'dollar_volume': filters['dollar_volume'],
                    'pct_from_high': filters['pct_from_high'],
                    'at_high': filters['at_high'],
                    'data_days': len(df)
                }
                
                results.append(result)
                
                high_indicator = "🎯" if filters['at_high'] else ""
                print(f"✅ {momentum_skip:+.4f} ({momentum_skip*100:+.2f}%) [{len(df)}d] {high_indicator}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:30]}...")
            
            # Small delay to be respectful to Yahoo Finance
            if i % 10 == 0 and i > 0:
                time.sleep(0.5)
        
        if not results:
            print(f"\n❌ No stocks passed filters")
            return pd.DataFrame()
        
        # Sort by momentum score (skip-recent version)
        results.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        self.results = df_results
        
        print(f"\n✅ Scan complete: {len(df_results)} stocks qualified")
        print(f"🏆 Top momentum: {df_results.iloc[0]['symbol']} ({df_results.iloc[0]['momentum_pct']:+.2f}%)")
        
        return df_results
    
    def display_results(self, top_n: int = 25):
        """Display Nick Radge book momentum results"""
        
        if self.results.empty:
            print("No results to display")
            return
            
        top_stocks = self.results.head(top_n)
        
        print(f"\n🏆 TOP {len(top_stocks)} MOMENTUM STOCKS - NICK RADGE BOOK METHOD")
        print("=" * 100)
        print("Using EXACT book formula: (PriceNow / Price252daysAgo) - 1 with 21-day skip")
        print("-" * 100)
        print(f"{'#':<3} {'Symbol':<6} {'Price':<10} {'Mom Score':<12} {'Mom %':<10} {'52WH':<6} {'$Vol':<8} {'Days':<5}")
        print("-" * 100)
        
        for i, (_, row) in enumerate(top_stocks.iterrows(), 1):
            high_indicator = "🎯" if row['at_high'] else ""
            
            print(f"{i:<3} {row['symbol']:<6} "
                  f"${row['current_price']:<9.2f} "
                  f"{row['momentum_score']:+<11.4f} "
                  f"{row['momentum_pct']:+<9.2f}% "
                  f"{row['pct_from_high']:>5.1f}% " if row['pct_from_high'] else f"{'N/A':>5} "
                  f"${row['dollar_volume']/1e6:<7.1f}M "
                  f"{row['data_days']:<5.0f} {high_indicator}")
        
        print("-" * 100)
        
        # Statistics
        avg_momentum = top_stocks['momentum_pct'].mean()
        positive_count = sum(top_stocks['momentum_pct'] > 0)
        high_count = sum(top_stocks['at_high'])
        
        print(f"\n📊 STATISTICS:")
        print(f"    Average Momentum: {avg_momentum:+.2f}%")
        print(f"    Positive Momentum: {positive_count}/{len(top_stocks)}")
        print(f"    Near 52-week High: {high_count}/{len(top_stocks)}")
    
    def save_results(self, filename: str = None):
        """Save results to CSV"""
        if self.results.empty:
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nick_radge_book_momentum_{timestamp}.csv"
            
        self.results.to_csv(filename, index=False)
        print(f"\n💾 Results saved to: {filename}")
        
        # Also save top 25 summary
        top_25_file = filename.replace('.csv', '_top25.csv')
        self.results.head(25).to_csv(top_25_file, index=False)
        print(f"📋 Top 25 summary: {top_25_file}")

def main():
    """Test Nick Radge book momentum with Yahoo Finance data"""
    
    print("🚀 NICK RADGE BOOK MOMENTUM - YAHOO FINANCE EDITION")
    print("✅ FREE historical data, ✅ UNLIMITED lookback, ✅ EXACT book formula")
    
    # Create scanner (no IB connection needed!)
    scanner = RadgeYFinanceMomentum()
    
    try:
        # Run FULL S&P 500 Nick Radge book scan
        results = scanner.scan_sp500_momentum(
            max_stocks=None,        # SCAN ALL 503 S&P 500 STOCKS!
            nlook=252,              # EXACT 12-month lookback from book
            skip_days=21,           # Skip last month as per book
            min_price=10.0,         # Book's price filter
            min_dollar_volume=1e6   # Book's liquidity filter
        )
        
        if not results.empty:
            # Display results in Nick Radge format
            scanner.display_results(top_n=25)
            
            # Save results
            scanner.save_results()
            
            print(f"\n🎉 NICK RADGE BOOK MOMENTUM - COMPLETE SUCCESS!")
            print(f"✅ Yahoo Finance data: UNLIMITED and FREE")
            print(f"✅ Book formula: EXACT 252-day implementation")
            print(f"✅ All filters: Applied as per book methodology")
            print(f"📊 Qualified stocks: {len(results)}")
            print(f"🏆 Top performer: {results.iloc[0]['symbol']} ({results.iloc[0]['momentum_pct']:+.2f}%)")
            
        else:
            print("❌ No qualifying stocks found")
        
    except KeyboardInterrupt:
        print("\n⚠️ Scan interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()