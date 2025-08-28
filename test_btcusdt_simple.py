"""
Simplified BTCUSDT Enhanced Strategy Test

Direct test of the BTCUSDT Enhanced Strategy adapted for the framework.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def create_synthetic_btc_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Create realistic synthetic BTC data for testing"""
    dates = pd.date_range(start_date, end_date, freq='H')
    n_points = len(dates)
    
    print(f"📊 Creating synthetic BTC data: {n_points:,} hourly points")
    
    # Realistic BTC parameters
    np.random.seed(42)  # For reproducibility
    base_price = 30000  # Starting price
    
    # Create realistic price movement with trends and volatility
    trends = []
    current_price = base_price
    
    for i in range(n_points):
        # Add weekly cycles and monthly trends
        week_cycle = np.sin(2 * np.pi * i / (24 * 7)) * 0.02
        month_cycle = np.sin(2 * np.pi * i / (24 * 30)) * 0.03
        
        # Random volatility with crypto-like characteristics
        volatility = 0.025 + 0.01 * np.sin(2 * np.pi * i / (24 * 30))
        random_change = np.random.normal(0.0003, volatility)  # Slight upward bias
        
        # Combine all factors
        total_change = random_change + week_cycle * 0.5 + month_cycle * 0.3
        current_price *= (1 + total_change)
        trends.append(current_price)
    
    prices = np.array(trends)
    
    # Create OHLCV data
    data = pd.DataFrame(index=dates)
    data['Close'] = prices
    
    # Generate realistic OHLC from close prices
    data['Open'] = data['Close'].shift(1).fillna(data['Close'].iloc[0])
    
    # Generate High/Low with realistic spread
    hourly_volatility = np.random.uniform(0.005, 0.025, n_points)
    data['High'] = data['Close'] * (1 + hourly_volatility / 2)
    data['Low'] = data['Close'] * (1 - hourly_volatility / 2)
    
    # Ensure OHLC consistency
    data['High'] = np.maximum(data['High'], np.maximum(data['Open'], data['Close']))
    data['Low'] = np.minimum(data['Low'], np.minimum(data['Open'], data['Close']))
    
    # Generate volume (crypto-like patterns)
    base_volume = 1000000
    volume_multiplier = 1 + np.random.exponential(0.5, n_points)
    data['Volume'] = base_volume * volume_multiplier
    
    print(f"✅ Generated data from ${prices[0]:,.0f} to ${prices[-1]:,.0f}")
    print(f"   Data points: {len(data):,}")
    print(f"   Price range: ${prices.min():,.0f} - ${prices.max():,.0f}")
    
    return data


