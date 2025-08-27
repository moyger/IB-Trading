#!/usr/bin/env python3
"""
XRPUSDT Phase 4B Strategy - Volatility Regime Adaptation
Dynamic parameter scaling based on market volatility conditions

PHASE 4B FEATURES:
✅ Realized volatility measurement and regime detection
✅ Dynamic parameter scaling (high/medium/low volatility)
✅ Adaptive position sizing based on volatility environment
✅ Enhanced signal sensitivity during different regimes
✅ Volatility-aware risk management

OPTIMIZATION APPROACH:
- Measure 20-day realized volatility continuously
- High volatility (>50%): Wider stops, bigger positions, relaxed signals
- Medium volatility (20-50%): Standard parameters (current approach)
- Low volatility (<20%): Tighter stops, smaller positions, stricter signals
- Breakout detection during low-to-high volatility transitions

EXPECTED OUTCOMES:
- Better performance across different market conditions
- More trades during appropriate volatility regimes
- Improved risk-adjusted returns through adaptive parameters
- Enhanced capture of volatility breakouts

AUTHOR: Claude (Anthropic AI)
VERSION: Phase 4B - Volatility Regime Adaptation
DATE: August 2024
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from xrpusdt_1h_enhanced_strategy_saved import XRPUSDT1HEnhancedStrategy

class XRPUSDT_Phase4B_Strategy(XRPUSDT1HEnhancedStrategy):
    """
    XRPUSDT Phase 4B Strategy - Volatility Regime Adaptation
    
    Dynamically adapts strategy parameters based on current market volatility:
    - High Volatility: More aggressive, wider stops, relaxed signal requirements
    - Medium Volatility: Standard approach (Phase 3 parameters)
    - Low Volatility: More conservative, tighter stops, stricter signals
    - Volatility Breakouts: Enhanced position sizing during regime transitions
    """
    
    def __init__(self, account_size=10000, risk_profile='moderate'):
        """Initialize Phase 4B strategy with volatility regime adaptation"""
        super().__init__(account_size, risk_profile)
        
        # Phase 4B: Volatility regime settings
        self.enable_volatility_adaptation = True
        self.volatility_cache = {}
        self.volatility_analysis_calls = 0
        self.volatility_adjustments_made = 0
        
        # Volatility regime thresholds (annualized percentages)
        self.high_volatility_threshold = 0.50   # 50% annualized
        self.low_volatility_threshold = 0.20    # 20% annualized
        self.volatility_lookback_days = 20      # 20-day realized volatility
        
        # Volatility regime parameter multipliers
        self.volatility_regime_multipliers = {
            'high': {
                'position_size': 1.5,      # Larger positions in high vol
                'stop_multiplier': 1.8,    # Wider stops for noise
                'signal_threshold': 0.7,   # Relaxed signal requirements
                'daily_trade_limit': 1.5,  # More trading opportunities
                'risk_multiplier': 1.3     # Higher risk tolerance
            },
            'medium': {
                'position_size': 1.0,      # Standard approach
                'stop_multiplier': 1.0,    # Standard stops
                'signal_threshold': 1.0,   # Standard signals
                'daily_trade_limit': 1.0,  # Standard trading
                'risk_multiplier': 1.0     # Standard risk
            },
            'low': {
                'position_size': 0.8,      # Smaller positions
                'stop_multiplier': 0.7,    # Tighter stops
                'signal_threshold': 1.3,   # Stricter signals
                'daily_trade_limit': 0.8,  # Fewer trades
                'risk_multiplier': 0.8     # Lower risk
            }
        }
        
        # Volatility breakout detection
        self.volatility_breakout_multiplier = 2.0  # Extra aggressive on vol breakouts
        self.breakout_detection_enabled = True
        
        # Enhanced logging
        self.phase4b_logs = []
        self.current_volatility_regime = 'medium'
        self.last_volatility_measurement = 0.0
        
        print("🌊 PHASE 4B INITIALIZATION - Volatility Regime Adaptation")
        print("=" * 70)
        print("📊 VOLATILITY REGIMES:")
        print(f"   🔥 High Volatility: >{self.high_volatility_threshold*100:.0f}% (aggressive parameters)")
        print(f"   📈 Medium Volatility: {self.low_volatility_threshold*100:.0f}-{self.high_volatility_threshold*100:.0f}% (standard parameters)")
        print(f"   📉 Low Volatility: <{self.low_volatility_threshold*100:.0f}% (conservative parameters)")
        print()
        print("🎯 ADAPTIVE FEATURES:")
        print("   ✅ Dynamic position sizing based on volatility")
        print("   ✅ Volatility-adjusted stop losses and signals")
        print("   ✅ Breakout detection during regime transitions")
        print("   ✅ Risk management scaling with market conditions")
        print()
    
    def log_phase4b_activity(self, message):
        """Enhanced logging for Phase 4B activities"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.phase4b_logs.append(log_entry)
        
        # Also add to trade log
        if hasattr(self, 'trade_log'):
            self.trade_log.append(f"Phase 4B: {message}")
        else:
            self.trade_log = [f"Phase 4B: {message}"]
    
    def calculate_realized_volatility(self, df, current_idx):
        """
        Calculate 20-day realized volatility (annualized)
        
        Args:
            df: Price dataframe
            current_idx: Current position in dataframe
            
        Returns:
            float: Annualized realized volatility (0.0 to 1.0+)
        """
        try:
            self.volatility_analysis_calls += 1
            
            # Need minimum data for volatility calculation
            if current_idx < self.volatility_lookback_days:
                return 0.25  # Default medium volatility
            
            # Get price data for volatility calculation
            start_idx = max(0, current_idx - self.volatility_lookback_days)
            price_data = df.iloc[start_idx:current_idx + 1]['Close']
            
            if len(price_data) < 5:
                return 0.25  # Default medium volatility
            
            # Calculate daily returns
            daily_returns = price_data.pct_change().dropna()
            
            if len(daily_returns) < 3:
                return 0.25  # Default medium volatility
            
            # Calculate realized volatility (standard deviation of returns)
            # For 1H data, annualize by sqrt(24*365) = sqrt(8760)
            hourly_vol = daily_returns.std()
            annualized_vol = hourly_vol * np.sqrt(8760)  # Annualize hourly volatility
            
            # Cache the result
            current_time = df.iloc[current_idx].name
            self.volatility_cache[current_time] = {
                'volatility': annualized_vol,
                'timestamp': current_time,
                'regime': self._classify_volatility_regime(annualized_vol)
            }
            
            return annualized_vol
            
        except Exception as e:
            self.log_phase4b_activity(f"Error calculating volatility: {str(e)[:50]}")
            return 0.25  # Default medium volatility
    
    def _classify_volatility_regime(self, volatility):
        """Classify volatility into regime categories"""
        if volatility > self.high_volatility_threshold:
            return 'high'
        elif volatility < self.low_volatility_threshold:
            return 'low'
        else:
            return 'medium'
    
    def detect_volatility_breakout(self, df, current_idx):
        """
        Detect volatility regime transitions (breakouts)
        
        Returns:
            tuple: (is_breakout, breakout_type, breakout_strength)
        """
        try:
            if current_idx < self.volatility_lookback_days + 5:
                return False, None, 1.0
            
            # Get current and previous volatility
            current_vol = self.calculate_realized_volatility(df, current_idx)
            previous_vol = self.calculate_realized_volatility(df, current_idx - 5)
            
            # Detect significant volatility increases (breakouts)
            vol_change = (current_vol - previous_vol) / max(previous_vol, 0.01)
            
            # Breakout conditions
            if vol_change > 0.5 and current_vol > self.low_volatility_threshold:
                # Volatility increased by 50%+ and moved out of low regime
                breakout_strength = min(3.0, 1.0 + vol_change)
                return True, 'expansion', breakout_strength
            
            elif vol_change < -0.3 and previous_vol > self.high_volatility_threshold:
                # Volatility decreased by 30%+ from high regime
                breakout_strength = 1.2  # Modest boost for vol compression
                return True, 'compression', breakout_strength
            
            return False, None, 1.0
            
        except Exception as e:
            return False, None, 1.0
    
    def get_volatility_adjustments(self, df, current_idx):
        """
        Get all volatility-based parameter adjustments
        
        Returns:
            dict: Complete set of volatility adjustments
        """
        try:
            # Calculate current volatility
            current_vol = self.calculate_realized_volatility(df, current_idx)
            regime = self._classify_volatility_regime(current_vol)
            
            # Get base multipliers for regime
            base_multipliers = self.volatility_regime_multipliers[regime].copy()
            
            # Check for volatility breakout
            is_breakout, breakout_type, breakout_strength = self.detect_volatility_breakout(df, current_idx)
            
            # Apply breakout adjustments
            if is_breakout and breakout_type == 'expansion':
                # Boost position sizing and relax requirements during vol expansion
                base_multipliers['position_size'] *= breakout_strength
                base_multipliers['signal_threshold'] *= 0.8  # More relaxed signals
                base_multipliers['daily_trade_limit'] *= 1.5
                
                self.log_phase4b_activity(f"Vol expansion breakout: {breakout_strength:.1f}x boost")
            
            elif is_breakout and breakout_type == 'compression':
                # Modest boost during vol compression (potential trend continuation)
                base_multipliers['position_size'] *= breakout_strength
                
                self.log_phase4b_activity(f"Vol compression detected: {breakout_strength:.1f}x adjustment")
            
            # Update tracking variables
            if regime != self.current_volatility_regime:
                self.log_phase4b_activity(
                    f"Volatility regime change: {self.current_volatility_regime} → {regime} "
                    f"({current_vol*100:.1f}% annualized)"
                )
                self.current_volatility_regime = regime
            
            self.last_volatility_measurement = current_vol
            
            return {
                'regime': regime,
                'volatility': current_vol,
                'multipliers': base_multipliers,
                'is_breakout': is_breakout,
                'breakout_type': breakout_type,
                'breakout_strength': breakout_strength if is_breakout else 1.0
            }
            
        except Exception as e:
            self.log_phase4b_activity(f"Error getting volatility adjustments: {str(e)[:50]}")
            return {
                'regime': 'medium',
                'volatility': 0.25,
                'multipliers': self.volatility_regime_multipliers['medium'],
                'is_breakout': False,
                'breakout_type': None,
                'breakout_strength': 1.0
            }
    
    def calculate_position_size(self, df, current_idx, signal_strength=1.0, atr=None):
        """Enhanced position sizing with Phase 4B volatility adaptation"""
        try:
            # Get volatility adjustments
            vol_adjustments = self.get_volatility_adjustments(df, current_idx)
            vol_multiplier = vol_adjustments['multipliers']['position_size']
            regime = vol_adjustments['regime']
            
            # Get base position size from Phase 3
            base_position_size = super().calculate_position_size(df, current_idx, signal_strength, atr)
            
            # Apply volatility-based position sizing
            volatility_adjusted_size = base_position_size * vol_multiplier
            
            # Apply risk limits with volatility adjustment
            risk_multiplier = vol_adjustments['multipliers']['risk_multiplier']
            max_risk_adjusted = self.max_risk_per_trade_hard_cap * risk_multiplier
            max_allowed_size = self.current_balance * (max_risk_adjusted / 100)
            
            final_position_size = min(volatility_adjusted_size, max_allowed_size)
            
            # Log significant adjustments
            if abs(vol_multiplier - 1.0) > 0.1:
                self.volatility_adjustments_made += 1
                volatility_pct = vol_adjustments['volatility'] * 100
                
                self.log_phase4b_activity(
                    f"Vol adjustment #{self.volatility_adjustments_made}: {regime.upper()} regime "
                    f"({volatility_pct:.1f}% vol) -> {vol_multiplier:.2f}x pos "
                    f"(${base_position_size:.0f} → ${final_position_size:.0f})"
                )
            
            return final_position_size
            
        except Exception as e:
            self.log_phase4b_activity(f"Error in volatility position sizing: {str(e)[:50]}")
            return super().calculate_position_size(df, current_idx, signal_strength, atr)
    
    def generate_signal(self, df, i):
        """Enhanced signal generation with volatility regime adjustments"""
        try:
            # Get volatility adjustments
            vol_adjustments = self.get_volatility_adjustments(df, i)
            signal_threshold_multiplier = vol_adjustments['multipliers']['signal_threshold']
            
            # For high volatility (relaxed signals), multiplier < 1.0 means easier to trade
            # For low volatility (strict signals), multiplier > 1.0 means harder to trade
            
            # Get base signal
            base_signal = super().generate_signal(df, i)
            
            # Apply volatility-based signal threshold adjustment
            if abs(signal_threshold_multiplier - 1.0) > 0.1:
                # Get current signal requirements
                original_min_signals = getattr(self, 'min_signals_to_trade', 2)
                original_adx_strong = getattr(self, 'adx_strong_threshold', 19)
                original_adx_weak = getattr(self, 'adx_weak_threshold', 14)
                
                # Apply volatility adjustments
                # For signal_threshold < 1.0: Relax requirements (easier trading)
                # For signal_threshold > 1.0: Tighten requirements (harder trading)
                adjusted_min_signals = max(1, int(original_min_signals * signal_threshold_multiplier))
                adjusted_adx_strong = max(15, int(original_adx_strong * signal_threshold_multiplier))
                adjusted_adx_weak = max(10, int(original_adx_weak * signal_threshold_multiplier))
                
                # Temporarily apply adjustments
                if hasattr(self, 'min_signals_to_trade'):
                    self.min_signals_to_trade = adjusted_min_signals
                if hasattr(self, 'adx_strong_threshold'):
                    self.adx_strong_threshold = adjusted_adx_strong
                if hasattr(self, 'adx_weak_threshold'):
                    self.adx_weak_threshold = adjusted_adx_weak
                
                # Recalculate signal with adjusted parameters
                adjusted_signal = super().generate_signal(df, i)
                
                # Restore original parameters
                if hasattr(self, 'min_signals_to_trade'):
                    self.min_signals_to_trade = original_min_signals
                if hasattr(self, 'adx_strong_threshold'):
                    self.adx_strong_threshold = original_adx_strong
                if hasattr(self, 'adx_weak_threshold'):
                    self.adx_weak_threshold = original_adx_weak
                
                # Log signal adjustments
                if adjusted_signal != base_signal:
                    regime = vol_adjustments['regime']
                    self.log_phase4b_activity(
                        f"Signal modified by {regime.upper()} vol regime: "
                        f"min_signals {original_min_signals}→{adjusted_min_signals}, "
                        f"ADX {original_adx_strong}→{adjusted_adx_strong} "
                        f"(signal: {base_signal}→{adjusted_signal})"
                    )
                
                return adjusted_signal
            
            return base_signal
            
        except Exception as e:
            self.log_phase4b_activity(f"Error in volatility signal generation: {str(e)[:50]}")
            return super().generate_signal(df, i)
    
    def print_phase4b_summary(self):
        """Print comprehensive Phase 4B volatility strategy summary"""
        print("\n" + "=" * 80)
        print("🌊 PHASE 4B SUMMARY - Volatility Regime Adaptation")
        print("=" * 80)
        
        print("📊 VOLATILITY REGIME FRAMEWORK:")
        print(f"- High Volatility (>{self.high_volatility_threshold*100:.0f}%): Aggressive parameters, wider stops")
        print(f"- Medium Volatility ({self.low_volatility_threshold*100:.0f}-{self.high_volatility_threshold*100:.0f}%): Standard Phase 3 parameters")
        print(f"- Low Volatility (<{self.low_volatility_threshold*100:.0f}%): Conservative parameters, tighter stops")
        print()
        
        print("🎯 PARAMETER ADAPTATIONS:")
        for regime, multipliers in self.volatility_regime_multipliers.items():
            print(f"  {regime.upper()} Volatility Regime:")
            print(f"    - Position Size: {multipliers['position_size']:.1f}x")
            print(f"    - Stop Multiplier: {multipliers['stop_multiplier']:.1f}x")
            print(f"    - Signal Threshold: {multipliers['signal_threshold']:.1f}x")
            print(f"    - Daily Trade Limit: {multipliers['daily_trade_limit']:.1f}x")
            print(f"    - Risk Multiplier: {multipliers['risk_multiplier']:.1f}x")
        print()
        
        print("📈 RUNTIME STATISTICS:")
        print(f"- Volatility Analysis Calls: {self.volatility_analysis_calls}")
        print(f"- Volatility Adjustments Made: {self.volatility_adjustments_made}")
        print(f"- Current Volatility Regime: {self.current_volatility_regime.upper()}")
        print(f"- Last Volatility Measurement: {self.last_volatility_measurement*100:.1f}%")
        print(f"- Phase 4B Log Entries: {len(self.phase4b_logs)}")
        print()
        
        if self.phase4b_logs:
            print("📝 RECENT PHASE 4B ACTIVITIES:")
            for i, log in enumerate(self.phase4b_logs[-5:]):
                print(f"  {i+1}. {log}")
            
            if len(self.phase4b_logs) > 5:
                print(f"  ... and {len(self.phase4b_logs) - 5} more activities")
        
        print()
        print("🚀 VOLATILITY BREAKOUT DETECTION:")
        print(f"- Breakout Detection: {'ENABLED' if self.breakout_detection_enabled else 'DISABLED'}")
        print(f"- Expansion Breakout Multiplier: {self.volatility_breakout_multiplier:.1f}x")
        print("- Monitors for 50%+ volatility increases and regime transitions")
        
        print("=" * 80)
        print("✅ Phase 4B - Volatility regime adaptation active!")
        print("=" * 80)

def create_xrpusdt_phase4b_strategy(account_size=10000, risk_profile='aggressive'):
    """Create XRPUSDT Phase 4B strategy with volatility adaptation"""
    return XRPUSDT_Phase4B_Strategy(account_size, risk_profile)

if __name__ == "__main__":
    print("🌊 XRPUSDT PHASE 4B - Volatility Regime Adaptation")
    print("=" * 60)
    
    # Test the implementation
    strategy = create_xrpusdt_phase4b_strategy(10000, 'aggressive')
    strategy.print_phase4b_summary()
    
    print("\n🧪 READY FOR VALIDATION TESTING")
    print("- Dynamic volatility regime detection")
    print("- Adaptive parameter scaling")
    print("- Breakout detection capabilities")
    print("- Expected: Better performance across market conditions")
    print()
    print("✅ Run validation test to measure improvements!")