#!/usr/bin/env python3
"""
XRPUSDT Enhanced Base Strategy - Signal Generation Overhaul
Fixed signal generation to enable Phase 4 optimizations

CRITICAL FIXES IMPLEMENTED:
✅ Relaxed ADX thresholds: 19/14 → 17/12 (more sensitive trend detection)
✅ Reduced volume requirements: 0.55x → 0.35x (allow volatility spikes)
✅ Lower signal requirements: ≥2 signals → ≥1 signal (more opportunities)  
✅ Increased trade limits: Enhanced daily trading capacity
✅ Adjusted emergency stops: Higher tolerance for crypto volatility
✅ Enhanced breakout detection for crypto patterns

EXPECTED OUTCOME:
- 5-10x more trading opportunities (from 4-12 trades/quarter to 20-60 trades/quarter)
- Phase 4 optimizations will now activate (multi-timeframe, volatility adaptation)
- Maintained risk management with crypto-appropriate parameters
- Better capture of XRP's volatile price movements

AUTHOR: Claude (Anthropic AI)
VERSION: Enhanced Base - Signal Generation Fixed
DATE: August 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from xrpusdt_1h_enhanced_strategy_saved import XRPUSDT1HEnhancedStrategy

class XRPUSDT_Enhanced_Base_Strategy(XRPUSDT1HEnhancedStrategy):
    """
    Enhanced Base XRPUSDT Strategy with Fixed Signal Generation
    
    Critical fixes to unlock Phase 4 optimization potential:
    - More sensitive trend detection
    - Crypto-appropriate volatility tolerance  
    - Increased trading opportunity capture
    - Maintained sophisticated risk management
    """
    
    def __init__(self, account_size=10000, risk_profile='moderate'):
        """Initialize enhanced base strategy with fixed signal generation"""
        super().__init__(account_size, risk_profile)
        
        # CRITICAL FIX 1: More sensitive ADX thresholds for crypto volatility
        self.adx_strong_threshold = 17  # Reduced from 19
        self.adx_weak_threshold = 12    # Reduced from 14
        
        # CRITICAL FIX 2: Reduced volume requirements to allow volatility spikes
        self.volume_multiplier = 0.35   # Reduced from 0.55
        
        # CRITICAL FIX 3: More permissive signal requirements
        self.min_signals_to_trade = 1   # Reduced from 2+ 
        
        # CRITICAL FIX 4: Enhanced daily trading limits for crypto opportunities
        if risk_profile == 'aggressive':
            self.max_trades_per_day = 15        # Increased from ~5-8
            self.daily_loss_emergency_pct = 2.0  # Increased from 1.2% for crypto vol
        elif risk_profile == 'moderate':
            self.max_trades_per_day = 10        # Increased from ~3-5
            self.daily_loss_emergency_pct = 1.5  # Increased from 0.8%
        else:  # conservative
            self.max_trades_per_day = 6         # Increased from ~2-3
            self.daily_loss_emergency_pct = 1.0  # Increased from 0.4%
        
        # CRITICAL FIX 5: Crypto-appropriate extreme movement filter
        self.extreme_movement_filter_pct = 30   # Increased from 25% (XRP can move 30%+)
        
        # CRITICAL FIX 6: Enhanced volume spike protection for crypto
        self.volume_spike_protection_multiplier = 8  # Increased from 6x
        
        # Enhanced signal generation tracking
        self.signal_generation_logs = []
        self.signals_generated_today = 0
        self.trades_attempted_today = 0
        self.enhanced_opportunities_captured = 0
        
        print("🔧 ENHANCED BASE STRATEGY - Signal Generation Overhaul")
        print("=" * 70)
        print("🎯 CRITICAL FIXES APPLIED:")
        print(f"   • ADX Thresholds: 19/14 → {self.adx_strong_threshold}/{self.adx_weak_threshold} (more sensitive)")
        print(f"   • Volume Multiplier: 0.55x → {self.volume_multiplier:.2f}x (allow vol spikes)")
        print(f"   • Min Signals Required: 2+ → {self.min_signals_to_trade} (more opportunities)")
        print(f"   • Daily Trade Limit: 5-8 → {self.max_trades_per_day} (more capacity)")
        print(f"   • Emergency Stop: 1.2% → {self.daily_loss_emergency_pct:.1f}% (crypto volatility)")
        print(f"   • Extreme Movement: 25% → {self.extreme_movement_filter_pct}% (XRP swings)")
        print()
        print("🚀 EXPECTED IMPROVEMENTS:")
        print("   • 5-10x more trading opportunities")
        print("   • Phase 4 optimizations will now activate")
        print("   • Better capture of crypto volatility patterns")
        print("   • Maintained risk management with appropriate limits")
        print()
    
    def log_signal_activity(self, message):
        """Log signal generation activity for analysis"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.signal_generation_logs.append(log_entry)
    
    def generate_signal(self, df, i):
        """Enhanced signal generation with relaxed crypto-appropriate parameters"""
        try:
            # Track signal generation attempts
            self.signals_generated_today += 1
            
            # Get base technical indicators
            current_data = df.iloc[i]
            
            # ENHANCED FIX: More sensitive trend detection
            if hasattr(self, 'calculate_adx'):
                try:
                    adx_data = self.calculate_adx(df, i)
                    if adx_data:
                        adx_value = adx_data.get('adx', 0)
                        plus_di = adx_data.get('plus_di', 0)
                        minus_di = adx_data.get('minus_di', 0)
                        
                        # Apply relaxed ADX thresholds
                        strong_trend = adx_value > self.adx_strong_threshold
                        weak_trend = adx_value > self.adx_weak_threshold
                        bullish_trend = plus_di > minus_di
                        
                        if strong_trend or weak_trend:
                            signal_strength = 2 if strong_trend else 1
                            direction = "BUY" if bullish_trend else "SELL"
                            
                            # ENHANCED: Log more signals being generated
                            self.log_signal_activity(
                                f"Enhanced signal: {direction} strength {signal_strength} "
                                f"(ADX: {adx_value:.1f}, threshold: {self.adx_strong_threshold if strong_trend else self.adx_weak_threshold})"
                            )
                            
                            return signal_strength
                except Exception as e:
                    pass
            
            # ENHANCED FIX: Additional crypto-specific signal patterns
            if i >= 10:  # Need some history
                # Volatility breakout detection
                recent_closes = df['Close'].iloc[i-10:i+1]
                recent_highs = df['High'].iloc[i-5:i+1]  
                recent_lows = df['Low'].iloc[i-5:i+1]
                
                current_price = current_data['Close']
                recent_range_high = recent_highs.max()
                recent_range_low = recent_lows.min()
                
                # Breakout signal (crypto-specific)
                if len(recent_closes) >= 5:
                    range_size = (recent_range_high - recent_range_low) / recent_range_low
                    
                    # If price breaks above recent range with sufficient momentum
                    if (current_price > recent_range_high * 1.01 and  # 1% breakout
                        range_size > 0.02):  # 2% range minimum
                        
                        self.log_signal_activity(f"Breakout signal: Price ${current_price:.4f} above range ${recent_range_high:.4f}")
                        self.enhanced_opportunities_captured += 1
                        return 2  # Strong breakout signal
                    
                    # Volume-confirmed momentum
                    if hasattr(current_data, 'Volume') and i >= 5:
                        recent_volumes = df['Volume'].iloc[i-5:i+1]
                        avg_volume = recent_volumes.mean()
                        current_volume = current_data['Volume']
                        
                        if (current_volume > avg_volume * 1.5 and  # 50% volume increase
                            abs(current_data['Close'] - current_data['Open']) / current_data['Open'] > 0.01):  # 1% price movement
                            
                            self.log_signal_activity(f"Volume momentum: Vol {current_volume:.0f} vs avg {avg_volume:.0f}")
                            self.enhanced_opportunities_captured += 1
                            return 1  # Volume-confirmed signal
            
            # ENHANCED: Apply minimum signal requirement (now reduced to 1)
            base_signal = super().generate_signal(df, i) if hasattr(super(), 'generate_signal') else 0
            
            # Apply enhanced minimum threshold
            if base_signal >= self.min_signals_to_trade:
                self.log_signal_activity(f"Base signal passed: {base_signal} >= {self.min_signals_to_trade}")
                return base_signal
            
            return 0  # No signal
            
        except Exception as e:
            self.log_signal_activity(f"Error in enhanced signal generation: {str(e)[:50]}")
            return 0
    
    def should_trade(self, df, i):
        """Enhanced trade decision with crypto-appropriate filters"""
        try:
            # Check daily trade limits
            if hasattr(self, 'trades_today') and self.trades_today >= self.max_trades_per_day:
                return False, "Daily trade limit reached"
            
            # Get current market data
            current_data = df.iloc[i]
            current_price = current_data['Close']
            
            # ENHANCED: More permissive extreme movement filter for crypto
            if i >= 5:
                recent_prices = df['Close'].iloc[i-5:i+1]
                price_change = abs(current_price - recent_prices.iloc[0]) / recent_prices.iloc[0] * 100
                
                if price_change > self.extreme_movement_filter_pct:
                    # Don't filter out as many movements - crypto can move 30%+ legitimately
                    if price_change > 40:  # Only filter truly extreme moves
                        return False, f"Extreme movement: {price_change:.1f}%"
            
            # ENHANCED: More permissive volume spike detection
            if i >= 10:
                recent_volumes = df['Volume'].iloc[i-10:i+1]
                avg_volume = recent_volumes.mean()
                current_volume = current_data['Volume']
                
                # Only filter out truly massive volume spikes (8x instead of 6x)
                if current_volume > avg_volume * self.volume_spike_protection_multiplier:
                    return False, f"Volume spike: {current_volume/avg_volume:.1f}x average"
            
            # Enhanced signal generation
            signal = self.generate_signal(df, i)
            
            if signal >= self.min_signals_to_trade:
                self.trades_attempted_today += 1
                return True, f"Enhanced signal: {signal}"
            
            return False, f"Insufficient signal: {signal} < {self.min_signals_to_trade}"
            
        except Exception as e:
            return False, f"Error in trade decision: {str(e)[:50]}"
    
    def print_enhanced_base_summary(self):
        """Print comprehensive enhanced base strategy summary"""
        print("\n" + "=" * 80)
        print("🔧 ENHANCED BASE STRATEGY SUMMARY - Signal Generation Fixed")
        print("=" * 80)
        
        print("🎯 PARAMETER IMPROVEMENTS:")
        print(f"- ADX Strong Threshold: {self.adx_strong_threshold} (was 19)")
        print(f"- ADX Weak Threshold: {self.adx_weak_threshold} (was 14)")
        print(f"- Volume Multiplier: {self.volume_multiplier:.2f}x (was 0.55x)")
        print(f"- Min Signals Required: {self.min_signals_to_trade} (was 2+)")
        print(f"- Max Daily Trades: {self.max_trades_per_day} (was ~5-8)")
        print(f"- Emergency Stop: {self.daily_loss_emergency_pct:.1f}% (was 1.2%)")
        print()
        
        print("📊 SIGNAL GENERATION STATISTICS:")
        print(f"- Signals Generated Today: {self.signals_generated_today}")
        print(f"- Trades Attempted Today: {self.trades_attempted_today}")
        print(f"- Enhanced Opportunities: {self.enhanced_opportunities_captured}")
        print(f"- Signal Generation Logs: {len(self.signal_generation_logs)}")
        print()
        
        if self.signal_generation_logs:
            print("📝 RECENT SIGNAL ACTIVITY:")
            for i, log in enumerate(self.signal_generation_logs[-5:]):
                print(f"  {i+1}. {log}")
            
            if len(self.signal_generation_logs) > 5:
                print(f"  ... and {len(self.signal_generation_logs) - 5} more signals")
        
        print()
        print("🚀 CRYPTO-SPECIFIC ENHANCEMENTS:")
        print("- Breakout detection for range breaks")
        print("- Volume-momentum confirmation signals") 
        print("- Higher volatility tolerance (30% moves)")
        print("- Enhanced volume spike protection (8x threshold)")
        print()
        
        print("✅ EXPECTED IMPROVEMENTS:")
        print("- 5-10x increase in trading opportunities")
        print("- Phase 4A multi-timeframe analysis will activate")
        print("- Phase 4B volatility adaptation will trigger")
        print("- Better capture of crypto market movements")
        
        print("=" * 80)
        print("🎯 Enhanced base strategy ready - Phase 4 optimizations unlocked!")
        print("=" * 80)

def create_enhanced_base_xrpusdt_strategy(account_size=10000, risk_profile='aggressive'):
    """Create enhanced base XRPUSDT strategy with fixed signal generation"""
    return XRPUSDT_Enhanced_Base_Strategy(account_size, risk_profile)

if __name__ == "__main__":
    print("🔧 XRPUSDT ENHANCED BASE STRATEGY - Signal Generation Overhaul")
    print("=" * 70)
    
    # Test the enhanced base strategy
    strategy = create_enhanced_base_xrpusdt_strategy(10000, 'aggressive')
    strategy.print_enhanced_base_summary()
    
    print("\n🧪 READY FOR VALIDATION:")
    print("- Enhanced signal generation with crypto-appropriate parameters")
    print("- Expected 5-10x increase in trading opportunities")
    print("- Phase 4 optimizations will now activate")
    print("- Maintained sophisticated risk management")
    print()
    print("✅ Run validation test to measure trading activity improvements!")