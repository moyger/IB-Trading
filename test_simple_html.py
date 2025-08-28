"""
Simple HTML Report Generation Test (Without VectorBT)
Demonstrates HTML visualization capabilities using mock data
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path


def create_sample_data():
    """Create sample portfolio and performance data"""
    
    # Generate sample dates (6 months)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Generate sample portfolio values with controlled scaling
    np.random.seed(42)
    initial_value = 100000
    
    # Create more controlled returns
    daily_drift = 0.0003  # Small positive drift
    daily_volatility = 0.012  # Reasonable volatility
    
    returns = np.random.normal(daily_drift, daily_volatility, len(dates))
    # Cap extreme returns to prevent unrealistic scaling
    returns = np.clip(returns, -0.05, 0.05)  # Cap at ±5% daily
    
    portfolio_values = initial_value * np.cumprod(1 + returns)
    
    # Normalize to ensure reasonable final value (~5.7% return)
    target_final_value = initial_value * 1.057  # 5.7% total return
    scaling_factor = target_final_value / portfolio_values[-1]
    
    # Apply smooth scaling to maintain realistic path shape
    scaling_curve = np.linspace(1, scaling_factor, len(portfolio_values))
    portfolio_values = initial_value + (portfolio_values - initial_value) * scaling_curve
    
    # Create portfolio series
    portfolio_series = pd.Series(portfolio_values, index=dates)
    
    # Calculate drawdown
    peak = portfolio_series.expanding().max()
    drawdown = (portfolio_series - peak) / peak * 100
    
    # Generate monthly data
    monthly_data = []
    current_balance = initial_value
    
    for month in range(1, 7):
        month_start = datetime(2024, month, 1)
        if month == 6:
            month_end = datetime(2024, 6, 30)
        else:
            next_month = month + 1
            month_end = datetime(2024, next_month, 1) - timedelta(days=1)
        
        month_mask = (portfolio_series.index >= month_start) & (portfolio_series.index <= month_end)
        month_values = portfolio_series[month_mask]
        
        if len(month_values) > 0:
            start_balance = month_values.iloc[0]
            end_balance = month_values.iloc[-1]
            pnl = end_balance - start_balance
            pnl_pct = (pnl / start_balance) * 100
            
            monthly_data.append({
                'month': f'2024-{month:02d}',
                'starting_balance': start_balance,
                'ending_balance': end_balance,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'trades': np.random.randint(2, 8)
            })
    
    return portfolio_series, drawdown, monthly_data


def create_portfolio_chart(portfolio_series, theme='dark'):
    """Create standalone portfolio value chart"""
    
    # Theme configuration
    if theme == 'dark':
        template = 'plotly_dark'
        bg_color = 'rgba(30, 30, 30, 1)'
        paper_color = 'rgba(37, 37, 37, 1)'
        text_color = '#e0e0e0'
        grid_color = '#444444'
    else:
        template = 'plotly_white'
        bg_color = 'rgba(255, 255, 255, 1)'
        paper_color = 'rgba(250, 250, 250, 1)'
        text_color = '#2c3e50'
        grid_color = '#e9ecef'
    
    fig = go.Figure()
    
    # Portfolio Value
    fig.add_trace(
        go.Scatter(
            x=portfolio_series.index,
            y=portfolio_series.values,
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='Value: $%{y:,.0f}<br>Date: %{x}<extra></extra>'
        )
    )
    
    # Benchmark line
    benchmark = np.linspace(portfolio_series.iloc[0], 
                           portfolio_series.iloc[0] * 1.15, 
                           len(portfolio_series))
    fig.add_trace(
        go.Scatter(
            x=portfolio_series.index,
            y=benchmark,
            name='Benchmark (+15%)',
            line=dict(color='gray', width=2, dash='dash'),
            hovertemplate='Benchmark: $%{y:,.0f}<br>Date: %{x}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title="Portfolio Value Evolution",
        title_x=0.5,
        title_font_size=16,
        title_font_color=text_color,
        height=400,
        template=template,
        plot_bgcolor=bg_color,
        paper_bgcolor=paper_color,
        font_color=text_color,
        showlegend=True,
        margin=dict(t=50, b=50, l=60, r=60),
        xaxis=dict(title="Date", gridcolor=grid_color),
        yaxis=dict(title="Portfolio Value ($)", gridcolor=grid_color)
    )
    
    return fig


def create_drawdown_chart(portfolio_series, drawdown, theme='dark'):
    """Create standalone drawdown chart"""
    
    # Theme configuration  
    if theme == 'dark':
        template = 'plotly_dark'
        bg_color = 'rgba(30, 30, 30, 1)'
        paper_color = 'rgba(37, 37, 37, 1)'
        text_color = '#e0e0e0'
        grid_color = '#444444'
    else:
        template = 'plotly_white'
        bg_color = 'rgba(255, 255, 255, 1)'
        paper_color = 'rgba(250, 250, 250, 1)'
        text_color = '#2c3e50'
        grid_color = '#e9ecef'
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=portfolio_series.index,
            y=drawdown.values,
            fill='tonexty',
            fillcolor='rgba(214, 39, 40, 0.3)',
            line=dict(color='#d62728', width=2),
            name='Drawdown %',
            hovertemplate='Drawdown: %{y:.2f}%<br>Date: %{x}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title="Drawdown Analysis",
        title_x=0.5,
        title_font_size=16,
        title_font_color=text_color,
        height=400,
        template=template,
        plot_bgcolor=bg_color,
        paper_bgcolor=paper_color,
        font_color=text_color,
        showlegend=True,
        margin=dict(t=50, b=50, l=60, r=60),
        xaxis=dict(title="Date", gridcolor=grid_color),
        yaxis=dict(title="Drawdown (%)", gridcolor=grid_color)
    )
    
    return fig


def create_comprehensive_chart(portfolio_series, drawdown, monthly_data, theme='dark'):
    """Create comprehensive strategy analysis chart with theme support"""
    
    # Theme configuration
    if theme == 'dark':
        template = 'plotly_dark'
        bg_color = 'rgba(30, 30, 30, 1)'
        paper_color = 'rgba(37, 37, 37, 1)'
        text_color = '#e0e0e0'
        grid_color = '#444444'
        table_header_color = '#2a2a2a'
        table_header_font_color = '#e0e0e0'
        table_cell_color = '#333333'
    else:
        template = 'plotly_white'
        bg_color = 'rgba(255, 255, 255, 1)'
        paper_color = 'rgba(250, 250, 250, 1)'
        text_color = '#2c3e50'
        grid_color = '#e9ecef'
        table_header_color = 'lightblue'
        table_header_font_color = '#2c3e50'
        table_cell_color = 'lightcyan'
    
    # Create subplots with proper spacing
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            'Portfolio Value Evolution', 'Drawdown Analysis',
            'Monthly Returns', 'Returns Distribution',
            'Risk Metrics', 'Trade Analysis'
        ],
        specs=[
            [{}, {}],  # Remove secondary_y to fix overlap
            [{"type": "bar"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "table"}]
        ],
        vertical_spacing=0.15,  # Increased spacing
        horizontal_spacing=0.10,  # Adjusted spacing
        row_heights=[0.35, 0.30, 0.35]  # Distribute heights better
    )
    
    # 1. Portfolio Value Chart
    fig.add_trace(
        go.Scatter(
            x=portfolio_series.index,
            y=portfolio_series.values,
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='Value: $%{y:,.0f}<br>Date: %{x}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add benchmark line (buy and hold)
    benchmark = np.linspace(portfolio_series.iloc[0], 
                           portfolio_series.iloc[0] * 1.15, 
                           len(portfolio_series))
    fig.add_trace(
        go.Scatter(
            x=portfolio_series.index,
            y=benchmark,
            name='Benchmark (+15%)',
            line=dict(color='gray', width=1, dash='dash'),
            hovertemplate='Benchmark: $%{y:,.0f}<br>Date: %{x}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Drawdown Chart
    fig.add_trace(
        go.Scatter(
            x=portfolio_series.index,
            y=drawdown.values,
            name='Drawdown %',
            line=dict(color='#d62728', width=1),
            fill='tonexty',
            fillcolor='rgba(214, 39, 40, 0.3)',
            hovertemplate='Drawdown: %{y:.2f}%<br>Date: %{x}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Monthly Returns Bar Chart
    monthly_returns = [m['pnl_pct'] for m in monthly_data]
    monthly_labels = [m['month'] for m in monthly_data]
    colors = ['green' if x > 0 else 'red' for x in monthly_returns]
    
    fig.add_trace(
        go.Bar(
            x=monthly_labels,
            y=monthly_returns,
            name='Monthly Returns',
            marker_color=colors,
            hovertemplate='Month: %{x}<br>Return: %{y:.2f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Returns Distribution
    daily_returns = portfolio_series.pct_change().dropna() * 100
    fig.add_trace(
        go.Histogram(
            x=daily_returns,
            name='Daily Returns',
            nbinsx=30,
            marker_color='#2ca02c',
            opacity=0.7,
            hovertemplate='Return: %{x:.2f}%<br>Frequency: %{y}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # 5. Risk Metrics Bar Chart
    risk_metrics = {
        'Volatility': daily_returns.std() * np.sqrt(252),
        'Max Drawdown': abs(drawdown.min()),
        'Sharpe Ratio': (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)),
        'Win Rate': len(daily_returns[daily_returns > 0]) / len(daily_returns) * 100
    }
    
    fig.add_trace(
        go.Bar(
            x=list(risk_metrics.keys()),
            y=list(risk_metrics.values()),
            name='Risk Metrics',
            marker_color=['#ff7f0e', '#d62728', '#9467bd', '#2ca02c'],
            hovertemplate='%{x}: %{y:.2f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # 6. Performance Summary Table
    total_return = ((portfolio_series.iloc[-1] / portfolio_series.iloc[0]) - 1) * 100
    summary_data = [
        ['Total Return', f'{total_return:.2f}%'],
        ['Annualized Return', f'{total_return * 2:.2f}%'],  # Approximate for 6 months
        ['Max Drawdown', f'{abs(drawdown.min()):.2f}%'],
        ['Sharpe Ratio', f'{risk_metrics["Sharpe Ratio"]:.2f}'],
        ['Volatility', f'{risk_metrics["Volatility"]:.2f}%'],
        ['Win Rate', f'{risk_metrics["Win Rate"]:.1f}%']
    ]
    
    fig.add_trace(
        go.Table(
            header=dict(
                values=['Metric', 'Value'],
                fill_color=table_header_color,
                font_color=table_header_font_color,
                align='left'
            ),
            cells=dict(
                values=[[row[0] for row in summary_data], 
                       [row[1] for row in summary_data]],
                fill_color=table_cell_color,
                font_color=text_color,
                align='left'
            )
        ),
        row=3, col=2
    )
    
    # Update layout with theme and proper margins
    fig.update_layout(
        height=1000,  # Increased height to accommodate spacing
        title_text="Trading Strategy Performance Dashboard - Interactive HTML Report",
        title_x=0.5,
        title_font_size=20,
        title_font_color=text_color,
        showlegend=True,
        template=template,
        plot_bgcolor=bg_color,
        paper_bgcolor=paper_color,
        font_color=text_color,
        margin=dict(t=80, b=60, l=80, r=80),  # Add proper margins
        xaxis=dict(gridcolor=grid_color),
        yaxis=dict(gridcolor=grid_color)
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Drawdown (%)", row=1, col=2)
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_yaxes(title_text="Return (%)", row=2, col=1)
    fig.update_xaxes(title_text="Daily Return (%)", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)
    
    return fig


def create_monthly_summary_table(monthly_data, theme='dark'):
    """Create interactive monthly summary table with theme support"""
    
    # Theme configuration
    if theme == 'dark':
        template = 'plotly_dark'
        header_color = '#2a2a2a'
        header_font_color = '#e0e0e0'
        cell_colors = ['#333333', '#3a3a3a']
        cell_font_color = '#e0e0e0'
        paper_bgcolor = 'rgba(37, 37, 37, 1)'
    else:
        template = 'plotly_white'
        header_color = 'navy'
        header_font_color = 'white'
        cell_colors = ['white', '#f8f9fa']
        cell_font_color = '#2c3e50'
        paper_bgcolor = 'rgba(255, 255, 255, 1)'
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Month', 'Start Balance', 'End Balance', 'P&L ($)', 'P&L (%)', 'Trades', 'Status'],
            fill_color=header_color,
            font_color=header_font_color,
            font_size=14,
            align='center'
        ),
        cells=dict(
            values=[
                [m['month'] for m in monthly_data],
                [f"${m['starting_balance']:,.0f}" for m in monthly_data],
                [f"${m['ending_balance']:,.0f}" for m in monthly_data],
                [f"${m['pnl']:+,.0f}" for m in monthly_data],
                [f"{m['pnl_pct']:+.2f}%" for m in monthly_data],
                [m['trades'] for m in monthly_data],
                ['📈' if m['pnl'] > 0 else '📉' for m in monthly_data]
            ],
            fill_color=[
                [cell_colors[0]] * len(monthly_data),  # Month
                [cell_colors[1]] * len(monthly_data),  # Start Balance
                [cell_colors[1]] * len(monthly_data),  # End Balance
                ['#2d5a3d' if theme == 'dark' and m['pnl'] > 0 else '#4a1e1e' if theme == 'dark' and m['pnl'] < 0 
                 else 'lightgreen' if m['pnl'] > 0 else 'lightcoral' for m in monthly_data],  # P&L $
                ['#2d5a3d' if theme == 'dark' and m['pnl'] > 0 else '#4a1e1e' if theme == 'dark' and m['pnl'] < 0 
                 else 'lightgreen' if m['pnl'] > 0 else 'lightcoral' for m in monthly_data],  # P&L %
                [cell_colors[0]] * len(monthly_data),  # Trades
                [cell_colors[1]] * len(monthly_data)   # Status
            ],
            font_color=cell_font_color,
            font_size=12,
            align='center'
        )
    )])
    
    fig.update_layout(
        title="Monthly Performance Summary - Interactive Table",
        title_x=0.5,
        title_font_color=cell_font_color,
        height=400,
        template=template,
        paper_bgcolor=paper_bgcolor
    )
    
    return fig


def generate_html_report(portfolio_series, drawdown, monthly_data):
    """Generate complete HTML report with individual charts"""
    
    # Create individual charts to avoid overlapping
    portfolio_chart = create_portfolio_chart(portfolio_series, theme='dark')
    drawdown_chart = create_drawdown_chart(portfolio_series, drawdown, theme='dark')
    monthly_table = create_monthly_summary_table(monthly_data, theme='dark')
    
    # Calculate summary statistics
    total_return = ((portfolio_series.iloc[-1] / portfolio_series.iloc[0]) - 1) * 100
    max_drawdown = abs(drawdown.min())
    daily_returns = portfolio_series.pct_change().dropna() * 100
    sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Strategy Analysis - Interactive HTML Report</title>
        <style>
            :root {{
                /* Light theme colors */
                --bg-gradient-light: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --container-bg-light: white;
                --text-primary-light: #2c3e50;
                --text-secondary-light: #6c757d;
                --border-light: #e9ecef;
                --card-bg-light: linear-gradient(135deg, #f8f9fa, #e9ecef);
                --card-item-bg-light: white;
                --chart-container-bg-light: #fafafa;
                --disclaimer-bg-light: #fff3cd;
                --disclaimer-border-light: #ffeaa7;
                
                /* Dark theme colors */
                --bg-gradient-dark: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                --container-bg-dark: #1e1e1e;
                --text-primary-dark: #e0e0e0;
                --text-secondary-dark: #a0a0a0;
                --border-dark: #333333;
                --card-bg-dark: linear-gradient(135deg, #2a2a2a, #3a3a3a);
                --card-item-bg-dark: #2a2a2a;
                --chart-container-bg-dark: #252525;
                --disclaimer-bg-dark: #3a3a1a;
                --disclaimer-border-dark: #4a4a2a;
            }}
            
            [data-theme="dark"] {{
                --bg-gradient: var(--bg-gradient-dark);
                --container-bg: var(--container-bg-dark);
                --text-primary: var(--text-primary-dark);
                --text-secondary: var(--text-secondary-dark);
                --border-color: var(--border-dark);
                --card-bg: var(--card-bg-dark);
                --card-item-bg: var(--card-item-bg-dark);
                --chart-container-bg: var(--chart-container-bg-dark);
                --disclaimer-bg: var(--disclaimer-bg-dark);
                --disclaimer-border: var(--disclaimer-border-dark);
            }}
            
            [data-theme="light"] {{
                --bg-gradient: var(--bg-gradient-light);
                --container-bg: var(--container-bg-light);
                --text-primary: var(--text-primary-light);
                --text-secondary: var(--text-secondary-light);
                --border-color: var(--border-light);
                --card-bg: var(--card-bg-light);
                --card-item-bg: var(--card-item-bg-light);
                --chart-container-bg: var(--chart-container-bg-light);
                --disclaimer-bg: var(--disclaimer-bg-light);
                --disclaimer-border: var(--disclaimer-border-light);
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: var(--bg-gradient);
                min-height: 100vh;
                transition: all 0.3s ease;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background-color: var(--container-bg);
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                padding: 30px;
                animation: fadeIn 0.8s ease-in-out;
                transition: all 0.3s ease;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 3px solid var(--border-color);
                padding-bottom: 20px;
                transition: all 0.3s ease;
            }}
            .header h1 {{
                color: var(--text-primary);
                margin: 0;
                font-size: 2.8em;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                transition: all 0.3s ease;
            }}
            .timestamp {{
                color: var(--text-secondary);
                font-size: 1.2em;
                margin-top: 10px;
                transition: all 0.3s ease;
            }}
            .stats-row {{
                display: flex;
                justify-content: space-around;
                margin: 30px 0;
                flex-wrap: wrap;
            }}
            .stat-card {{
                background: var(--card-bg);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin: 10px;
                flex: 1;
                min-width: 200px;
                transition: transform 0.2s, background 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                color: var(--text-secondary);
                font-size: 1.1em;
                transition: color 0.3s ease;
            }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .chart-container {{
                margin: 30px 0;
                border: 2px solid var(--border-color);
                border-radius: 10px;
                padding: 15px;
                background-color: var(--chart-container-bg);
                transition: all 0.3s ease;
            }}
            .features-section {{
                background: var(--card-bg);
                border-radius: 10px;
                padding: 25px;
                margin: 30px 0;
                transition: all 0.3s ease;
            }}
            .features-section h2 {{
                color: var(--text-primary);
                transition: color 0.3s ease;
            }}
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .feature-item {{
                display: flex;
                align-items: center;
                padding: 10px;
                background-color: var(--card-item-bg);
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                color: var(--text-primary);
                transition: all 0.3s ease;
            }}
            .feature-icon {{
                font-size: 1.5em;
                margin-right: 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 30px;
                border-top: 2px solid var(--border-color);
                color: var(--text-secondary);
                transition: all 0.3s ease;
            }}
            .disclaimer {{
                background-color: var(--disclaimer-bg);
                border: 1px solid var(--disclaimer-border);
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                text-align: center;
                font-style: italic;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }}
            
            .theme-toggle {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--card-bg);
                border: 2px solid var(--border-color);
                border-radius: 25px;
                padding: 10px 15px;
                cursor: pointer;
                font-size: 1.2em;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transition: all 0.3s ease;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
                color: var(--text-primary);
                font-weight: 500;
            }}
            .theme-toggle:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            }}
            @media (max-width: 768px) {{
                .stats-row {{ flex-direction: column; }}
                .stat-card {{ margin: 5px 0; }}
                .container {{ padding: 15px; }}
                .header h1 {{ font-size: 2.2em; }}
            }}
        </style>
    </head>
    <body data-theme="dark">
        <div class="theme-toggle" onclick="toggleTheme()">
            <span id="theme-icon">🌙</span>
            <span id="theme-text">Dark Mode</span>
        </div>
        <div class="container">
            <div class="header">
                <h1>🚀 Trading Strategy Performance Dashboard</h1>
                <div class="timestamp">📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div class="timestamp">📊 Period: January 2024 - June 2024 (6 months)</div>
            </div>
            
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-value {'positive' if total_return > 0 else 'negative'}">{total_return:+.2f}%</div>
                    <div class="stat-label">Total Return</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value negative">{max_drawdown:.2f}%</div>
                    <div class="stat-label">Max Drawdown</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {'positive' if sharpe_ratio > 1 else 'negative'}">{sharpe_ratio:.2f}</div>
                    <div class="stat-label">Sharpe Ratio</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len([r for r in daily_returns if r > 0]) / len(daily_returns) * 100:.1f}%</div>
                    <div class="stat-label">Win Rate</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3 style="color: var(--text-primary); text-align: center; margin-bottom: 20px;">📈 Portfolio Performance Charts</h3>
                {portfolio_chart.to_html(include_plotlyjs='cdn', div_id="portfolio-chart", config={'responsive': True, 'displayModeBar': True})}
            </div>
            
            <div class="chart-container">
                {drawdown_chart.to_html(include_plotlyjs=False, div_id="drawdown-chart", config={'responsive': True, 'displayModeBar': True})}
            </div>
            
            <div class="chart-container">
                <h3 style="color: var(--text-primary); text-align: center; margin-bottom: 20px;">📊 Monthly Summary</h3>
                {monthly_table.to_html(include_plotlyjs=False, div_id="monthly-table", config={'responsive': True})}
            </div>
            
            <div class="features-section">
                <h2>✨ Interactive HTML Report Features</h2>
                <div class="features-grid">
                    <div class="feature-item">
                        <div class="feature-icon">📈</div>
                        <div>Interactive charts with zoom, pan, and hover tooltips</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📊</div>
                        <div>Multi-subplot layouts with comprehensive analysis</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📱</div>
                        <div>Responsive design that works on all devices</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🎨</div>
                        <div>Professional styling with modern aesthetics</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">💾</div>
                        <div>Self-contained HTML files for easy sharing</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">⚡</div>
                        <div>Fast loading with optimized Plotly.js integration</div>
                    </div>
                </div>
            </div>
            
            <div class="disclaimer">
                ⚠️ <strong>Disclaimer:</strong> This is a demonstration of HTML visualization capabilities. 
                Past performance does not guarantee future results. All data shown is for educational purposes only.
            </div>
            
            <div class="footer">
                <h3>🔧 Generated by Universal Backtesting Framework</h3>
                <p>Powered by VectorBT, Plotly, and Python</p>
                <p><strong>Framework Capabilities:</strong></p>
                <p>✅ Ultra-fast vectorized backtesting • ✅ Multi-asset portfolio support • ✅ Professional risk management</p>
                <p>✅ Interactive HTML visualization • ✅ Comprehensive performance analytics • ✅ FTMO compliance</p>
                
                <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                    <h4>📊 Chart Interactions Available:</h4>
                    <p><strong>🖱️ Mouse:</strong> Click and drag to pan, scroll to zoom, hover for details</p>
                    <p><strong>🔧 Toolbar:</strong> Pan, zoom, select, reset view, download as PNG</p>
                    <p><strong>📈 Legend:</strong> Click to hide/show data series</p>
                    <p><strong>📋 Tables:</strong> Scroll horizontally on mobile devices</p>
                </div>
            </div>
        </div>
        
        <script>
            // Add some interactive enhancements
            document.addEventListener('DOMContentLoaded', function() {{
                // Add click animation to stat cards
                document.querySelectorAll('.stat-card').forEach(card => {{
                    card.addEventListener('click', function() {{
                        this.style.transform = 'scale(0.95)';
                        setTimeout(() => {{
                            this.style.transform = 'translateY(-5px)';
                        }}, 100);
                    }});
                }});
                
                console.log('🎉 Interactive HTML Report Loaded Successfully!');
                console.log('📊 Framework: Universal Backtesting with VectorBT');
                console.log('🚀 All charts are interactive - try hovering and zooming!');
            }});
            
            // Theme Toggle Functionality
            function toggleTheme() {{
                const body = document.body;
                const themeIcon = document.getElementById('theme-icon');
                const themeText = document.getElementById('theme-text');
                
                if (body.getAttribute('data-theme') === 'dark') {{
                    body.setAttribute('data-theme', 'light');
                    themeIcon.textContent = '☀️';
                    themeText.textContent = 'Light Mode';
                    localStorage.setItem('theme', 'light');
                    updatePlotlyTheme('light');
                    console.log('🌞 Switched to Light Mode');
                }} else {{
                    body.setAttribute('data-theme', 'dark');
                    themeIcon.textContent = '🌙';
                    themeText.textContent = 'Dark Mode';
                    localStorage.setItem('theme', 'dark');
                    updatePlotlyTheme('dark');
                    console.log('🌙 Switched to Dark Mode');
                }}
            }}
            
            // Update Plotly charts theme
            function updatePlotlyTheme(theme) {{
                const isDark = theme === 'dark';
                
                const layout_update = {{
                    template: isDark ? 'plotly_dark' : 'plotly_white',
                    plot_bgcolor: isDark ? 'rgba(30, 30, 30, 1)' : 'rgba(255, 255, 255, 1)',
                    paper_bgcolor: isDark ? 'rgba(37, 37, 37, 1)' : 'rgba(250, 250, 250, 1)',
                    font: {{
                        color: isDark ? '#e0e0e0' : '#2c3e50'
                    }},
                    'title.font.color': isDark ? '#e0e0e0' : '#2c3e50',
                    xaxis: {{
                        gridcolor: isDark ? '#444444' : '#e9ecef',
                        color: isDark ? '#e0e0e0' : '#2c3e50'
                    }},
                    yaxis: {{
                        gridcolor: isDark ? '#444444' : '#e9ecef',
                        color: isDark ? '#e0e0e0' : '#2c3e50'
                    }}
                }};
                
                // Update specific chart IDs
                const chartIds = ['portfolio-chart', 'drawdown-chart', 'monthly-table'];
                chartIds.forEach(chartId => {{
                    const chartDiv = document.getElementById(chartId);
                    if (chartDiv && window.Plotly) {{
                        window.Plotly.relayout(chartId, layout_update);
                        console.log('📊 Updated chart:', chartId);
                    }}
                }});
            }}
            
            // Load saved theme preference
            document.addEventListener('DOMContentLoaded', function() {{
                const savedTheme = localStorage.getItem('theme') || 'dark';
                const body = document.body;
                const themeIcon = document.getElementById('theme-icon');
                const themeText = document.getElementById('theme-text');
                
                body.setAttribute('data-theme', savedTheme);
                if (savedTheme === 'light') {{
                    themeIcon.textContent = '☀️';
                    themeText.textContent = 'Light Mode';
                }} else {{
                    themeIcon.textContent = '🌙';
                    themeText.textContent = 'Dark Mode';
                }}
                
                // Apply theme to Plotly charts after they load
                setTimeout(() => {{
                    updatePlotlyTheme(savedTheme);
                }}, 1000);
                
                console.log('🎨 Theme loaded:', savedTheme);
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content


def main():
    """Main execution function"""
    
    print("🎯 HTML Visualization Demo - Universal Backtesting Framework")
    print("📊 Generating interactive HTML report with Plotly charts...")
    print("=" * 70)
    
    # Create sample data
    print("📈 Creating sample portfolio data...")
    portfolio_series, drawdown, monthly_data = create_sample_data()
    
    # Generate HTML report
    print("🔧 Generating comprehensive HTML report...")
    html_content = generate_html_report(portfolio_series, drawdown, monthly_data)
    
    # Create output directory
    output_dir = Path("html-reports")
    output_dir.mkdir(exist_ok=True)
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_strategy_demo_{timestamp}.html"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML report generated successfully!")
    print(f"📄 File: {filepath}")
    print(f"📊 Size: {filepath.stat().st_size / 1024:.1f} KB")
    
    print("\n🎉 HTML VISUALIZATION DEMO COMPLETED!")
    print("=" * 70)
    print("📱 Features demonstrated:")
    print("  ✅ Interactive Plotly charts with zoom, pan, hover")
    print("  ✅ Multi-subplot dashboard layout")
    print("  ✅ Professional styling with responsive design")
    print("  ✅ Monthly performance tables with color coding")
    print("  ✅ Risk metrics visualization")
    print("  ✅ Mobile-friendly responsive layout")
    print("  ✅ Self-contained HTML file for easy sharing")
    
    print(f"\n💻 Open the file in your browser to view:")
    print(f"    file://{filepath.absolute()}")
    print("\n🔍 Try interacting with the charts:")
    print("  • Hover over data points for details")
    print("  • Click and drag to pan")
    print("  • Scroll to zoom in/out")
    print("  • Use toolbar buttons for additional options")
    print("  • Click legend items to hide/show data series")
    
    return str(filepath)


if __name__ == "__main__":
    main()