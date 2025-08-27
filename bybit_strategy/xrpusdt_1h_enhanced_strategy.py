#!/usr/bin/env python3
"""
XRPUSDT 1H Enhanced Strategy with Complete Phase 3 Optimization
Adapted from the successful ADAUSDT Phase 3 strategy for XRP trading

Complete Feature Set:
- Phase 1: Optimized parameters (ADX thresholds, volume, signals, position sizing)
- Phase 2: Market intelligence (BTC dominance tracking, correlation analysis)  
- Phase 3: Dynamic adaptation (mode switching, drawdown recovery, alt season detection)

Key Adaptations for XRP:
- Adjusted volatility thresholds for XRP's unique price behavior
- Enhanced position sizing for XRP's higher volatility
- Calibrated ADX parameters for XRP trend detection
- Maintains proven regime filter methodology
"""

# Import the enhanced strategy class
from btcusdt_1h_enhanced_strategy_saved import BTCUSDT1HEnhancedStrategy
from altcoin_market_intelligence import AltcoinMarketIntelligence
from dynamic_strategy_adapter import DynamicStrategyAdapter, TradingMode
import pandas as pd

class XRPUSDT1HEnhancedStrategy(BTCUSDT1HEnhancedStrategy):
    """
    XRPUSDT 1H Enhanced Strategy with Complete Phase 3 Optimization
    Inherits from proven BTCUSDT strategy with XRP-specific adjustments
    """
    
    def __init__(self, account_size=10000, risk_profile='moderate'):
        """Initialize XRPUSDT strategy with XRP-specific parameters"""
        super().__init__(account_size, risk_profile)
        
        # Override symbol for XRP
        self.symbol = "XRP-USD"
        
        # Initialize market intelligence system
        self.market_intelligence = AltcoinMarketIntelligence()
        self.market_analysis_cache = {}
        
        # Initialize dynamic strategy adapter (Phase 3)
        self.dynamic_adapter = DynamicStrategyAdapter(self)
        self.mode_updates_today = 0
        
        # XRP-specific adjustments
        # XRP has unique volatility patterns, adjust risk parameters accordingly
        if risk_profile == 'conservative':
            self.max_risk_per_trade_hard_cap = 1.1  # Slightly lower for XRP
            self.daily_loss_emergency_pct = 0.4     # Tighter emergency stop
        elif risk_profile == 'aggressive':
            self.max_risk_per_trade_hard_cap = 2.6  # Slightly lower than BTC
            self.daily_loss_emergency_pct = 1.2     # Slightly tighter
        else:  # moderate
            self.max_risk_per_trade_hard_cap = 1.7  # Slightly lower than BTC
            self.daily_loss_emergency_pct = 0.8     # Tighter for XRP
        
        # Optimized XRP regime filter adjustments (Phase 1 + 2 optimizations)
        self.adx_strong_threshold = 19          # Optimized for XRP trend detection
        self.adx_moderate_threshold = 14        # More permissive for XRP signals
        self.volume_threshold_multiplier = 0.55 # Adjusted for XRP volume patterns
        self.volatility_threshold_multiplier = 0.65  # XRP-specific volatility
        
        # Optimized XRP position sizing - Phase 1 enhancements
        if risk_profile == 'conservative':
            self.base_position_sizing = {
                -5: (0.0, 0.0), -4: (0.0, 0.0), -3: (0.0, 0.0), -2: (0.0, 0.0), -1: (0.0, 0.0),
                 0: (0.0, 0.0),
                 1: (0.4, 1.0), 2: (0.6, 1.0), 3: (0.9, 1.0), 4: (1.1, 1.0), 5: (1.4, 1.0),
            }
        elif risk_profile == 'aggressive':
            self.base_position_sizing = {
                -5: (0.0, 0.0), -4: (0.0, 0.0), -3: (0.0, 0.0), -2: (0.0, 0.0), -1: (0.0, 0.0),
                 0: (0.0, 0.0),
                 1: (0.9, 1.0), 2: (1.3, 1.0), 3: (1.9, 1.0), 4: (2.4, 1.0), 5: (2.9, 1.0),
            }
        else:  # moderate
            self.base_position_sizing = {
                -5: (0.0, 0.0), -4: (0.0, 0.0), -3: (0.0, 0.0), -2: (0.0, 0.0), -1: (0.0, 0.0),
                 0: (0.0, 0.0),
                 1: (0.6, 1.0), 2: (0.9, 1.0), 3: (1.3, 1.0), 4: (1.7, 1.0), 5: (2.1, 1.0),
            }
        
        print(f"🚀 XRPUSDT 1H ENHANCED STRATEGY WITH COMPLETE PHASE 3 OPTIMIZATION ({risk_profile.upper()})")
        print(f"💼 Account Size: ${account_size:,}")
        print(f"🎯 Target: {self.profit_target_pct}% in {self.target_timeframe_days} days")
        print(f"🪙 XRP Features: Optimized parameters, enhanced opportunity capture")
        print(f"⚠️ Risk Limits: Daily {self.daily_loss_cutoff_pct}% | Emergency {self.daily_loss_emergency_pct}%")
        print(f"🔍 XRP Regime Filter: ADX {self.adx_strong_threshold}/{self.adx_moderate_threshold}, Vol {self.volume_threshold_multiplier:.2f}x")
        print(f"🧠 Market Intelligence: BTC Dominance tracking, correlation analysis")
        print(f"🔄 Dynamic Adaptation: Mode switching, drawdown recovery, alt season detection")
        print(f"✨ Optimization: Complete Phase 3 - All enhancements integrated")
    
    def get_market_intelligence_multiplier(self, df, current_idx):
        """Get market intelligence multiplier for position sizing"""
        try:
            # Cache key for efficiency
            current_date = df.index[current_idx]
            cache_key = current_date.strftime('%Y-%m-%d')
            
            if cache_key in self.market_analysis_cache:
                return self.market_analysis_cache[cache_key]
            
            # Get XRP and BTC price data for correlation analysis
            xrp_prices = df['Close'].iloc[max(0, current_idx-20):current_idx+1]
            
            # Try to get BTC data (simplified approach)
            try:
                import yfinance as yf
                end_date = current_date
                start_date = end_date - pd.Timedelta(days=25)
                btc_data = yf.download('BTC-USD', start=start_date, end=end_date, interval='1d', progress=False)
                
                if not btc_data.empty:
                    btc_prices = btc_data['Close']
                    # Align with XRP dates
                    btc_aligned = btc_prices.reindex(xrp_prices.index, method='ffill')
                else:
                    btc_aligned = None
            except:
                btc_aligned = None
            
            # Get comprehensive market analysis
            analysis = self.market_intelligence.get_comprehensive_multiplier(
                ada_prices=xrp_prices,  # Reuse ADA logic for XRP
                btc_prices=btc_aligned,
                current_date=current_date
            )
            
            # Cache the result
            self.market_analysis_cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            # Fallback to neutral conditions
            return {
                'combined_multiplier': 1.0,
                'regime': 'neutral',
                'recommendation': '⚖️ NEUTRAL: Market intelligence unavailable'
            }

    def update_dynamic_mode(self, df, current_idx):
        """Update dynamic trading mode based on current conditions"""
        try:
            # Get market intelligence
            market_analysis = self.get_market_intelligence_multiplier(df, current_idx)
            
            # Prepare price data for cycle analysis
            price_data = df['Close'].iloc[max(0, current_idx-30):current_idx+1]
            
            # Calculate daily P&L (simplified)
            daily_pnl = 0
            if hasattr(self, 'trades') and self.trades:
                today_trades = [t for t in self.trades if t.get('timestamp', '').startswith(str(df.index[current_idx].date()))]
                daily_pnl = sum([t.get('pnl', 0) for t in today_trades])
            
            # Update mode
            mode_changed = self.dynamic_adapter.update_trading_mode(
                market_intelligence={
                    'btc_dominance': market_analysis.get('btc_dominance', 45.0),
                    'regime': market_analysis.get('regime', 'neutral')
                },
                price_data=price_data,
                current_balance=self.current_balance,
                initial_balance=self.initial_balance,
                daily_pnl=daily_pnl,
                trades_today=len(today_trades) if 'today_trades' in locals() else 0
            )
            
            if mode_changed:
                self.mode_updates_today += 1
                
            return self.dynamic_adapter.get_current_parameters()
            
        except Exception as e:
            # Fallback to standard parameters
            return {
                'position_multiplier': 1.0,
                'risk_multiplier': 1.0,
                'signal_threshold': 2,
                'max_trades_per_day': 5
            }

    def calculate_safe_position_size_1h(self, composite_score, current_price, atr, current_hour, df=None, current_idx=None):
        """Calculate safe position size for 1H XRP trading with enhanced risk management"""
        position_size, stop_distance, risk_pct, position_value = super().calculate_safe_position_size_1h(
            composite_score, current_price, atr, current_hour
        )
        
        # Apply additional XRP risk scaling
        if position_size > 0:
            # XRP-specific volatility adjustment - optimized for Phase 3
            xrp_volatility_multiplier = 1.15  # Slightly more aggressive than ADA
            
            # Apply market intelligence multiplier if available
            market_multiplier = 1.0
            dynamic_multiplier = 1.0
            
            if df is not None and current_idx is not None:
                try:
                    # Get market intelligence multiplier
                    market_analysis = self.get_market_intelligence_multiplier(df, current_idx)
                    market_multiplier = market_analysis['combined_multiplier']
                    
                    # Get dynamic strategy adaptation multiplier
                    dynamic_params = self.update_dynamic_mode(df, current_idx)
                    dynamic_multiplier = dynamic_params['position_multiplier']
                    
                    # Log conditions for transparency
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"  Market Intelligence: {market_analysis['recommendation']}")
                        print(f"  Dynamic Mode: {self.dynamic_adapter.current_mode.value} | Multiplier: {dynamic_multiplier:.2f}x")
                        print(f"  Combined: Market {market_multiplier:.2f}x × Dynamic {dynamic_multiplier:.2f}x")
                        
                except:
                    market_multiplier = 1.0  # Fallback
                    dynamic_multiplier = 1.0
            
            # Combine all multipliers
            total_multiplier = xrp_volatility_multiplier * market_multiplier * dynamic_multiplier
            position_size *= total_multiplier
            risk_pct *= total_multiplier
            
            # Recalculate position value
            position_value = position_size * current_price
        
        return position_size, stop_distance, risk_pct, position_value
    
    def calculate_1h_crypto_trend_composite(self, df):
        """
        Calculate 1H XRP trend composite score with enhanced filtering
        Adapted for XRP's unique volatility patterns
        """
        if len(df) < 100:
            return pd.Series(0, index=df.index)
        
        # Use the parent class method but with XRP-specific adjustments
        composite_score = super().calculate_1h_crypto_trend_composite(df)
        
        # Dynamic signal threshold based on current trading mode
        try:
            # Get current dynamic parameters
            dynamic_params = self.dynamic_adapter.get_current_parameters()
            signal_threshold = dynamic_params.get('signal_threshold', 2)
        except:
            signal_threshold = 2  # Fallback
        
        # Apply dynamic signal filtering
        xrp_filter = abs(composite_score) >= signal_threshold
        composite_score = composite_score * xrp_filter.astype(int)
        
        return composite_score
    
    def check_market_regime(self, df, current_idx):
        """
        Enhanced market regime check for XRP
        Stricter requirements due to XRP volatility
        """
        can_trade, multiplier, reason = super().check_market_regime(df, current_idx)
        
        if can_trade:
            # Additional XRP checks
            current_close = df.iloc[current_idx]['Close']
            current_volume = df.iloc[current_idx].get('Volume', 1)
            
            # Check for extreme price movements (XRP-specific)
            if current_idx > 5:
                price_change_5h = (current_close / df.iloc[current_idx-5]['Close'] - 1) * 100
                
                # Skip trading during extreme XRP movements - relaxed threshold for Phase 3
                if abs(price_change_5h) > 25:  # Higher threshold for XRP volatility
                    return False, 0, f"Extreme XRP movement: {price_change_5h:+.1f}%"
            
            # Volume spike check for XRP (pump/dump protection)
            if 'Volume' in df.columns and current_idx > 24:
                volume_24h_avg = df['Volume'].iloc[current_idx-24:current_idx].mean()
                volume_spike_ratio = current_volume / volume_24h_avg if volume_24h_avg > 0 else 1
                
                # Skip if volume is >6x normal (XRP is prone to manipulation)
                if volume_spike_ratio > 6:
                    return False, 0, f"XRP volume spike: {volume_spike_ratio:.1f}x normal"
            
            # Apply optimized XRP multiplier
            xrp_multiplier = 1.05  # Slightly favorable multiplier for XRP
            multiplier *= xrp_multiplier
            reason += " (XRP optimized)"
        
        return can_trade, multiplier, reason
    
    def print_dynamic_strategy_summary(self):
        """Print summary of dynamic strategy adaptations"""
        try:
            summary = self.dynamic_adapter.get_mode_summary()
            print(f"\n🔄 DYNAMIC STRATEGY SUMMARY:")
            print(f"Current Mode: {summary['current_mode'].upper()}")
            print(f"Mode Changes Today: {summary['mode_changes_today']}")
            print(f"Total Mode Changes: {summary['total_mode_changes']}")
            
            params = summary['current_parameters']
            print(f"Position Multiplier: {params['position_multiplier']:.2f}x")
            print(f"Risk Multiplier: {params['risk_multiplier']:.2f}x")
            print(f"Signal Threshold: ≥{params['signal_threshold']}")
            print(f"Max Daily Trades: {params['max_trades_per_day']}")
            print(f"Seasonal Adjustment: {params.get('seasonal_multiplier', 1.0):.2f}x")
        except Exception as e:
            print(f"\n🔄 DYNAMIC STRATEGY: Standard mode (adapter error)")
    
    def execute_trade_entry(self, df, i, current_score, current_price, current_atr, current_hour):
        """Override trade entry to pass market intelligence parameters"""
        # Check if we can trade and get regime information
        can_trade, regime_multiplier, regime_reason = self.check_market_regime(df, i)
        
        if can_trade:
            # Call our enhanced position sizing with market intelligence
            position_size, stop_distance, risk_pct, position_value = self.calculate_safe_position_size_1h(
                current_score, current_price, current_atr, current_hour, df, i
            )
            
            # Apply regime multiplier from parent class
            position_size *= regime_multiplier
            risk_pct *= regime_multiplier
            position_value = position_size * current_price
            
            return position_size, stop_distance, risk_pct, position_value, regime_reason
        else:
            return 0, 0, 0, 0, regime_reason

