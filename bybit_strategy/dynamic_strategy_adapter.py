#!/usr/bin/env python3
"""
Dynamic Strategy Adapter - Phase 3 Enhancement
Implements intelligent strategy adaptation based on market conditions and performance

Key Features:
- Alt season detection and mode switching
- Drawdown recovery modes
- Performance-based parameter adjustment
- Market cycle adaptation
- Seasonal trading patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum

class TradingMode(Enum):
    """Different trading modes based on market conditions"""
    CONSERVATIVE = "conservative"
    STANDARD = "standard" 
    AGGRESSIVE = "aggressive"
    ALT_SEASON = "alt_season"
    RECOVERY = "recovery"
    HIBERNATION = "hibernation"

class MarketCycle(Enum):
    """Market cycle phases"""
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"

class DynamicStrategyAdapter:
    """
    Dynamic Strategy Adapter for intelligent trading mode switching
    """
    
    def __init__(self, base_strategy):
        self.base_strategy = base_strategy
        self.current_mode = TradingMode.STANDARD
        self.previous_mode = TradingMode.STANDARD
        self.mode_history = []
        
        # Performance tracking for adaptation
        self.performance_window = 10  # Last N trading days
        self.performance_history = []
        self.drawdown_threshold = 15.0  # % drawdown to trigger recovery mode
        self.recovery_target = 5.0     # % profit to exit recovery mode
        
        # Alt season detection parameters
        self.alt_season_threshold = 42.0  # BTC dominance threshold
        self.alt_season_streak = 3        # Days below threshold to confirm
        self.dominance_streak = 0
        
        # Market cycle detection
        self.cycle_lookback = 30
        self.current_cycle = MarketCycle.ACCUMULATION
        
        # Seasonal patterns (months where strategy performs better)
        self.favorable_months = [2, 8, 9, 11]  # Feb, Aug, Sep, Nov based on historical data
        self.unfavorable_months = [6, 7, 12]   # Jun, Jul, Dec - historically weak
        
        # Mode-specific parameter adjustments
        self.mode_parameters = self._initialize_mode_parameters()
        
        print("🧠 DYNAMIC STRATEGY ADAPTER INITIALIZED")
        print(f"📊 Performance Tracking: {self.performance_window} day window")
        print(f"🎯 Drawdown Recovery: {self.drawdown_threshold}% trigger")
        print(f"🌊 Alt Season: <{self.alt_season_threshold}% BTC dominance")
        
    def _initialize_mode_parameters(self) -> Dict[TradingMode, Dict]:
        """Initialize parameter sets for different trading modes"""
        return {
            TradingMode.CONSERVATIVE: {
                'position_multiplier': 0.6,
                'risk_multiplier': 0.7,
                'signal_threshold': 3,
                'max_trades_per_day': 3,
                'stop_loss_multiplier': 0.8,
                'take_profit_multiplier': 1.5
            },
            TradingMode.STANDARD: {
                'position_multiplier': 1.0,
                'risk_multiplier': 1.0,
                'signal_threshold': 2,
                'max_trades_per_day': 5,
                'stop_loss_multiplier': 1.0,
                'take_profit_multiplier': 1.0
            },
            TradingMode.AGGRESSIVE: {
                'position_multiplier': 1.4,
                'risk_multiplier': 1.3,
                'signal_threshold': 2,
                'max_trades_per_day': 8,
                'stop_loss_multiplier': 1.1,
                'take_profit_multiplier': 0.8
            },
            TradingMode.ALT_SEASON: {
                'position_multiplier': 1.6,
                'risk_multiplier': 1.4,
                'signal_threshold': 1,  # Lower threshold for more entries
                'max_trades_per_day': 10,
                'stop_loss_multiplier': 1.2,
                'take_profit_multiplier': 0.7  # Quick profits
            },
            TradingMode.RECOVERY: {
                'position_multiplier': 0.4,
                'risk_multiplier': 0.5,
                'signal_threshold': 4,  # Only strongest signals
                'max_trades_per_day': 2,
                'stop_loss_multiplier': 0.6,
                'take_profit_multiplier': 2.0  # Bigger targets
            },
            TradingMode.HIBERNATION: {
                'position_multiplier': 0.1,
                'risk_multiplier': 0.3,
                'signal_threshold': 5,  # Almost no trading
                'max_trades_per_day': 1,
                'stop_loss_multiplier': 0.5,
                'take_profit_multiplier': 3.0
            }
        }
    
    def update_performance_metrics(self, daily_pnl: float, current_balance: float, 
                                   initial_balance: float, trades_today: int):
        """Update performance metrics for adaptation decisions"""
        # Calculate current drawdown
        peak_balance = max([p.get('peak_balance', initial_balance) for p in self.performance_history] + [current_balance, initial_balance])
        current_drawdown = (peak_balance - current_balance) / peak_balance * 100
        
        # Add to performance history
        perf_data = {
            'date': datetime.now(),
            'daily_pnl': daily_pnl,
            'balance': current_balance,
            'peak_balance': peak_balance,
            'drawdown': current_drawdown,
            'trades': trades_today,
            'mode': self.current_mode
        }
        
        self.performance_history.append(perf_data)
        
        # Keep only recent performance data
        if len(self.performance_history) > self.performance_window * 2:
            self.performance_history = self.performance_history[-self.performance_window:]
        
        return current_drawdown, peak_balance
    
    def detect_alt_season(self, btc_dominance: float) -> bool:
        """Detect if we're in alt season based on BTC dominance"""
        if btc_dominance < self.alt_season_threshold:
            self.dominance_streak += 1
        else:
            self.dominance_streak = 0
        
        return self.dominance_streak >= self.alt_season_streak
    
    def detect_market_cycle(self, price_data: pd.Series) -> MarketCycle:
        """Detect current market cycle phase"""
        if len(price_data) < self.cycle_lookback:
            return MarketCycle.ACCUMULATION
        
        # Calculate key metrics
        recent_prices = price_data.tail(self.cycle_lookback)
        price_trend = (recent_prices.iloc[-1] / recent_prices.iloc[0] - 1) * 100
        volatility = recent_prices.pct_change().std() * 100
        volume_trend = 0  # Simplified - would use actual volume data
        
        # Classify market cycle
        if price_trend > 15 and volatility < 5:
            return MarketCycle.MARKUP
        elif price_trend > 5 and volatility > 8:
            return MarketCycle.DISTRIBUTION  
        elif price_trend < -15 and volatility < 5:
            return MarketCycle.MARKDOWN
        else:
            return MarketCycle.ACCUMULATION
    
    def get_seasonal_adjustment(self, current_month: int) -> float:
        """Get seasonal adjustment multiplier based on historical patterns"""
        if current_month in self.favorable_months:
            return 1.2  # Increase aggression in favorable months
        elif current_month in self.unfavorable_months:
            return 0.8  # Reduce aggression in unfavorable months
        else:
            return 1.0  # Neutral months
    
    def determine_optimal_mode(self, market_intelligence: Dict, price_data: pd.Series, 
                              current_balance: float, initial_balance: float) -> TradingMode:
        """Determine optimal trading mode based on all available information"""
        
        # Get current performance metrics
        if self.performance_history:
            current_drawdown = self.performance_history[-1]['drawdown']
            recent_performance = sum([p['daily_pnl'] for p in self.performance_history[-5:]])
        else:
            current_drawdown = 0
            recent_performance = 0
        
        # Priority 1: Recovery mode if significant drawdown
        if current_drawdown > self.drawdown_threshold:
            return TradingMode.RECOVERY
        
        # Priority 2: Hibernation if extreme losses
        if current_balance < initial_balance * 0.7:  # 30%+ loss
            return TradingMode.HIBERNATION
        
        # Priority 3: Alt season detection
        btc_dominance = market_intelligence.get('btc_dominance', 45.0)
        if self.detect_alt_season(btc_dominance):
            return TradingMode.ALT_SEASON
        
        # Priority 4: Market cycle and seasonal adjustments
        current_month = datetime.now().month
        seasonal_multiplier = self.get_seasonal_adjustment(current_month)
        market_cycle = self.detect_market_cycle(price_data)
        
        # Base mode selection on recent performance and market conditions
        if recent_performance > 0 and seasonal_multiplier > 1.0:
            if market_cycle in [MarketCycle.MARKUP, MarketCycle.ACCUMULATION]:
                return TradingMode.AGGRESSIVE
            else:
                return TradingMode.STANDARD
        elif recent_performance < -500:  # Recent losses
            return TradingMode.CONSERVATIVE
        else:
            return TradingMode.STANDARD
    
    def apply_mode_adjustments(self, base_position_size: float, base_risk: float, 
                              signal_strength: int) -> Tuple[float, float, bool]:
        """Apply current mode adjustments to trading parameters"""
        
        mode_params = self.mode_parameters[self.current_mode]
        
        # Adjust position size and risk
        adjusted_position_size = base_position_size * mode_params['position_multiplier']
        adjusted_risk = base_risk * mode_params['risk_multiplier']
        
        # Check if signal meets threshold
        signal_meets_threshold = abs(signal_strength) >= mode_params['signal_threshold']
        
        return adjusted_position_size, adjusted_risk, signal_meets_threshold
    
    def update_trading_mode(self, market_intelligence: Dict, price_data: pd.Series,
                           current_balance: float, initial_balance: float, 
                           daily_pnl: float = 0, trades_today: int = 0) -> bool:
        """Update trading mode based on current conditions. Returns True if mode changed."""
        
        # Update performance metrics
        current_drawdown, peak_balance = self.update_performance_metrics(
            daily_pnl, current_balance, initial_balance, trades_today
        )
        
        # Determine optimal mode
        optimal_mode = self.determine_optimal_mode(
            market_intelligence, price_data, current_balance, initial_balance
        )
        
        # Check if mode should change
        mode_changed = False
        if optimal_mode != self.current_mode:
            self.previous_mode = self.current_mode
            self.current_mode = optimal_mode
            mode_changed = True
            
            # Log mode change
            self.mode_history.append({
                'timestamp': datetime.now(),
                'from_mode': self.previous_mode.value,
                'to_mode': self.current_mode.value,
                'reason': self._get_mode_change_reason(market_intelligence, current_drawdown),
                'balance': current_balance,
                'drawdown': current_drawdown
            })
            
            print(f"\n🔄 MODE CHANGE: {self.previous_mode.value} → {self.current_mode.value}")
            print(f"💰 Balance: ${current_balance:,.0f} (Drawdown: {current_drawdown:.1f}%)")
            print(f"📝 Reason: {self.mode_history[-1]['reason']}")
        
        return mode_changed
    
    def _get_mode_change_reason(self, market_intelligence: Dict, current_drawdown: float) -> str:
        """Generate human-readable reason for mode change"""
        
        if self.current_mode == TradingMode.RECOVERY:
            return f"High drawdown ({current_drawdown:.1f}%) - switching to recovery mode"
        elif self.current_mode == TradingMode.HIBERNATION:
            return "Extreme losses - minimizing risk exposure"
        elif self.current_mode == TradingMode.ALT_SEASON:
            return f"Alt season detected (BTC dom: {market_intelligence.get('btc_dominance', 45):.1f}%)"
        elif self.current_mode == TradingMode.AGGRESSIVE:
            return "Favorable conditions - increasing aggression"
        elif self.current_mode == TradingMode.CONSERVATIVE:
            return "Recent losses - reducing risk"
        else:
            return "Standard market conditions"
    
    def get_current_parameters(self) -> Dict:
        """Get current mode parameters for strategy use"""
        base_params = self.mode_parameters[self.current_mode].copy()
        
        # Add seasonal adjustment
        seasonal_mult = self.get_seasonal_adjustment(datetime.now().month)
        base_params['seasonal_multiplier'] = seasonal_mult
        
        # Apply seasonal adjustment to position and risk multipliers
        base_params['position_multiplier'] *= seasonal_mult
        base_params['risk_multiplier'] *= seasonal_mult
        
        return base_params
    
    def get_mode_summary(self) -> Dict:
        """Get summary of current mode and recent changes"""
        return {
            'current_mode': self.current_mode.value,
            'previous_mode': self.previous_mode.value,
            'mode_changes_today': len([m for m in self.mode_history if m['timestamp'].date() == datetime.now().date()]),
            'total_mode_changes': len(self.mode_history),
            'current_parameters': self.get_current_parameters(),
            'performance_window': len(self.performance_history),
            'dominance_streak': self.dominance_streak
        }

