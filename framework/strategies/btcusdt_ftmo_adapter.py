"""
BTCUSDT FTMO 1H Strategy Adapter for Universal Framework
Adapts the proven FTMO 1H strategy for use with the universal backtesting framework
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add crypto strategies to path
crypto_path = Path(__file__).parent.parent.parent / "crypto" / "strategies"
sys.path.append(str(crypto_path))

try:
    from btcusdt_ftmo_1h_strategy import BTCUSDTFTMO1HStrategy
    print("✅ Successfully imported BTCUSDT FTMO 1H Strategy")
except ImportError as e:
    print(f"❌ Failed to import FTMO strategy: {e}")

from ..core.universal_strategy import UniversalStrategy, AssetType
from ..core.config import StrategyConfig

class BTCUSDTFTMOAdapter(UniversalStrategy):
    """Adapter to integrate BTCUSDT FTMO 1H Strategy with Universal Framework"""
    
    def __init__(self, risk_profile='moderate', challenge_phase=1):
        """Initialize FTMO strategy adapter"""
        
        # Risk profile mappings
        risk_configs = {
            'conservative': {
                'risk_per_trade': 0.5,  # 0.5% per trade
                'max_daily_loss': 1.0,
                'max_overall_loss': 3.0,
                'min_confluence': 4,    # Higher threshold
                'position_multiplier': 0.7
            },
            'moderate': {
                'risk_per_trade': 1.0,  # 1.0% per trade
                'max_daily_loss': 1.5,
                'max_overall_loss': 5.0,
                'min_confluence': 3,
                'position_multiplier': 1.0
            },
            'aggressive': {
                'risk_per_trade': 1.5,  # 1.5% per trade
                'max_daily_loss': 2.0,
                'max_overall_loss': 6.0,
                'min_confluence': 3,
                'position_multiplier': 1.2
            }
        }
        
        risk_config = risk_configs.get(risk_profile, risk_configs['moderate'])
        
        # Create strategy configuration
        config = StrategyConfig(
            name=f"BTCUSDT FTMO 1H {risk_profile.title()} Phase {challenge_phase}",
            asset_type=AssetType.CRYPTO,
            timeframe='1h',
            risk_per_trade=risk_config['risk_per_trade'] / 100,
            max_daily_loss=risk_config['max_daily_loss'] / 100,
            max_overall_loss=risk_config['max_overall_loss'] / 100,
            commission=0.001,  # 0.1% commission
            slippage=0.0005    # 0.05% slippage
        )
        
        super().__init__(config)
        
        self.risk_profile = risk_profile
        self.challenge_phase = challenge_phase
        self.risk_config = risk_config
        
        # Initialize the original FTMO strategy
        initial_cash = 100000
        self.ftmo_strategy = BTCUSDTFTMO1HStrategy(
            account_size=initial_cash, 
            challenge_phase=challenge_phase
        )
        
        # Override some parameters based on risk profile
        self.ftmo_strategy.daily_loss_cutoff_pct = risk_config['max_daily_loss']
        self.ftmo_strategy.overall_loss_cutoff_pct = risk_config['max_overall_loss']
        
        # Update position sizing based on risk profile
        multiplier = risk_config['position_multiplier']
        for score in self.ftmo_strategy.base_position_sizing:
            original_risk, leverage = self.ftmo_strategy.base_position_sizing[score]
            if original_risk > 0:
                new_risk = min(original_risk * multiplier, risk_config['risk_per_trade'])
                self.ftmo_strategy.base_position_sizing[score] = (new_risk, leverage)
        
        self.min_confluence = risk_config['min_confluence']
        
        print(f"🎯 BTCUSDT FTMO Adapter initialized: {risk_profile} risk, Phase {challenge_phase}")
        print(f"   Risk per trade: {risk_config['risk_per_trade']:.1f}%")
        print(f"   Max daily loss: {risk_config['max_daily_loss']:.1f}%")
        print(f"   Min confluence: {self.min_confluence}")

    def calculate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Calculate trading signals using FTMO strategy logic"""
        try:
            if len(data) < 100:
                return pd.Series(0, index=data.index)
            
            # Use the original FTMO strategy's trend composite calculation
            composite_score = self.ftmo_strategy.calculate_bitcoin_trend_composite(data.copy())
            
            # Apply minimum confluence filter
            signals = pd.Series(0, index=data.index)
            
            # Generate signals based on composite score and confluence threshold
            long_signals = composite_score >= self.min_confluence
            short_signals = composite_score <= -self.min_confluence
            
            signals[long_signals] = 1   # Buy signal
            signals[short_signals] = -1  # Sell signal
            
            return signals
            
        except Exception as e:
            print(f"❌ Error calculating FTMO signals: {e}")
            return pd.Series(0, index=data.index)

    def calculate_position_size(self, data: pd.DataFrame, signal: float, current_price: float, index: int) -> float:
        """Calculate position size using FTMO strategy logic"""
        try:
            if abs(signal) < 1:
                return 0
            
            # Get current hour for hourly trade limits
            current_time = data.index[index]
            current_hour = current_time.hour
            
            # Assess Bitcoin volatility using FTMO method
            volatility_mode = self.ftmo_strategy.assess_bitcoin_volatility(data, index)
            
            # Calculate ATR for position sizing
            atr_data = self._calculate_atr(data, index)
            current_atr = atr_data if atr_data > 0 else current_price * 0.03
            
            # Use FTMO's composite score for position sizing
            try:
                composite_score = self.ftmo_strategy.calculate_bitcoin_trend_composite(data.iloc[:index+1])
                if len(composite_score) > 0:
                    current_score = composite_score.iloc[-1]
                else:
                    current_score = signal * 3  # Fallback
            except:
                current_score = signal * 3  # Fallback
            
            # Use FTMO's position sizing calculation
            position_size, stop_distance, risk_pct, position_value = self.ftmo_strategy.calculate_safe_position_size_bitcoin(
                current_score, current_price, current_atr, current_hour, volatility_mode
            )
            
            if position_size <= 0:
                return 0
            
            # Convert to our framework's position size format (percentage of portfolio)
            current_balance = self.ftmo_strategy.current_balance
            if current_balance <= 0:
                current_balance = 100000  # Fallback
            
            position_percentage = (position_value / current_balance)
            
            # Apply signal direction
            if signal < 0:
                position_percentage = -position_percentage
            
            return min(abs(position_percentage), 0.3) * (1 if signal > 0 else -1)  # Cap at 30%
            
        except Exception as e:
            print(f"❌ Error calculating FTMO position size: {e}")
            return 0

    def _calculate_atr(self, data: pd.DataFrame, index: int, period: int = 14) -> float:
        """Calculate Average True Range"""
        if index < period:
            return data['Close'].iloc[index] * 0.03  # Fallback to 3%
        
        try:
            recent_data = data.iloc[max(0, index-period):index+1]
            
            high_low = recent_data['High'] - recent_data['Low']
            high_close = abs(recent_data['High'] - recent_data['Close'].shift(1))
            low_close = abs(recent_data['Low'] - recent_data['Close'].shift(1))
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=min(period, len(tr))).mean().iloc[-1]
            
            return atr if not pd.isna(atr) else data['Close'].iloc[index] * 0.03
            
        except:
            return data['Close'].iloc[index] * 0.03

    def should_exit_position(self, data: pd.DataFrame, current_position: float, 
                           entry_price: float, current_price: float, 
                           days_held: int, index: int) -> tuple:
        """Determine if position should be closed using FTMO exit logic"""
        
        if current_position == 0:
            return False, "No Position"
        
        try:
            # Calculate ATR for stop loss
            current_atr = self._calculate_atr(data, index)
            
            # FTMO-style stop loss (1.2x ATR)
            atr_multiplier = 1.2
            stop_distance = current_atr * atr_multiplier
            
            if current_position > 0:  # Long position
                stop_price = entry_price - stop_distance
                take_profit = entry_price + (2.5 * stop_distance)  # 2.5:1 RR
                
                if current_price <= stop_price:
                    return True, "Stop Loss"
                elif current_price >= take_profit:
                    return True, "Take Profit"
                    
            else:  # Short position
                stop_price = entry_price + stop_distance
                take_profit = entry_price - (2.5 * stop_distance)
                
                if current_price >= stop_price:
                    return True, "Stop Loss"
                elif current_price <= take_profit:
                    return True, "Take Profit"
            
            # Time-based exit after 24 hours (24 1-hour bars)
            if days_held >= 24:
                return True, "Time Exit"
            
            return False, "Hold"
            
        except Exception as e:
            print(f"❌ Error in exit logic: {e}")
            return True, "Error Exit"

    def get_strategy_info(self) -> dict:
        """Return strategy information"""
        return {
            'name': self.config.name,
            'type': 'FTMO Bitcoin 1H Strategy',
            'risk_profile': self.risk_profile,
            'challenge_phase': self.challenge_phase,
            'timeframe': '1h',
            'asset_class': 'Cryptocurrency',
            'risk_per_trade': f"{self.risk_config['risk_per_trade']:.1f}%",
            'max_daily_loss': f"{self.risk_config['max_daily_loss']:.1f}%",
            'min_confluence': self.min_confluence,
            'features': [
                'FTMO-compliant risk management',
                'Bitcoin volatility adaptation',
                'Multi-confluence scoring',
                'Hourly trade limits',
                'Emergency stop mechanisms',
                'Trailing stops',
                '2.5:1 risk/reward targets'
            ]
        }


def create_btcusdt_ftmo_strategy(risk_profile='moderate', challenge_phase=1):
    """Factory function to create BTCUSDT FTMO strategy"""
    return BTCUSDTFTMOAdapter(
        risk_profile=risk_profile,
        challenge_phase=challenge_phase
    )


if __name__ == "__main__":
    # Test the adapter
    print("🧪 Testing BTCUSDT FTMO Adapter")
    
    strategy = create_btcusdt_ftmo_strategy('moderate', 1)
    info = strategy.get_strategy_info()
    
    print(f"\n📊 Strategy Info:")
    for key, value in info.items():
        if key == 'features':
            print(f"   {key}: {', '.join(value)}")
        else:
            print(f"   {key}: {value}")