def test_xrpusdt_strategy():
    """Test XRPUSDT strategy across different periods"""
    print("🚀 TESTING XRPUSDT 1H ENHANCED STRATEGY WITH COMPLETE PHASE 3 OPTIMIZATION")
    print("=" * 80)
    
    # Test periods - focus on key crypto market periods
    test_periods = [
        ("Feb 2024", "2024-02-01", "2024-02-29", "Crypto bull run"),
        ("May 2024", "2024-05-01", "2024-05-31", "Market correction"),
        ("Jun 2024", "2024-06-01", "2024-06-30", "Altcoin weakness"),
        ("Nov 2024", "2024-11-01", "2024-11-30", "Altcoin season"),
    ]
    
    results = []
    
    for period_name, start_date, end_date, description in test_periods:
        print(f"\n📅 Testing {period_name} - {description}")
        print("-" * 50)
        
        # Test aggressive profile for XRP
        xrp_strategy = XRPUSDT1HEnhancedStrategy(10000, 'aggressive')
        df = xrp_strategy.run_1h_crypto_backtest(start_date, end_date, "XRP-USD")
        
        if df is not None:
            xrp_strategy.print_crypto_results()
            xrp_strategy.print_dynamic_strategy_summary()
            
            profit_pct = (xrp_strategy.current_balance - xrp_strategy.initial_balance) / xrp_strategy.initial_balance * 100
            closed_trades = len([t for t in xrp_strategy.trades if t['action'] == 'CLOSE'])
            
            results.append({
                'period': period_name,
                'profit_pct': profit_pct,
                'trades': closed_trades,
                'description': description
            })
        else:
            print(f"❌ Failed to test {period_name}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 XRPUSDT PHASE 3 STRATEGY SUMMARY")
    print("=" * 80)
    
    if results:
        print(f"{'Period':<12} {'Profit':<10} {'Trades':<8} {'Description'}")
        print("-" * 50)
        
        total_profit = 0
        total_trades = 0
        
        for result in results:
            print(f"{result['period']:<12} {result['profit_pct']:+7.2f}% {result['trades']:<8} {result['description']}")
            total_profit += result['profit_pct']
            total_trades += result['trades']
        
        print("-" * 50)
        print(f"{'AVERAGE':<12} {total_profit/len(results):+7.2f}% {total_trades//len(results):<8}")
        
        print("\n💡 XRP Phase 3 Strategy Features:")
        print("• Complete Phase 3 optimization (Dynamic + Intelligence + Optimized)")
        print("• XRP-specific volatility and volume protections")
        print("• Enhanced position sizing for XRP characteristics")
        print("• Intelligent mode switching and market adaptation")
        print("• BTC correlation analysis and dominance tracking")

if __name__ == "__main__":
    test_xrpusdt_strategy()