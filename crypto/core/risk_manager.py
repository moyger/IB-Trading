#!/usr/bin/env python3
"""
Advanced Risk Management Module for BTCUSDT Strategy
Implements proven FTMO-style risk controls with crypto market adaptations

Key Features:
- Real-time risk buffer monitoring
- Emergency stop mechanisms
- Dynamic position sizing
- Performance-based risk adjustment
- Comprehensive violation detection
- Profit acceleration controls
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class CryptoRiskManager:
    """Advanced risk management for crypto trading strategies"""
    
    def __init__(self, account_size: float, risk_profile: str = 'moderate'):
        """
        Initialize crypto risk manager
        
        Args:
            account_size: Initial trading capital
            risk_profile: 'conservative', 'moderate', 'aggressive'
        """
        self.initial_balance = account_size
        self.current_balance = account_size
        self.risk_profile = risk_profile
        
        # Initialize risk parameters
        self._init_risk_parameters()
        
        # Risk tracking
        self.daily_starting_balance = account_size
        self.max_balance_today = account_size
        self.max_balance_ever = account_size
        self.current_date = None
        
        # State tracking
        self.emergency_stop = False
        self.daily_emergency_stop = False
        self.can_trade_today = True
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # Performance tracking
        self.risk_alerts = []
        self.violation_history = []
        self.daily_pnl_history = []
        self.trades_today = 0
        self.max_trades_per_day = 10  # Crypto market allows more frequent trading
        
        # Advanced features
        self.profit_acceleration_mode = False
        self.drawdown_protection_mode = False
        self.risk_budget_used = 0.0
        
        print(f"🛡️ CRYPTO RISK MANAGER INITIALIZED ({risk_profile.upper()})")
        print(f"💰 Account Size: ${account_size:,}")
        print(f"⚠️ Daily Loss Limit: {self.max_daily_loss_pct}%")
        print(f"🔴 Emergency Stop: {self.daily_loss_emergency_pct}%")
        
    def _init_risk_parameters(self):
        """Initialize risk parameters based on profile"""
        risk_configs = {
            'conservative': {
                'max_daily_loss_pct': 3.0,
                'max_overall_loss_pct': 8.0,
                'daily_loss_cutoff_pct': 1.0,
                'overall_loss_cutoff_pct': 4.0,
                'daily_loss_emergency_pct': 0.5,
                'max_risk_per_trade_hard_cap': 1.5,
                'profit_target_pct': 15.0,
                'max_consecutive_losses': 3,
                'max_daily_risk_budget': 4.0,  # Total daily risk exposure
            },
            'moderate': {
                'max_daily_loss_pct': 4.0,
                'max_overall_loss_pct': 10.0,
                'daily_loss_cutoff_pct': 1.5,
                'overall_loss_cutoff_pct': 5.0,
                'daily_loss_emergency_pct': 1.0,
                'max_risk_per_trade_hard_cap': 2.0,
                'profit_target_pct': 20.0,
                'max_consecutive_losses': 4,
                'max_daily_risk_budget': 6.0,
            },
            'aggressive': {
                'max_daily_loss_pct': 6.0,
                'max_overall_loss_pct': 12.0,
                'daily_loss_cutoff_pct': 2.0,
                'overall_loss_cutoff_pct': 6.0,
                'daily_loss_emergency_pct': 1.5,
                'max_risk_per_trade_hard_cap': 3.0,
                'profit_target_pct': 25.0,
                'max_consecutive_losses': 5,
                'max_daily_risk_budget': 8.0,
            }
        }
        
        config = risk_configs[self.risk_profile]
        for key, value in config.items():
            setattr(self, key, value)
    
    def update_balance(self, new_balance: float, timestamp: datetime = None):
        """Update balance and perform risk checks"""
        if timestamp is None:
            timestamp = datetime.now()
            
        current_date = timestamp.date()
        
        # Check for new day
        if current_date != self.current_date:
            self._start_new_day(current_date, new_balance)
        
        # Update balance
        previous_balance = self.current_balance
        self.current_balance = new_balance
        
        # Update max balance tracking
        self.max_balance_today = max(self.max_balance_today, new_balance)
        self.max_balance_ever = max(self.max_balance_ever, new_balance)
        
        # Perform risk checks
        self._perform_risk_checks()
        
        # Update daily P&L tracking
        daily_pnl_pct = (new_balance - self.daily_starting_balance) / self.initial_balance * 100
        self.daily_pnl_history.append({
            'date': current_date,
            'daily_pnl_pct': daily_pnl_pct,
            'balance': new_balance,
            'max_balance_today': self.max_balance_today
        })
    
    def _start_new_day(self, current_date, new_balance: float):
        """Initialize new trading day"""
        self.current_date = current_date
        self.daily_starting_balance = new_balance
        self.max_balance_today = new_balance
        self.daily_emergency_stop = False
        self.can_trade_today = True
        self.trades_today = 0
        self.risk_budget_used = 0.0
        
        # Check if we should enable profit acceleration
        self._check_profit_acceleration()
        
        # Check for drawdown protection
        self._check_drawdown_protection()
    
    def can_open_position(self, risk_pct: float, position_value: float = 0) -> Tuple[bool, str]:
        """
        Check if new position can be opened
        
        Args:
            risk_pct: Risk percentage for the trade
            position_value: Total position value
            
        Returns:
            (can_open, reason)
        """
        # Emergency stops
        if self.emergency_stop:
            return False, "Emergency stop active - overall loss limit reached"
        
        if self.daily_emergency_stop:
            return False, "Daily emergency stop active"
        
        if not self.can_trade_today:
            return False, "Daily trading disabled"
        
        # Trade count limits
        if self.trades_today >= self.max_trades_per_day:
            return False, f"Maximum trades per day reached ({self.max_trades_per_day})"
        
        # Risk budget check
        if self.risk_budget_used + risk_pct > self.max_daily_risk_budget:
            return False, f"Daily risk budget exceeded ({self.risk_budget_used:.1f}% + {risk_pct:.1f}% > {self.max_daily_risk_budget}%)"
        
        # Consecutive loss protection
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"Too many consecutive losses ({self.consecutive_losses})"
        
        # Single trade risk limit
        if risk_pct > self.max_risk_per_trade_hard_cap:
            return False, f"Risk per trade too high ({risk_pct:.2f}% > {self.max_risk_per_trade_hard_cap}%)"
        
        # Drawdown protection
        if self.drawdown_protection_mode and risk_pct > self.max_risk_per_trade_hard_cap * 0.5:
            return False, "Drawdown protection active - reduced position sizes only"
        
        return True, "Risk check passed"
    
    def calculate_safe_risk_pct(self, base_risk_pct: float, confluence_score: int = 0) -> float:
        """
        Calculate safe risk percentage with dynamic adjustments
        
        Args:
            base_risk_pct: Base risk percentage
            confluence_score: Signal confluence strength (0-7)
            
        Returns:
            Adjusted risk percentage
        """
        risk_pct = base_risk_pct
        
        # Performance-based adjustments
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        # Profit acceleration mode
        if self.profit_acceleration_mode and profit_pct > 3.0:
            acceleration_factor = min(1.4, 1.0 + (profit_pct * 0.02))
            risk_pct *= acceleration_factor
        
        # Win streak bonus
        if self.consecutive_wins >= 3:
            streak_bonus = min(1.2, 1.0 + (self.consecutive_wins * 0.05))
            risk_pct *= streak_bonus
        
        # Loss streak reduction
        if self.consecutive_losses >= 2:
            loss_penalty = max(0.6, 1.0 - (self.consecutive_losses * 0.15))
            risk_pct *= loss_penalty
        
        # Confluence-based adjustment
        if confluence_score >= 6:  # Very strong signal
            risk_pct *= 1.15
        elif confluence_score >= 5:  # Strong signal
            risk_pct *= 1.1
        elif confluence_score <= 3:  # Weak signal
            risk_pct *= 0.85
        
        # Drawdown protection
        if self.drawdown_protection_mode:
            risk_pct *= 0.6
        
        # Hard caps
        risk_pct = min(risk_pct, self.max_risk_per_trade_hard_cap)
        
        # Risk buffer protection
        available_buffer = self._calculate_available_risk_buffer()
        if risk_pct > available_buffer:
            risk_pct = max(0, available_buffer * 0.8)  # Leave some buffer
        
        return max(0, risk_pct)
    
    def register_trade_open(self, risk_pct: float):
        """Register new trade opening"""
        self.trades_today += 1
        self.risk_budget_used += risk_pct
    
    def register_trade_close(self, pnl: float, result: str):
        """Register trade closing and update streaks"""
        if result == "WIN":
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif result == "LOSS":
            self.consecutive_wins = 0
            self.consecutive_losses += 1
        
        # Check for risk alerts
        pnl_pct = pnl / self.initial_balance * 100
        if abs(pnl_pct) > 1.0:  # Alert for large moves
            alert = f"Large {'gain' if pnl > 0 else 'loss'}: {pnl_pct:+.2f}%"
            self.risk_alerts.append({
                'timestamp': datetime.now(),
                'alert': alert,
                'balance': self.current_balance
            })
    
    def _perform_risk_checks(self):
        """Perform comprehensive risk checks"""
        # Calculate current losses
        daily_loss_pct = (self.daily_starting_balance - self.current_balance) / self.initial_balance * 100
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        
        # Daily emergency stop check
        if daily_loss_pct >= self.daily_loss_emergency_pct:
            self.daily_emergency_stop = True
            self.can_trade_today = False
            violation = f"Daily emergency stop triggered: {daily_loss_pct:.2f}% loss"
            self.violation_history.append({
                'date': self.current_date,
                'type': 'DAILY_EMERGENCY_STOP',
                'description': violation
            })
            self.risk_alerts.append({
                'timestamp': datetime.now(),
                'alert': violation,
                'balance': self.current_balance
            })
        
        # Daily loss cutoff check
        elif daily_loss_pct >= self.daily_loss_cutoff_pct:
            self.can_trade_today = False
            violation = f"Daily trading stopped: {daily_loss_pct:.2f}% loss reached cutoff"
            self.risk_alerts.append({
                'timestamp': datetime.now(),
                'alert': violation,
                'balance': self.current_balance
            })
        
        # Overall emergency stop check
        if overall_loss_pct >= self.overall_loss_cutoff_pct:
            self.emergency_stop = True
            violation = f"Overall emergency stop triggered: {overall_loss_pct:.2f}% loss"
            self.violation_history.append({
                'date': self.current_date,
                'type': 'OVERALL_EMERGENCY_STOP',
                'description': violation
            })
            self.risk_alerts.append({
                'timestamp': datetime.now(),
                'alert': violation,
                'balance': self.current_balance
            })
    
    def _calculate_available_risk_buffer(self) -> float:
        """Calculate remaining risk buffer"""
        daily_loss_pct = (self.daily_starting_balance - self.current_balance) / self.initial_balance * 100
        daily_buffer = self.daily_loss_cutoff_pct - daily_loss_pct
        
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        overall_buffer = self.overall_loss_cutoff_pct - overall_loss_pct
        
        return min(daily_buffer, overall_buffer, self.max_daily_risk_budget - self.risk_budget_used)
    
    def _check_profit_acceleration(self):
        """Check if profit acceleration should be enabled"""
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        # Enable profit acceleration if we're profitable with consecutive wins
        if profit_pct > 2.0 and self.consecutive_wins >= 2:
            available_buffer = self._calculate_available_risk_buffer()
            if available_buffer > 2.0:  # Need sufficient buffer
                self.profit_acceleration_mode = True
            else:
                self.profit_acceleration_mode = False
        else:
            self.profit_acceleration_mode = False
    
    def _check_drawdown_protection(self):
        """Check if drawdown protection should be enabled"""
        # Enable if we've had significant losses or consecutive losses
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        
        if overall_loss_pct > 3.0 or self.consecutive_losses >= 3:
            self.drawdown_protection_mode = True
        else:
            self.drawdown_protection_mode = False
    
    def get_risk_summary(self) -> Dict:
        """Get comprehensive risk summary"""
        daily_loss_pct = (self.daily_starting_balance - self.current_balance) / self.initial_balance * 100
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        max_drawdown = 0
        peak_balance = self.initial_balance
        for record in self.daily_pnl_history:
            peak_balance = max(peak_balance, record['balance'])
            drawdown = (peak_balance - record['balance']) / self.initial_balance * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'current_balance': self.current_balance,
            'profit_loss_pct': profit_pct,
            'daily_pnl_pct': daily_loss_pct,
            'overall_loss_pct': overall_loss_pct,
            'max_drawdown': max_drawdown,
            'risk_limits': {
                'daily_loss_limit': self.max_daily_loss_pct,
                'overall_loss_limit': self.max_overall_loss_pct,
                'daily_emergency_limit': self.daily_loss_emergency_pct,
            },
            'risk_buffers': {
                'daily_buffer': max(0, self.daily_loss_cutoff_pct - daily_loss_pct),
                'overall_buffer': max(0, self.overall_loss_cutoff_pct - overall_loss_pct),
                'daily_risk_budget_remaining': max(0, self.max_daily_risk_budget - self.risk_budget_used)
            },
            'trading_state': {
                'can_trade_today': self.can_trade_today,
                'emergency_stop': self.emergency_stop,
                'daily_emergency_stop': self.daily_emergency_stop,
                'profit_acceleration_mode': self.profit_acceleration_mode,
                'drawdown_protection_mode': self.drawdown_protection_mode
            },
            'performance': {
                'consecutive_wins': self.consecutive_wins,
                'consecutive_losses': self.consecutive_losses,
                'trades_today': self.trades_today,
                'total_risk_alerts': len(self.risk_alerts),
                'total_violations': len(self.violation_history)
            }
        }
    
    def print_risk_status(self):
        """Print current risk status"""
        summary = self.get_risk_summary()
        
        print(f"\n🛡️ CRYPTO RISK MANAGER STATUS")
        print("=" * 50)
        print(f"Current Balance:        ${summary['current_balance']:,.2f}")
        print(f"Profit/Loss:            {summary['profit_loss_pct']:+.2f}%")
        print(f"Daily P&L:              {summary['daily_pnl_pct']:+.2f}%")
        print(f"Max Drawdown:           {summary['max_drawdown']:.2f}%")
        
        print(f"\n⚠️ RISK BUFFERS:")
        buffers = summary['risk_buffers']
        print(f"Daily Buffer:           {buffers['daily_buffer']:.2f}%")
        print(f"Overall Buffer:         {buffers['overall_buffer']:.2f}%")
        print(f"Risk Budget Left:       {buffers['daily_risk_budget_remaining']:.2f}%")
        
        print(f"\n🚦 TRADING STATE:")
        state = summary['trading_state']
        print(f"Can Trade Today:        {'✅' if state['can_trade_today'] else '❌'}")
        print(f"Emergency Stop:         {'🔴' if state['emergency_stop'] else '✅'}")
        print(f"Profit Acceleration:    {'🚀' if state['profit_acceleration_mode'] else '❌'}")
        print(f"Drawdown Protection:    {'🛡️' if state['drawdown_protection_mode'] else '❌'}")
        
        print(f"\n📊 PERFORMANCE:")
        perf = summary['performance']
        print(f"Win Streak:             {perf['consecutive_wins']}")
        print(f"Loss Streak:            {perf['consecutive_losses']}")
        print(f"Trades Today:           {perf['trades_today']}")
        print(f"Risk Alerts:            {perf['total_risk_alerts']}")
        print(f"Violations:             {perf['total_violations']}")
        
        if perf['total_violations'] > 0:
            print(f"\n❌ RECENT VIOLATIONS:")
            for violation in self.violation_history[-3:]:  # Show last 3
                print(f"   • {violation['date']}: {violation['description']}")
    
    def check_compliance(self) -> Tuple[bool, List[str]]:
        """Check overall strategy compliance"""
        violations = []
        
        # Check for hard violations
        daily_loss_pct = (self.daily_starting_balance - self.current_balance) / self.initial_balance * 100
        overall_loss_pct = (self.initial_balance - self.current_balance) / self.initial_balance * 100
        
        if daily_loss_pct >= self.max_daily_loss_pct:
            violations.append(f"Daily loss limit exceeded: {daily_loss_pct:.2f}% > {self.max_daily_loss_pct}%")
        
        if overall_loss_pct >= self.max_overall_loss_pct:
            violations.append(f"Overall loss limit exceeded: {overall_loss_pct:.2f}% > {self.max_overall_loss_pct}%")
        
        # Add historical violations
        for violation in self.violation_history:
            violations.append(f"{violation['date']}: {violation['description']}")
        
        return len(violations) == 0, violations


if __name__ == "__main__":
    print("🧪 Testing Crypto Risk Manager")
    print("=" * 40)
    
    # Test risk manager
    rm = CryptoRiskManager(account_size=10000, risk_profile='moderate')
    
    # Simulate some trades
    print("\n📊 Initial Status:")
    rm.print_risk_status()
    
    # Test position opening
    can_open, reason = rm.can_open_position(risk_pct=1.5)
    print(f"\nCan open position (1.5% risk): {can_open}")
    print(f"Reason: {reason}")
    
    # Test safe risk calculation
    safe_risk = rm.calculate_safe_risk_pct(base_risk_pct=2.0, confluence_score=6)
    print(f"Safe risk (base 2%, confluence 6): {safe_risk:.2f}%")
    
    # Simulate a loss
    rm.update_balance(9500)  # 5% loss
    print(f"\n📊 After 5% Loss:")
    rm.print_risk_status()
    
    # Check compliance
    compliant, violations = rm.check_compliance()
    print(f"\nCompliance Status: {'✅ COMPLIANT' if compliant else '❌ VIOLATIONS'}")
    
    print("\n✅ Risk manager test completed!")