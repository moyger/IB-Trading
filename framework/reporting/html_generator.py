"""
HTML Report Generator with VectorBT Visualizations

Professional-grade HTML report generation with interactive charts,
portfolio analytics, and comprehensive strategy analysis.
"""

import pandas as pd
import numpy as np
import vectorbt as vbt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import logging


class HTMLReportGenerator:
    """
    Generate comprehensive HTML reports with interactive visualizations
    using VectorBT and Plotly integration.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize HTML report generator.
        
        Args:
            output_dir: Directory to save HTML reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure Plotly theme
        self.theme = 'plotly_white'
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
            '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
        ]
        
    def generate_strategy_report(self, result: Dict[str, Any], 
                               filename: Optional[str] = None) -> str:
        """
        Generate comprehensive HTML report for single strategy.
        
        Args:
            result: Backtest result dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to generated HTML file
        """
        if filename is None:
            strategy_name = result['strategy']['name'].replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{strategy_name}_{timestamp}.html"
        
        # Extract components
        portfolio = result['portfolio']
        performance = result['performance']
        strategy_info = result['strategy']
        
        # Create main report figure
        fig = self._create_strategy_overview(portfolio, performance, strategy_info)
        
        # Generate HTML content
        html_content = self._generate_html_template(
            title=f"{strategy_info['name']} - Backtest Report",
            figures=[fig],
            summary_data=self._generate_summary_table(result),
            monthly_data=result.get('monthly_summaries', [])
        )
        
        # Save HTML file
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"Strategy report saved: {filepath}")
        return str(filepath)
    
    def generate_comparison_report(self, results: List[Dict[str, Any]], 
                                 title: str = "Strategy Comparison",
                                 filename: Optional[str] = None) -> str:
        """
        Generate HTML comparison report for multiple strategies.
        
        Args:
            results: List of backtest results
            title: Report title
            filename: Output filename
            
        Returns:
            Path to generated HTML file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"strategy_comparison_{timestamp}.html"
        
        # Create comparison charts
        comparison_fig = self._create_comparison_dashboard(results)
        performance_fig = self._create_performance_comparison(results)
        risk_fig = self._create_risk_analysis(results)
        
        # Generate comparison table
        comparison_table = self._generate_comparison_table(results)
        
        # Generate HTML content
        html_content = self._generate_html_template(
            title=title,
            figures=[comparison_fig, performance_fig, risk_fig],
            summary_data=comparison_table,
            monthly_data=[]
        )
        
        # Save HTML file
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"Comparison report saved: {filepath}")
        return str(filepath)
    
    def _create_strategy_overview(self, portfolio: vbt.Portfolio, 
                                performance: Dict[str, Any],
                                strategy_info: Dict[str, Any]) -> go.Figure:
        """Create comprehensive strategy overview with multiple subplots"""
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=[
                'Portfolio Value', 'Drawdown',
                'Trade Signals', 'Returns Distribution', 
                'Monthly P&L', 'Trade Analysis',
                'Risk Metrics', 'Performance Summary'
            ],
            specs=[
                [{"secondary_y": True}, {}],
                [{"colspan": 2}, None],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "table"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.10
        )
        
        # 1. Portfolio Value Chart
        portfolio_value = portfolio.value()
        fig.add_trace(
            go.Scatter(
                x=portfolio_value.index, 
                y=portfolio_value.values,
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='Value: $%{y:,.0f}<br>Date: %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. Drawdown Chart
        drawdown = portfolio.drawdowns.drawdown.values * 100
        fig.add_trace(
            go.Scatter(
                x=portfolio_value.index,
                y=drawdown,
                name='Drawdown %',
                line=dict(color='#d62728', width=1),
                fill='tonexty',
                hovertemplate='Drawdown: %{y:.2f}%<br>Date: %{x}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. Trade Signals (if available)
        if hasattr(portfolio, 'orders') and portfolio.orders.count() > 0:
            orders = portfolio.orders.records_readable
            buy_orders = orders[orders['Side'] == 'Buy']
            sell_orders = orders[orders['Side'] == 'Sell']
            
            if len(buy_orders) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=buy_orders.index,
                        y=buy_orders['Price'],
                        mode='markers',
                        name='Buy Signals',
                        marker=dict(color='green', size=8, symbol='triangle-up'),
                        hovertemplate='Buy: $%{y:,.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            if len(sell_orders) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=sell_orders.index,
                        y=sell_orders['Price'],
                        mode='markers',
                        name='Sell Signals',
                        marker=dict(color='red', size=8, symbol='triangle-down'),
                        hovertemplate='Sell: $%{y:,.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=2, col=1
                )
        
        # 4. Returns Distribution
        returns = portfolio.returns().dropna() * 100
        if len(returns) > 0:
            fig.add_trace(
                go.Histogram(
                    x=returns,
                    name='Returns Distribution',
                    nbinsx=30,
                    marker_color='#2ca02c',
                    opacity=0.7,
                    hovertemplate='Returns: %{x:.2f}%<br>Count: %{y}<extra></extra>'
                ),
                row=2, col=2
            )
        
        # 5. Monthly P&L Bar Chart
        monthly_returns = portfolio.value().resample('M').last().pct_change().dropna() * 100
        if len(monthly_returns) > 0:
            colors = ['green' if x > 0 else 'red' for x in monthly_returns]
            fig.add_trace(
                go.Bar(
                    x=monthly_returns.index,
                    y=monthly_returns.values,
                    name='Monthly Returns',
                    marker_color=colors,
                    hovertemplate='Month: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                ),
                row=3, col=1
            )
        
        # 6. Trade Analysis Scatter
        if hasattr(portfolio, 'trades') and portfolio.trades.count() > 0:
            trade_returns = portfolio.trades.returns.values * 100
            trade_durations = portfolio.trades.duration.values
            
            fig.add_trace(
                go.Scatter(
                    x=trade_durations,
                    y=trade_returns,
                    mode='markers',
                    name='Trade Analysis',
                    marker=dict(
                        color=trade_returns,
                        colorscale='RdYlGn',
                        size=8,
                        colorbar=dict(title="Return %")
                    ),
                    hovertemplate='Duration: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                ),
                row=3, col=2
            )
        
        # 7. Risk Metrics Bar Chart
        risk_metrics = {
            'Volatility': performance.get('volatility', 0),
            'Max Drawdown': abs(performance.get('max_drawdown', 0)),
            'VaR 95%': abs(performance.get('var_95', 0)),
            'Sharpe Ratio': performance.get('sharpe_ratio', 0)
        }
        
        fig.add_trace(
            go.Bar(
                x=list(risk_metrics.keys()),
                y=list(risk_metrics.values()),
                name='Risk Metrics',
                marker_color=['#ff7f0e', '#d62728', '#9467bd', '#2ca02c'],
                hovertemplate='%{x}: %{y:.2f}<extra></extra>'
            ),
            row=4, col=1
        )
        
        # 8. Performance Summary Table
        summary_data = [
            ['Total Return', f"{performance.get('total_return', 0):.2f}%"],
            ['Annualized Return', f"{performance.get('annualized_return', 0):.2f}%"],
            ['Max Drawdown', f"{performance.get('max_drawdown', 0):.2f}%"],
            ['Sharpe Ratio', f"{performance.get('sharpe_ratio', 0):.2f}"],
            ['Win Rate', f"{performance.get('win_rate', 0):.1f}%"],
            ['Total Trades', f"{performance.get('total_trades', 0)}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=[[row[0] for row in summary_data], 
                                 [row[1] for row in summary_data]]),
                columnwidth=[0.7, 0.3]
            ),
            row=4, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text=f"{strategy_info['name']} - Comprehensive Analysis",
            title_x=0.5,
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def _create_comparison_dashboard(self, results: List[Dict[str, Any]]) -> go.Figure:
        """Create strategy comparison dashboard"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Portfolio Value Comparison', 'Drawdown Comparison',
                'Return vs Risk', 'Performance Metrics'
            ]
        )
        
        # Extract data for comparison
        for i, result in enumerate(results):
            portfolio = result['portfolio']
            strategy_name = result['strategy']['name']
            color = self.color_palette[i % len(self.color_palette)]
            
            # Portfolio value comparison
            portfolio_value = portfolio.value()
            normalized_value = (portfolio_value / portfolio_value.iloc[0]) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=portfolio_value.index,
                    y=normalized_value,
                    name=strategy_name,
                    line=dict(color=color),
                    hovertemplate=f'{strategy_name}<br>Value: %{{y:.1f}}<br>Date: %{{x}}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Drawdown comparison
            drawdown = portfolio.drawdowns.drawdown.values * 100
            fig.add_trace(
                go.Scatter(
                    x=portfolio_value.index,
                    y=drawdown,
                    name=f'{strategy_name} DD',
                    line=dict(color=color, dash='dot'),
                    showlegend=False,
                    hovertemplate=f'{strategy_name} DD<br>Drawdown: %{{y:.2f}}%<br>Date: %{{x}}<extra></extra>'
                ),
                row=1, col=2
            )
            
            # Return vs Risk scatter
            performance = result['performance']
            fig.add_trace(
                go.Scatter(
                    x=[performance.get('volatility', 0)],
                    y=[performance.get('total_return', 0)],
                    mode='markers+text',
                    name=strategy_name,
                    marker=dict(color=color, size=15),
                    text=strategy_name,
                    textposition='top center',
                    showlegend=False,
                    hovertemplate=f'{strategy_name}<br>Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Performance metrics comparison table
        metrics_data = []
        strategy_names = []
        
        for result in results:
            strategy_names.append(result['strategy']['name'])
            performance = result['performance']
            metrics_data.append([
                f"{performance.get('total_return', 0):.2f}%",
                f"{performance.get('max_drawdown', 0):.2f}%",
                f"{performance.get('sharpe_ratio', 0):.2f}",
                f"{performance.get('win_rate', 0):.1f}%"
            ])
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Strategy', 'Total Return', 'Max DD', 'Sharpe', 'Win Rate']),
                cells=dict(values=[strategy_names] + list(zip(*metrics_data))),
                columnwidth=[0.3, 0.175, 0.175, 0.175, 0.175]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Strategy Comparison Dashboard",
            title_x=0.5,
            template=self.theme
        )
        
        return fig
    
    def _create_performance_comparison(self, results: List[Dict[str, Any]]) -> go.Figure:
        """Create detailed performance comparison charts"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Monthly Returns Heatmap', 'Rolling Sharpe Ratio',
                'Trade Distribution', 'Risk-Adjusted Returns'
            ]
        )
        
        # This is a placeholder for more detailed comparisons
        # Would need actual implementation based on available data
        
        fig.update_layout(
            height=600,
            title_text="Detailed Performance Analysis",
            title_x=0.5,
            template=self.theme
        )
        
        return fig
    
    def _create_risk_analysis(self, results: List[Dict[str, Any]]) -> go.Figure:
        """Create risk analysis visualization"""
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=['Risk Metrics Comparison', 'Drawdown Analysis']
        )
        
        # Extract risk metrics for comparison
        strategies = []
        volatilities = []
        max_drawdowns = []
        vars = []
        sharpe_ratios = []
        
        for result in results:
            strategies.append(result['strategy']['name'])
            performance = result['performance']
            volatilities.append(performance.get('volatility', 0))
            max_drawdowns.append(abs(performance.get('max_drawdown', 0)))
            vars.append(abs(performance.get('var_95', 0)))
            sharpe_ratios.append(performance.get('sharpe_ratio', 0))
        
        # Risk metrics comparison
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=volatilities,
                name='Volatility',
                marker_color='orange',
                yaxis='y',
                offsetgroup=1
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=max_drawdowns,
                name='Max Drawdown',
                marker_color='red',
                yaxis='y',
                offsetgroup=2
            ),
            row=1, col=1
        )
        
        # Sharpe ratio comparison
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=sharpe_ratios,
                name='Sharpe Ratio',
                marker_color='green'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            title_text="Risk Analysis",
            title_x=0.5,
            template=self.theme
        )
        
        return fig
    
    def _generate_html_template(self, title: str, figures: List[go.Figure],
                              summary_data: Dict[str, Any],
                              monthly_data: List[Dict[str, Any]]) -> str:
        """Generate complete HTML template with embedded charts"""
        
        # Convert figures to HTML
        figures_html = []
        for i, fig in enumerate(figures):
            fig_html = fig.to_html(
                include_plotlyjs='cdn',
                div_id=f"chart_{i}",
                config={'displayModeBar': True, 'responsive': True}
            )
            figures_html.append(fig_html)
        
        # Generate monthly summary table if available
        monthly_table_html = ""
        if monthly_data:
            monthly_table_html = self._generate_monthly_table_html(monthly_data)
        
        # HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 2.5em;
                }}
                .timestamp {{
                    color: #6c757d;
                    font-size: 1.1em;
                    margin-top: 10px;
                }}
                .chart-container {{
                    margin: 30px 0;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 15px;
                }}
                .summary-section {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .monthly-section {{
                    background-color: #fff;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #e9ecef;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e9ecef;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                    color: #2c3e50;
                }}
                .positive {{
                    color: #28a745;
                }}
                .negative {{
                    color: #dc3545;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <div class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                
                {''.join([f'<div class="chart-container">{fig_html}</div>' for fig_html in figures_html])}
                
                {monthly_table_html}
                
                <div class="footer">
                    <p>Generated by Universal Backtesting Framework with VectorBT</p>
                    <p>This report contains backtested performance data. Past performance does not guarantee future results.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_monthly_table_html(self, monthly_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for monthly performance data"""
        
        if not monthly_data:
            return ""
        
        table_rows = []
        total_pnl = 0
        profitable_months = 0
        
        for month in monthly_data:
            pnl = month.get('pnl', 0)
            pnl_pct = month.get('pnl_pct', 0)
            total_pnl += pnl
            
            if pnl > 0:
                profitable_months += 1
                pnl_class = 'positive'
                emoji = '📈'
            else:
                pnl_class = 'negative'
                emoji = '📉'
            
            table_rows.append(f"""
                <tr>
                    <td>{month.get('month', '')}</td>
                    <td>${month.get('starting_balance', 0):,.0f}</td>
                    <td>${month.get('ending_balance', 0):,.0f}</td>
                    <td class="{pnl_class}">${pnl:+,.0f}</td>
                    <td class="{pnl_class}">{pnl_pct:+.2f}%</td>
                    <td>{month.get('trades', 0)}</td>
                    <td>{emoji}</td>
                </tr>
            """)
        
        win_rate = (profitable_months / len(monthly_data)) * 100 if monthly_data else 0
        avg_monthly = total_pnl / len(monthly_data) if monthly_data else 0
        
        return f"""
        <div class="monthly-section">
            <h2>📅 Monthly Performance Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Start Balance</th>
                        <th>End Balance</th>
                        <th>P&L ($)</th>
                        <th>P&L (%)</th>
                        <th>Trades</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
            <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                <strong>Summary:</strong> 
                Total P&L: <span class="{'positive' if total_pnl > 0 else 'negative'}">${total_pnl:+,.0f}</span> | 
                Profitable Months: {profitable_months}/{len(monthly_data)} ({win_rate:.1f}%) | 
                Average Monthly: <span class="{'positive' if avg_monthly > 0 else 'negative'}">${avg_monthly:+,.0f}</span>
            </div>
        </div>
        """
    
    def _generate_summary_table(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for the strategy"""
        return {
            'strategy': result.get('strategy', {}),
            'performance': result.get('performance', {}),
            'period': result.get('period', ''),
            'data_points': result.get('data_points', 0)
        }
    
    def _generate_comparison_table(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparison table data"""
        comparison_data = []
        
        for result in results:
            strategy_info = result.get('strategy', {})
            performance = result.get('performance', {})
            
            comparison_data.append({
                'name': strategy_info.get('name', 'Unknown'),
                'total_return': performance.get('total_return', 0),
                'max_drawdown': performance.get('max_drawdown', 0),
                'sharpe_ratio': performance.get('sharpe_ratio', 0),
                'win_rate': performance.get('win_rate', 0),
                'total_trades': performance.get('total_trades', 0)
            })
        
        return {'comparison_data': comparison_data}