def test_dynamic_adapter():
    """Test the dynamic strategy adapter"""
    print("🧠 TESTING DYNAMIC STRATEGY ADAPTER")
    print("=" * 60)
    
    # Mock base strategy
    class MockStrategy:
        def __init__(self):
            self.current_balance = 10000
            self.initial_balance = 10000
    
    # Create adapter
    base_strategy = MockStrategy()
    adapter = DynamicStrategyAdapter(base_strategy)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Normal Market',
            'market_intel': {'btc_dominance': 45.0, 'regime': 'neutral'},
            'price_data': pd.Series([100, 102, 101, 103, 105] * 10),
            'balance': 10500,
            'daily_pnl': 50
        },
        {
            'name': 'Alt Season',
            'market_intel': {'btc_dominance': 38.0, 'regime': 'alt_season'},
            'price_data': pd.Series([100, 110, 120, 115, 125] * 10),
            'balance': 11000,
            'daily_pnl': 200
        },
        {
            'name': 'High Drawdown',
            'market_intel': {'btc_dominance': 48.0, 'regime': 'btc_season'},
            'price_data': pd.Series([100, 95, 90, 85, 80] * 10),
            'balance': 8200,
            'daily_pnl': -300
        },
        {
            'name': 'Extreme Losses',
            'market_intel': {'btc_dominance': 52.0, 'regime': 'btc_season'},
            'price_data': pd.Series([100, 90, 80, 70, 60] * 10),
            'balance': 6500,
            'daily_pnl': -500
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(scenarios):
        print(f"\n📊 Scenario {i+1}: {scenario['name']}")
        print("-" * 40)
        
        # Update mode
        mode_changed = adapter.update_trading_mode(
            scenario['market_intel'],
            scenario['price_data'],
            scenario['balance'],
            10000,
            scenario['daily_pnl']
        )
        
        # Get current parameters
        params = adapter.get_current_parameters()
        summary = adapter.get_mode_summary()
        
        print(f"Mode: {summary['current_mode'].upper()}")
        print(f"Position Multiplier: {params['position_multiplier']:.2f}x")
        print(f"Risk Multiplier: {params['risk_multiplier']:.2f}x")
        print(f"Signal Threshold: ≥{params['signal_threshold']}")
        print(f"Max Trades/Day: {params['max_trades_per_day']}")
        
        # Test parameter application
        test_pos, test_risk, signal_ok = adapter.apply_mode_adjustments(1000, 2.0, 3)
        print(f"Sample Trade: ${test_pos:.0f} position, {test_risk:.1f}% risk, Signal OK: {signal_ok}")
    
    print("\n" + "=" * 60)
    print("💡 DYNAMIC ADAPTER FEATURES:")
    print("• Automatic mode switching based on performance")
    print("• Alt season detection and exploitation")
    print("• Drawdown recovery protocols")
    print("• Seasonal pattern recognition")
    print("• Market cycle awareness")

if __name__ == "__main__":
    test_dynamic_adapter()