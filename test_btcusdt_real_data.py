"""
BTCUSDT Enhanced Strategy - REAL DATA Test

Test with actual BTC-USD historical data from Yahoo Finance
Period: August 2023 to July 2025 (or latest available)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def fetch_real_btc_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch real BTC-USD data from Yahoo Finance"""
    print(f"📊 Fetching REAL BTC-USD data from Yahoo Finance...")
    print(f"   Period: {start_date} to {end_date}")
    
    try:
        # Download BTC-USD data
        ticker = yf.Ticker("BTC-USD")
        
        # Try hourly data first
        data = ticker.history(start=start_date, end=end_date, interval='1h')
        
        if data.empty or len(data) < 100:
            print("⚠️ Hourly data not available, fetching daily data...")
            data = ticker.history(start=start_date, end=end_date, interval='1d')
            
        if data.empty:
            raise ValueError("No data retrieved from Yahoo Finance")
        
        # Clean column names
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Remove timezone if present
        if hasattr(data.index, 'tz'):
            data.index = data.index.tz_localize(None)
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"   Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"   Price range: ${data['Close'].min():,.0f} - ${data['Close'].max():,.0f}")
        print(f"   Current price: ${data['Close'].iloc[-1]:,.0f}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        return None


def calculate_enhanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the enhanced technical indicators"""
    print("🔧 Calculating enhanced technical indicators...")
    
    if len(df) < 200:
        print(f"⚠️ Limited data ({len(df)} points), adjusting indicators...")
        
    # EMAs
    ema_periods = [8, 21, 50, 100, 200]
    for period in ema_periods:
        if len(df) >= period:
            df[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        else:
            df[f'ema_{period}'] = df['Close'].rolling(min(period, len(df)//2)).mean()
    
    # RSI
    def calculate_rsi(prices, period=14):
        if len(prices) < period + 1:
            return pd.Series(50, index=prices.index)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    df['rsi_14'] = calculate_rsi(df['Close'], 14)
    df['rsi_21'] = calculate_rsi(df['Close'], 21)
    
    # MACD
    if len(df) >= 26:
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
    else:
        df['macd'] = 0
        df['macd_signal'] = 0
        df['macd_histogram'] = 0
    
    # Volume indicators
    df['volume_sma'] = df['Volume'].rolling(window=min(20, len(df)//2)).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma'].replace(0, 1)
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift(1))
    low_close = abs(df['Low'] - df['Close'].shift(1))
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=min(14, len(df)//2)).mean()
    
    # Volatility ratio
    df['volatility_ratio'] = df['atr'] / df['atr'].rolling(window=min(24, len(df)//2)).mean()
    
    # Simple ADX approximation
    if len(df) >= 21:
        df['adx'] = abs(df['ema_8'] - df['ema_21']) / df['Close'] * 100
        df['adx'] = df['adx'].rolling(window=14).mean()
    else:
        df['adx'] = 20  # Default neutral value
    
    # Bollinger Bands
    period = min(20, len(df)//2)
    df['bb_middle'] = df['Close'].rolling(window=period).mean()
    bb_std = df['Close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower']).replace(0, 0.5)
    
    # Fill NaN values
    df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
    
    print(f"✅ Technical indicators calculated ({len(df)} data points)")
    return df


def calculate_confluence_score(data, idx):
    """Calculate confluence score for the enhanced strategy"""
    if idx < min(50, len(data)//4):  # Adjust for available data
        return 0, {}
    
    row = data.iloc[idx]
    score = 0
    details = {}
    
    # 1. Trend Alignment (0-2 points)
    close = row['Close']
    ema8 = row.get('ema_8', close)
    ema21 = row.get('ema_21', close)
    ema50 = row.get('ema_50', close)
    ema100 = row.get('ema_100', close)
    
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
    rsi14 = row.get('rsi_14', 50)
    rsi21 = row.get('rsi_21', 50)
    macd = row.get('macd', 0)
    macd_signal = row.get('macd_signal', 0)
    
    momentum_score = 0
    rsi_bullish = 30 < rsi14 < 70 and rsi14 > rsi21
    macd_bullish = macd > macd_signal and macd > 0
    
    if rsi_bullish and macd_bullish and trend_score > 0:
        momentum_score = 2
    elif (rsi_bullish or macd_bullish) and trend_score > 0:
        momentum_score = 1
    
    score += momentum_score
    details['momentum'] = 'Strong' if momentum_score == 2 else ('Moderate' if momentum_score == 1 else 'Weak')
    
    # 3. Market Regime (0-1 points)
    adx = row.get('adx', 20)
    regime_score = 1 if adx > 20 else 0
    score += regime_score
    details['adx'] = adx
    
    # 4. Volume/Volatility (0-1 points)
    volume_ratio = row.get('volume_ratio', 1.0)
    vol_score = 1 if volume_ratio > 1.0 else 0.5 if volume_ratio > 0.8 else 0
    score += vol_score
    details['volume'] = volume_ratio
    
    # 5. Bollinger Band position (0-1 points)
    bb_pos = row.get('bb_position', 0.5)
    bb_score = 1 if (trend_score > 0 and bb_pos < 0.3) or (0.2 < bb_pos < 0.8) else 0
    score += bb_score
    
    final_score = min(7, int(score))
    details['final_score'] = final_score
    details['signal_direction'] = 'LONG' if trend_score > 0 and momentum_score > 0 else 'NONE'
    
    return final_score, details


def run_enhanced_strategy_backtest(data: pd.DataFrame, risk_profile: str = 'moderate'):
    """Run the enhanced strategy backtest with REAL data"""
    
    print(f"\n🚀 Running Enhanced Strategy Backtest - {risk_profile.upper()}")
    print("-" * 60)
    
    # Risk parameters with REALISTIC settings
    risk_configs = {
        'conservative': {
            'risk_per_trade': 0.005,  # 0.5% risk (more realistic)
            'min_confluence': 5,
            'max_daily_loss': 0.02,   # 2% daily loss limit
            'take_profit_mult': 2.0,  # 2:1 risk reward
            'stop_loss_atr': 2.0      # 2 ATR stop
        },
        'moderate': {
            'risk_per_trade': 0.01,   # 1% risk
            'min_confluence': 4,
            'max_daily_loss': 0.03,   # 3% daily loss limit
            'take_profit_mult': 2.5,  # 2.5:1 risk reward
            'stop_loss_atr': 2.0
        },
        'aggressive': {
            'risk_per_trade': 0.015,  # 1.5% risk
            'min_confluence': 3,
            'max_daily_loss': 0.05,   # 5% daily loss limit
            'take_profit_mult': 3.0,  # 3:1 risk reward
            'stop_loss_atr': 1.5
        }
    }
    
    config = risk_configs[risk_profile]
    
    # REALISTIC transaction costs
    commission = 0.001  # 0.1% per side
    slippage = 0.0005   # 0.05% slippage
    
    # Initial capital
    initial_capital = 100000
    current_balance = initial_capital
    position = 0
    entry_price = 0
    stop_price = 0
    target_price = 0
    trades = []
    equity_curve = []
    monthly_summaries = []
    
    # Daily loss tracking
    daily_pnl = 0
    current_day = None
    
    # Track monthly data
    current_month = None
    month_start_balance = initial_capital
    month_trades = 0
    
    print(f"💰 Initial Capital: ${initial_capital:,}")
    print(f"🎯 Risk per trade: {config['risk_per_trade']:.1%}")
    print(f"📊 Min confluence: {config['min_confluence']}")
    print(f"💸 Transaction costs: {(commission + slippage) * 2:.2%} round trip")
    
    # Determine starting point based on available data
    start_idx = min(50, len(data)//4)
    
    # Process each bar
    for i in range(start_idx, len(data)):
        current_time = data.index[i]
        current_data = data.iloc[i]
        current_price = current_data['Close']
        
        # Daily loss limit check
        if current_day != current_time.date():
            current_day = current_time.date()
            daily_pnl = 0
        
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
            # Check stop loss
            if position > 0 and current_price <= stop_price:
                # Exit with loss
                exit_price = current_price * (1 - slippage)  # Slippage on stop
                pnl = (exit_price - entry_price) * abs(position) - (commission * 2 * entry_price * abs(position))
                current_balance += pnl
                daily_pnl += pnl
                
                trades.append({
                    'timestamp': current_time,
                    'action': 'CLOSE',
                    'price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': (pnl / initial_capital) * 100,
                    'balance': current_balance,
                    'reason': 'Stop Loss'
                })
                
                month_trades += 1
                position = 0
                entry_price = 0
                
            # Check take profit
            elif position > 0 and current_price >= target_price:
                # Exit with profit
                exit_price = current_price * (1 - slippage)
                pnl = (exit_price - entry_price) * abs(position) - (commission * 2 * entry_price * abs(position))
                current_balance += pnl
                daily_pnl += pnl
                
                trades.append({
                    'timestamp': current_time,
                    'action': 'CLOSE',
                    'price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': (pnl / initial_capital) * 100,
                    'balance': current_balance,
                    'reason': 'Take Profit'
                })
                
                month_trades += 1
                position = 0
                entry_price = 0
        
        # Check daily loss limit
        if abs(daily_pnl) >= initial_capital * config['max_daily_loss']:
            continue  # Skip new entries for today
        
        # Look for new entries
        if position == 0:
            confluence_score, confluence_details = calculate_confluence_score(data, i)
            
            if confluence_score >= config['min_confluence']:
                signal_direction = confluence_details.get('signal_direction', 'NONE')
                
                if signal_direction == 'LONG':
                    # Calculate position size with Kelly-like adjustment
                    risk_amount = current_balance * config['risk_per_trade']
                    atr = current_data.get('atr', current_price * 0.02)  # Default 2% if no ATR
                    
                    if atr > 0:
                        stop_distance = atr * config['stop_loss_atr']
                        position_size = risk_amount / stop_distance
                        
                        # Apply position limits (max 10% of portfolio in one position)
                        max_position_value = current_balance * 0.1
                        if position_size * current_price > max_position_value:
                            position_size = max_position_value / current_price
                        
                        # Enter position with costs
                        entry_price = current_price * (1 + slippage)  # Slippage on entry
                        position = position_size
                        stop_price = entry_price - stop_distance
                        target_price = entry_price + (stop_distance * config['take_profit_mult'])
                        
                        # Deduct commission
                        current_balance -= commission * entry_price * position_size
                        
                        trades.append({
                            'timestamp': current_time,
                            'action': 'OPEN',
                            'price': entry_price,
                            'size': position_size,
                            'stop': stop_price,
                            'target': target_price,
                            'confluence_score': confluence_score,
                            'confluence_details': confluence_details
                        })
        
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
    
    # Calculate profit factor
    if closed_trades:
        gross_profit = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in closed_trades if t['pnl'] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    else:
        profit_factor = 0
    
    results = {
        'initial_capital': initial_capital,
        'final_balance': current_balance,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'total_trades': len(closed_trades),
        'win_rate': win_rate,
        'profit_factor': profit_factor,
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
    print(f"   Profit Factor:       {results['profit_factor']:.2f}")
    
    if results['monthly_summaries']:
        profitable_months = len([m for m in results['monthly_summaries'] if m['pnl'] > 0])
        total_months = len(results['monthly_summaries'])
        print(f"   Profitable Months:   {profitable_months}/{total_months} ({profitable_months/total_months*100:.1f}%)")


def print_monthly_summary(results: dict):
    """Print detailed monthly summary"""
    
    print(f"\n📅 MONTHLY PERFORMANCE SUMMARY - {results['risk_profile'].upper()} (REAL DATA)")
    print("=" * 80)
    
    monthly_summaries = results['monthly_summaries']
    
    if not monthly_summaries:
        print("❌ No monthly data available")
        return
    
    print(f"{'Month':<10} {'Start Balance':<15} {'End Balance':<15} {'P&L':<12} {'P&L %':<8} {'Trades':<8}")
    print("-" * 75)
    
    total_pnl = 0
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
        total_pnl += pnl
    
    print("-" * 75)
    print(f"TOTAL P&L: ${total_pnl:+,.0f}")


def main():
    """Main test function with REAL data"""
    
    print("🎯 BTCUSDT Enhanced Strategy - REAL DATA Test")
    print("📊 Testing with actual Bitcoin historical data from Yahoo Finance")
    print("=" * 70)
    
    # Date range for test
    start_date = '2023-08-01'
    end_date = '2025-07-31'  # Will get latest available if future date
    
    print(f"📅 Requested period: {start_date} to {end_date}")
    
    # Fetch REAL Bitcoin data
    data = fetch_real_btc_data(start_date, end_date)
    
    if data is None or data.empty:
        print("❌ Failed to fetch real data. Please check internet connection.")
        return
    
    # Calculate indicators
    data = calculate_enhanced_indicators(data)
    
    # Test all risk profiles
    risk_profiles = ['conservative', 'moderate', 'aggressive']
    all_results = {}
    
    for risk_profile in risk_profiles:
        print(f"\n" + "="*70)
        results = run_enhanced_strategy_backtest(data, risk_profile)
        all_results[risk_profile] = results
        
        print_results(results)
        print_monthly_summary(results)
    
    # Summary comparison
    print(f"\n🏆 REAL DATA PERFORMANCE COMPARISON")
    print("=" * 70)
    print(f"{'Profile':<12} {'Return':<12} {'Drawdown':<12} {'Win Rate':<10} {'PF':<8} {'Trades':<8}")
    print("-" * 65)
    
    for profile, results in all_results.items():
        return_str = f"{results['total_return']:+.2f}%"
        dd_str = f"{results['max_drawdown']:.2f}%"
        wr_str = f"{results['win_rate']:.1f}%"
        pf_str = f"{results['profit_factor']:.2f}"
        
        print(f"{profile.title():<12} {return_str:<12} {dd_str:<12} {wr_str:<10} {pf_str:<8} {results['total_trades']:<8}")
    
    print(f"\n✅ REAL DATA BACKTEST COMPLETED!")
    print("📊 These are ACTUAL results based on historical Bitcoin prices")
    print("💡 Note: Past performance does not guarantee future results")


if __name__ == "__main__":
    main()