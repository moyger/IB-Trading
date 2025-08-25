#!/usr/bin/env python3
"""
Individual Stock Portfolio Strategy using Trend Composite
- Position allocation per stock
- Stock selection criteria  
- Portfolio construction for $5K capital
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IndividualStockPortfolio:
    """
    Portfolio manager for trend composite on individual stocks
    """
    
    def __init__(self, total_capital=5000, max_positions=3):
        self.total_capital = total_capital
        self.max_positions = max_positions
        self.capital_per_position = total_capital / max_positions
        
        print(f"💰 INDIVIDUAL STOCK PORTFOLIO STRATEGY")
        print(f"📊 Total Capital: ${total_capital:,}")
        print(f"🎯 Max Positions: {max_positions}")
        print(f"💵 Capital per Position: ${self.capital_per_position:,.0f}")
        print()

    def define_stock_selection_criteria(self):
        """
        Define criteria for selecting individual stocks for trend composite
        """
        
        criteria = {
            "market_cap": "> $10B (large/mega cap for liquidity)",
            "avg_volume": "> 10M shares daily (high liquidity)",
            "volatility": "30-80% annual (enough movement for signals)", 
            "momentum_history": "Capable of 100%+ moves in bull markets",
            "sector_exposure": "Growth sectors: Tech, AI, EV, Biotech",
            "fundamental_strength": "Strong revenue growth, innovative products",
            "technical_requirements": "Clear trend patterns, responds to TA"
        }
        
        print("📋 STOCK SELECTION CRITERIA:")
        print("=" * 60)
        for criterion, description in criteria.items():
            print(f"✅ {criterion.replace('_', ' ').title()}: {description}")
        print()
        
        return criteria

    def get_candidate_stocks(self):
        """
        List of candidate stocks that meet our criteria
        """
        
        candidates = {
            # AI/Tech Leaders
            "NVDA": {"name": "NVIDIA", "sector": "AI/Semiconductors", "rationale": "AI leader, high volatility, strong trends"},
            "TSLA": {"name": "Tesla", "sector": "EV/Tech", "rationale": "Volatile, strong momentum history, clear trends"},
            "PLTR": {"name": "Palantir", "sector": "AI/Data", "rationale": "Proven trend composite performance, high volatility"},
            "AMD": {"name": "AMD", "sector": "Semiconductors", "rationale": "NVDA competitor, cyclical trends"},
            
            # Growth Tech
            "GOOGL": {"name": "Alphabet", "sector": "Tech/AI", "rationale": "AI player, large cap liquidity"},
            "META": {"name": "Meta", "sector": "Social/VR", "rationale": "High volatility, trend responsive"},
            "AMZN": {"name": "Amazon", "sector": "Cloud/Commerce", "rationale": "Large moves, institutional following"},
            
            # Biotech/Innovation  
            "MRNA": {"name": "Moderna", "sector": "Biotech", "rationale": "High volatility, news-driven trends"},
            "CRSP": {"name": "CRISPR", "sector": "Gene Editing", "rationale": "Emerging tech, volatile"},
            
            # Emerging Growth
            "COIN": {"name": "Coinbase", "sector": "Crypto", "rationale": "Crypto proxy, high volatility"},
            "RBLX": {"name": "Roblox", "sector": "Gaming/Metaverse", "rationale": "Growth story, volatile"}
        }
        
        print("🎯 CANDIDATE STOCK UNIVERSE:")
        print("=" * 80)
        for symbol, info in candidates.items():
            print(f"{symbol:6} | {info['name']:15} | {info['sector']:18} | {info['rationale']}")
        print()
        
        return candidates

    def analyze_stock_characteristics(self, symbols, period="2y"):
        """
        Analyze key characteristics of candidate stocks
        """
        
        print("📊 ANALYZING STOCK CHARACTERISTICS:")
        print("=" * 90)
        print(f"{'Symbol':6} {'Price':>8} {'Vol(%)':>7} {'AvgVol(M)':>10} {'Momentum':>9} {'Trend Score':>11}")
        print("-" * 90)
        
        stock_analysis = {}
        
        for symbol in symbols:
            try:
                # Download data
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                
                if df.empty:
                    continue
                
                # Calculate metrics
                current_price = df['Close'].iloc[-1]
                
                # Annualized volatility
                daily_returns = df['Close'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252) * 100
                
                # Average volume (millions)
                avg_volume = df['Volume'].mean() / 1_000_000
                
                # 6-month momentum (Nick Radge style)
                if len(df) >= 126:  # 6 months
                    momentum = (df['Close'].iloc[-1] / df['Close'].iloc[-126] - 1) * 100
                else:
                    momentum = 0
                
                # Simple trend score (price vs MA50, MA20)
                ma50 = df['Close'].rolling(50).mean().iloc[-1]
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                
                trend_signals = 0
                if current_price > ma50: trend_signals += 1
                if current_price > ma20: trend_signals += 1  
                if ma20 > ma50: trend_signals += 1
                trend_score = f"{trend_signals}/3"
                
                stock_analysis[symbol] = {
                    'price': current_price,
                    'volatility': volatility,
                    'avg_volume': avg_volume,
                    'momentum': momentum,
                    'trend_score': trend_signals,
                    'suitable': volatility >= 30 and avg_volume >= 5 and trend_signals >= 2
                }
                
                print(f"{symbol:6} ${current_price:7.2f} {volatility:6.1f}% {avg_volume:9.1f} {momentum:+8.1f}% {trend_score:>10}")
                
            except Exception as e:
                print(f"{symbol:6} ERROR: {e}")
                continue
        
        print()
        return stock_analysis

    def recommend_portfolio_allocation(self, stock_analysis, max_positions=3):
        """
        Recommend top stocks and allocation strategy
        """
        
        print("🏆 PORTFOLIO RECOMMENDATIONS:")
        print("=" * 60)
        
        # Filter suitable stocks
        suitable_stocks = {symbol: data for symbol, data in stock_analysis.items() if data.get('suitable', False)}
        
        if len(suitable_stocks) < max_positions:
            print(f"⚠️ Only {len(suitable_stocks)} stocks meet criteria (need {max_positions})")
            max_positions = len(suitable_stocks)
        
        # Rank by combination of momentum and trend strength
        ranked_stocks = sorted(suitable_stocks.items(), 
                             key=lambda x: (x[1]['trend_score'], x[1]['momentum']), 
                             reverse=True)
        
        print("📊 RANKING CRITERIA:")
        print("1. Current trend strength (3/3 signals preferred)")
        print("2. Recent momentum performance")
        print("3. Volatility level (30-80% optimal)")
        print("4. Liquidity (>5M average volume)")
        print()
        
        print("🥇 TOP SELECTIONS:")
        print("-" * 60)
        
        selected_stocks = []
        for i, (symbol, data) in enumerate(ranked_stocks[:max_positions]):
            rank = i + 1
            allocation_pct = 100 / max_positions
            capital_allocation = self.total_capital / max_positions
            
            print(f"#{rank}. {symbol}")
            print(f"    💰 Allocation: {allocation_pct:.0f}% (${capital_allocation:,.0f})")
            print(f"    📊 Price: ${data['price']:.2f} | Vol: {data['volatility']:.1f}% | Trend: {data['trend_score']}/3")
            print(f"    🚀 Momentum: {data['momentum']:+.1f}% | Volume: {data['avg_volume']:.1f}M")
            print()
            
            selected_stocks.append({
                'symbol': symbol,
                'allocation_pct': allocation_pct,
                'capital': capital_allocation,
                'price': data['price'],
                'shares': int(capital_allocation / data['price'])
            })
        
        return selected_stocks

    def position_allocation_levels(self):
        """
        Define position allocation levels for trend composite scores
        """
        
        print("📈 POSITION ALLOCATION BY TREND COMPOSITE SCORE:")
        print("=" * 60)
        
        # Optimized levels based on PLTR analysis
        allocation_levels = {
            -5: 0.00,  # Very bearish - full cash
            -4: 0.00,  # Bearish - full cash  
            -3: 0.00,  # Moderately bearish - full cash
            -2: 0.00,  # Mildly bearish - full cash
            -1: 0.00,  # Slightly bearish - full cash
             0: 0.20,  # Neutral - small position
             1: 0.40,  # Slightly bullish - moderate position
             2: 0.60,  # Mildly bullish - larger position
             3: 0.80,  # Moderately bullish - large position
             4: 1.00,  # Bullish - full position
             5: 1.00   # Very bullish - full position
        }
        
        print("Score | Allocation | Rationale")
        print("-" * 40)
        for score, allocation in allocation_levels.items():
            if score <= -1:
                rationale = "Cash - avoid bearish trends"
            elif score == 0:
                rationale = "Small position - neutral"
            elif score <= 2:
                rationale = f"Gradual increase - {int(allocation*100)}%"
            else:
                rationale = "Full position - strong trend"
                
            print(f"{score:+2d}    | {allocation:8.0%} | {rationale}")
        
        print()
        return allocation_levels

    def calculate_total_portfolio_exposure(self, num_stocks, avg_score):
        """
        Calculate total portfolio exposure based on individual stock allocations
        """
        
        allocation_levels = self.position_allocation_levels()
        per_stock_allocation = allocation_levels.get(avg_score, 0.5)
        
        # Each stock gets 1/3 of capital, then adjusted by trend composite score
        base_allocation_per_stock = 1.0 / num_stocks
        actual_allocation_per_stock = base_allocation_per_stock * per_stock_allocation
        total_portfolio_exposure = actual_allocation_per_stock * num_stocks
        
        print(f"💼 PORTFOLIO EXPOSURE CALCULATION:")
        print(f"   📊 Number of stocks: {num_stocks}")
        print(f"   🎯 Average trend score: {avg_score}")
        print(f"   📈 Per-stock base allocation: {base_allocation_per_stock:.1%}")
        print(f"   ⚡ Score-adjusted allocation: {actual_allocation_per_stock:.1%} per stock")
        print(f"   💰 Total portfolio exposure: {total_portfolio_exposure:.1%}")
        print()
        
        return total_portfolio_exposure

def run_portfolio_analysis():
    """
    Run complete portfolio analysis for individual stock trend composite
    """
    
    # Initialize portfolio manager
    portfolio = IndividualStockPortfolio(total_capital=5000, max_positions=3)
    
    # Define selection criteria
    criteria = portfolio.define_stock_selection_criteria()
    
    # Get candidate universe
    candidates = portfolio.get_candidate_stocks()
    candidate_symbols = list(candidates.keys())
    
    # Analyze characteristics
    analysis = portfolio.analyze_stock_characteristics(candidate_symbols)
    
    # Get recommendations
    selected = portfolio.recommend_portfolio_allocation(analysis, max_positions=3)
    
    # Show allocation strategy
    allocation_levels = portfolio.position_allocation_levels()
    
    # Example exposure calculation
    portfolio.calculate_total_portfolio_exposure(num_stocks=3, avg_score=3)
    
    print("🎯 IMPLEMENTATION STRATEGY:")
    print("=" * 60)
    print("1. 🔄 Daily monitoring of trend composite scores")
    print("2. 📊 Rebalance when score changes by 1+ point")
    print("3. ⚖️ Equal weighting across selected stocks")
    print("4. 🛡️ Individual stock stop losses at -20%")
    print("5. 📈 Portfolio rebalancing monthly")
    print()
    
    print("📋 RISK MANAGEMENT:")
    print("-" * 40)
    print("• Maximum 3 positions (diversification)")
    print("• No more than 33% in any single stock")
    print("• Stop losses prevent large individual losses") 
    print("• Trend composite reduces drawdown periods")
    print("• High-quality, liquid stocks only")
    
    return selected

if __name__ == "__main__":
    selected_portfolio = run_portfolio_analysis()