def calculate_enhanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the enhanced technical indicators"""
    print("🔧 Calculating enhanced technical indicators...")
    
    if len(df) < 200:
        print("❌ Insufficient data for indicators")
        return df
    
    # EMAs
    ema_periods = [8, 21, 50, 100, 200]
    for period in ema_periods:
        df[f'ema_{period}'] = df['Close'].ewm(span=period).mean()
    
    # RSI
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    df['rsi_14'] = calculate_rsi(df['Close'], 14)
    df['rsi_21'] = calculate_rsi(df['Close'], 21)
    
    # MACD
    ema_12 = df['Close'].ewm(span=12).mean()
    ema_26 = df['Close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # Volume indicators
    df['volume_sma'] = df['Volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma']
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift(1))
    low_close = abs(df['Low'] - df['Close'].shift(1))
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()
    df['volatility_ratio'] = df['atr'] / df['atr'].rolling(window=24).mean()
    
    # Simple ADX approximation
    df['adx'] = abs(df['ema_8'] - df['ema_21']) / df['Close'] * 100
    df['adx'] = df['adx'].rolling(window=14).mean()
    
    # Bollinger Bands
    df['bb_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    print("✅ Technical indicators calculated")
    return df.fillna(method='bfill').fillna(0)


def calculate_confluence_score(data, idx):
    """Calculate confluence score for the enhanced strategy"""
    if idx < 200:
        return 0, {}
    
    row = data.iloc[idx]
    score = 0
    details = {}
    
    # 1. Trend Alignment (0-2 points)
    close = row['Close']
    ema8, ema21, ema50, ema100 = row['ema_8'], row['ema_21'], row['ema_50'], row['ema_100']
    
    trend_score = 0
    if close > ema8 > ema21 > ema50 > ema100:
        trend_score = 2
        details['trend'] = 'Strong Bullish'
    elif close > ema8 > ema21 > ema50:
        trend_score = 1
        details['trend'] = 'Moderate Bullish'
    elif close < ema8 < ema21 < ema50:
        trend_score = -1
        details['trend'] = 'Moderate Bearish'
    else:
        trend_score = 0
        details['trend'] = 'Mixed'
    
    score += abs(trend_score)
    
    # 2. Momentum (0-2 points)
    rsi14, rsi21 = row['rsi_14'], row['rsi_21']
    macd, macd_signal = row['macd'], row['macd_signal']
    
    momentum_score = 0
    rsi_bullish = 30 < rsi14 < 75 and rsi14 > rsi21
    macd_bullish = macd > macd_signal
    
    if rsi_bullish and macd_bullish and trend_score > 0:
        momentum_score = 2
    elif (rsi_bullish or macd_bullish) and trend_score > 0:
        momentum_score = 1
    
    score += momentum_score
    details['momentum'] = 'Strong' if momentum_score == 2 else ('Moderate' if momentum_score == 1 else 'Weak')
    
    # 3. Market Regime (0-1 points)
    adx = row['adx']
    regime_score = 1 if adx > 20 else 0
    score += regime_score
    details['adx'] = adx
    
    # 4. Volume/Volatility (0-1 points)
    volume_ratio = row['volume_ratio']
    vol_score = 1 if volume_ratio > 1.0 else 0
    score += vol_score
    details['volume'] = volume_ratio
    
    # 5. Bollinger Band position (0-1 points)
    bb_pos = row['bb_position']
    bb_score = 1 if (trend_score > 0 and bb_pos < 0.3) or (0.2 < bb_pos < 0.8) else 0
    score += bb_score
    
    final_score = min(7, score)
    details['final_score'] = final_score
    details['signal_direction'] = 'LONG' if trend_score + momentum_score > 0 else 'NONE'
    
    return final_score, details


def run_enhanced_strategy_backtest(data: pd.DataFrame, risk_profile: str = 'moderate'):
    """Run the enhanced strategy backtest"""
    
    print(f"\n🚀 Running Enhanced Strategy Backtest - {risk_profile.upper()}")
    print("-" * 60)
    
    # Risk parameters
    risk_configs = {
        'conservative': {'risk_per_trade': 0.01, 'min_confluence': 5, 'max_daily_loss': 0.03},
        'moderate': {'risk_per_trade': 0.02, 'min_confluence': 4, 'max_daily_loss': 0.05},
        'aggressive': {'risk_per_trade': 0.03, 'min_confluence': 3, 'max_daily_loss': 0.07}
    }
    
    config = risk_configs[risk_profile]
    
    # Initial capital
    initial_capital = 100000
    current_balance = initial_capital
    position = 0
    entry_price = 0
    trades = []
    equity_curve = []
    monthly_summaries = []
    
    # Track monthly data
    current_month = None
    month_start_balance = initial_capital
    month_trades = 0
    
    print(f"💰 Initial Capital: ${initial_capital:,}")
    print(f"🎯 Risk per trade: {config['risk_per_trade']:.1%}")
    print(f"📊 Min confluence: {config['min_confluence']}")
    
    # Process each bar
    for i in range(200, len(data)):
        current_time = data.index[i]
        current_data = data.iloc[i]
        current_price = current_data['Close']
        
        # Monthly tracking
        current_month_str = current_time.strftime('%Y-%m')
        if current_month != current_month_str:
            if current_month is not None:
                # Save previous month summary
                month_pnl = current_balance - month_start_balance
                monthly_summaries.append({
                    'month': current_month,
                    'starting_balance': month_start_balance,
                    'ending_balance': current_balance,
                    'pnl': month_pnl,
                    'pnl_pct': (month_pnl / month_start_balance) * 100,
                    'trades': month_trades
                })
            
            current_month = current_month_str
            month_start_balance = current_balance
            month_trades = 0
        
        # Process existing position
        if position != 0:
            # Simple stop loss (5% for long positions)
            stop_price = entry_price * 0.95 if position > 0 else entry_price * 1.05
            
            # Simple take profit (15% for long positions)
            target_price = entry_price * 1.15 if position > 0 else entry_price * 0.85
            
            should_exit = False
            exit_reason = ""
            
            if position > 0:  # Long position
                if current_price <= stop_price:
                    should_exit = True
                    exit_reason = "Stop Loss"
                elif current_price >= target_price:
                    should_exit = True
                    exit_reason = "Take Profit"
            
            if should_exit:
                # Close position
                pnl = (current_price - entry_price) * abs(position)
                current_balance += pnl
                
                trade_record = {
                    'timestamp': current_time,
                    'action': 'CLOSE',
                    'price': current_price,
                    'pnl': pnl,
                    'pnl_pct': (pnl / initial_capital) * 100,
                    'balance': current_balance,
                    'reason': exit_reason
                }
                
                trades.append(trade_record)
                month_trades += 1
                position = 0
                entry_price = 0
        
        # Look for new entries
        elif position == 0:
            confluence_score, confluence_details = calculate_confluence_score(data, i)
            
            if confluence_score >= config['min_confluence']:
                signal_direction = confluence_details.get('signal_direction', 'NONE')
                
                if signal_direction == 'LONG':
                    # Calculate position size
                    risk_amount = current_balance * config['risk_per_trade']
                    atr = current_data['atr']
                    stop_distance = atr * 2.0  # 2 ATR stop
                    
                    if stop_distance > 0:
                        position_size = risk_amount / stop_distance
                        
                        # Enter position
                        position = position_size
                        entry_price = current_price
                        
                        trade_record = {
                            'timestamp': current_time,
                            'action': 'OPEN',
                            'price': current_price,
                            'size': position_size,
                            'confluence_score': confluence_score,
                            'confluence_details': confluence_details
                        }
                        
                        trades.append(trade_record)
        
        # Record equity curve
        unrealized_pnl = 0
        if position != 0:
            unrealized_pnl = (current_price - entry_price) * abs(position)
        
        equity_curve.append({
            'timestamp': current_time,
            'balance': current_balance + unrealized_pnl,
            'position': position,
            'price': current_price
        })
    
    # Close final month
    if current_month is not None:
        month_pnl = current_balance - month_start_balance
        monthly_summaries.append({
            'month': current_month,
            'starting_balance': month_start_balance,
            'ending_balance': current_balance,
            'pnl': month_pnl,
            'pnl_pct': (month_pnl / month_start_balance) * 100,
            'trades': month_trades
        })
    
    # Calculate performance metrics
    total_return = (current_balance - initial_capital) / initial_capital * 100
    closed_trades = [t for t in trades if t['action'] == 'CLOSE']
    
    win_trades = [t for t in closed_trades if t['pnl'] > 0]
    win_rate = (len(win_trades) / len(closed_trades)) * 100 if closed_trades else 0
    
    # Calculate max drawdown
    equity_values = [e['balance'] for e in equity_curve]
    if equity_values:
        equity_series = pd.Series(equity_values)
        rolling_max = equity_series.expanding().max()
        drawdown = ((equity_series / rolling_max) - 1) * 100
        max_drawdown = drawdown.min()
    else:
        max_drawdown = 0
    
    results = {
        'initial_capital': initial_capital,
        'final_balance': current_balance,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'total_trades': len(closed_trades),
        'win_rate': win_rate,
        'trades': trades,
        'equity_curve': equity_curve,
        'monthly_summaries': monthly_summaries,
        'risk_profile': risk_profile
    }
    
    return results


def print_results(results: dict):
    """Print comprehensive backtest results"""
    
    print(f"\n🏆 BTCUSDT ENHANCED STRATEGY RESULTS - {results['risk_profile'].upper()}")
    print("=" * 70)
    
    print(f"💰 Financial Performance:")
    print(f"   Initial Capital:     ${results['initial_capital']:,}")
    print(f"   Final Balance:       ${results['final_balance']:,.2f}")
    print(f"   Total Return:        {results['total_return']:+.2f}%")
    print(f"   Max Drawdown:        {results['max_drawdown']:.2f}%")
    
    print(f"\n📊 Trading Performance:")
    print(f"   Total Trades:        {results['total_trades']}")
    print(f"   Win Rate:            {results['win_rate']:.1f}%")
    
    if results['monthly_summaries']:
        profitable_months = len([m for m in results['monthly_summaries'] if m['pnl'] > 0])
        total_months = len(results['monthly_summaries'])
        print(f"   Profitable Months:   {profitable_months}/{total_months} ({profitable_months/total_months*100:.1f}%)")


def print_monthly_summary(results: dict):
    """Print detailed monthly summary"""
    
    print(f"\n📅 MONTHLY PERFORMANCE SUMMARY - {results['risk_profile'].upper()}")
    print("=" * 70)
    
    monthly_summaries = results['monthly_summaries']
    
    if not monthly_summaries:
        print("❌ No monthly data available")
        return
    
    print(f"{'Month':<10} {'Start Balance':<15} {'End Balance':<15} {'P&L':<12} {'P&L %':<8} {'Trades':<8}")
    print("-" * 70)
    
    for month_data in monthly_summaries:
        month = month_data['month']
        start_bal = month_data['starting_balance']
        end_bal = month_data['ending_balance']
        pnl = month_data['pnl']
        pnl_pct = month_data['pnl_pct']
        trades = month_data['trades']
        
        # Format with emoji
        emoji = "📈" if pnl > 0 else "📉"
        
        print(f"{month:<10} ${start_bal:<14,.0f} ${end_bal:<14,.0f} ${pnl:<+11,.0f} {pnl_pct:<+7.2f}% {trades:<3} {emoji}")


def main():
    """Main test function"""
    
    print("🎯 BTCUSDT Enhanced Strategy - 24 Month Test")
    print("📊 Testing adapted multi-confluence strategy")
    print("=" * 60)
    
    # Create test data
    start_date = '2023-08-01'
    end_date = '2025-07-31'
    
    print(f"📅 Period: {start_date} to {end_date} (24 months)")
    
    # Generate synthetic data
    data = create_synthetic_btc_data(start_date, end_date)
    
    # Calculate indicators
    data = calculate_enhanced_indicators(data)
    
    # Test all risk profiles
    risk_profiles = ['conservative', 'moderate', 'aggressive']
    all_results = {}
    
    for risk_profile in risk_profiles:
        print(f"\n" + "="*60)
        results = run_enhanced_strategy_backtest(data, risk_profile)
        all_results[risk_profile] = results
        
        print_results(results)
        print_monthly_summary(results)
    
    # Summary comparison
    print(f"\n🏆 PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"{'Profile':<12} {'Return':<10} {'Drawdown':<10} {'Win Rate':<10} {'Trades':<8}")
    print("-" * 50)
    
    for profile, results in all_results.items():
        print(f"{profile.title():<12} {results['total_return']:+8.2f}% {results['max_drawdown']:8.2f}% {results['win_rate']:8.1f}% {results['total_trades']:8}")
    
    print(f"\n✅ 24-MONTH BACKTEST COMPLETED!")
    print("📊 Enhanced BTCUSDT multi-confluence strategy tested successfully")


if __name__ == "__main__":
    main()