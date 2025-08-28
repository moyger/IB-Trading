# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Architecture

This repository contains cryptocurrency trading strategies adapted from FTMO (Forex) success patterns for crypto markets. The codebase has evolved from a multi-strategy universal system to three focused individual strategies:

## References
1. https://github.com/topics/trading-algorithms?l=python

2. https://docs.pytrade.org/




## Key Backtest Metrics
1. Return Metrics

CAGR (Compounded Annual Growth Rate): Average annual growth of equity curve. Shows long-term profitability.

Total Return: Overall % gained/lost in the test period.

Monthly / Quarterly Returns: To check consistency.

2. Risk Metrics

Max Drawdown (MDD): Largest peak-to-trough equity decline. Lower is better.

Volatility (Std. Dev of returns): How “bumpy” returns are.

Downside Deviation: Measures only negative volatility (more useful than total volatility).

Value at Risk (VaR): Probable worst loss at a confidence level.

3. Risk-Adjusted Metrics

Sharpe Ratio: Return ÷ volatility. (>1 good, >2 very good, >3 excellent).

Sortino Ratio: Return ÷ downside volatility. Better for asymmetric strategies.

Calmar Ratio: CAGR ÷ Max Drawdown. Tells how much return is achieved per unit of drawdown.

Profit Factor (PF): Gross profits ÷ gross losses. (>1.5 is decent, >2 strong).

4. Trade-Level Metrics

Win Rate (%): % of trades that are winners. High win rate isn’t always better — depends on payoff.

Average R per Trade: Expected return relative to risk (expectancy). A positive expectancy >0.3R is a good sign.

Payoff Ratio (Avg Win ÷ Avg Loss): Risk-to-reward on executed trades.

Trade Frequency: Number of trades per month/quarter. Too few = slow edge validation, too many = noise.

5. Consistency Metrics

Equity Curve Smoothness: Less chop = more stable strategy.

% of Profitable Months: Good check for robustness.

Rolling Expectancy: Does the strategy’s edge persist across different market conditions?

6. Robustness Checks

Out-of-Sample Test: Forward test on unseen data.

Walk-Forward Analysis: Rolling windows to see if parameters adapt well.

Monte Carlo Simulations: Randomizing trade order to check risk of ruin.

Different Market Regimes: Trending, ranging, high-vol, low-vol periods.

7. Monthly summary with P&L and running balance

## Important Notes

- Always backtest strategies in 24 months period August 2023 to  July 2025
- When we do a backtest, create a log in markdown format in /backtest-logs 

- the backtest should always include a monthly summary with P&L amount and percentage, running balance and number of trades