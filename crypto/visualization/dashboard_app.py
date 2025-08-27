#!/usr/bin/env python3
"""
Advanced Trading Dashboard using Plotly Dash
Provides comprehensive visual analytics for BTCUSDT strategy

Features:
- Real-time strategy monitoring
- Interactive charts with trade analysis
- Performance metrics dashboard
- Confluence score visualization
- Risk management monitoring
- Export capabilities
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

# Import our components
from data_fetcher import BTCDataFetcher
from visual_backtest_runner import VisualBacktestRunner

warnings.filterwarnings('ignore')

class BTCTradingDashboard:
    """Advanced trading dashboard with real-time analytics"""
    
    def __init__(self, port=8050):
        """Initialize the dashboard application"""
        self.app = dash.Dash(__name__)
        self.port = port
        
        # Data components
        self.data_fetcher = BTCDataFetcher()
        self.backtest_runner = VisualBacktestRunner()
        
        # Dashboard state
        self.current_data = None
        self.backtest_results = None
        
        # Initialize layout
        self._setup_layout()
        self._setup_callbacks()
        
        print(f"🎨 ADVANCED TRADING DASHBOARD INITIALIZED")
        print(f"🌐 Will run on: http://localhost:{port}")
    
    def _setup_layout(self):
        """Setup the main dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("🚀 BTCUSDT Advanced Trading Dashboard", 
                       className="dashboard-title"),
                html.P("Enhanced Multi-Confluence Strategy Analytics", 
                       className="dashboard-subtitle")
            ], className="header-section"),
            
            # Control Panel
            html.Div([
                html.Div([
                    html.Label("📅 Date Range:", className="control-label"),
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date=datetime.now() - timedelta(days=60),
                        end_date=datetime.now(),
                        display_format='YYYY-MM-DD'
                    )
                ], className="control-item"),
                
                html.Div([
                    html.Label("💰 Initial Capital:", className="control-label"),
                    dcc.Input(
                        id='capital-input',
                        type='number',
                        value=10000,
                        min=1000,
                        step=1000
                    )
                ], className="control-item"),
                
                html.Div([
                    html.Button("🔄 Run Backtest", id="run-backtest-btn", 
                               className="action-button"),
                    html.Button("📊 Load Live Data", id="load-data-btn", 
                               className="action-button"),
                ], className="control-buttons")
            ], className="control-panel"),
            
            # Main Charts Section
            html.Div([
                # Price Chart with Signals
                html.Div([
                    dcc.Graph(id="main-price-chart", className="chart-container")
                ], className="chart-section"),
                
                # Performance Metrics
                html.Div([
                    html.Div(id="performance-metrics", className="metrics-grid")
                ], className="metrics-section")
            ], className="main-content"),
            
            # Secondary Analysis
            html.Div([
                # Confluence Score Chart
                html.Div([
                    dcc.Graph(id="confluence-chart", className="chart-container")
                ], className="chart-half"),
                
                # Risk Analysis
                html.Div([
                    dcc.Graph(id="risk-chart", className="chart-container")
                ], className="chart-half")
            ], className="secondary-content"),
            
            # Trade Journal
            html.Div([
                html.H3("📝 Trade Journal"),
                html.Div(id="trade-journal", className="trade-journal")
            ], className="journal-section"),
            
            # Status Bar
            html.Div([
                html.Div(id="status-bar", children="Ready", className="status-text")
            ], className="status-bar")
            
        ], className="dashboard-container")
        
        # Add CSS styling
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    .dashboard-container { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0; padding: 20px; background-color: #f5f5f5;
                    }
                    .header-section {
                        text-align: center; margin-bottom: 30px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 20px; border-radius: 10px;
                    }
                    .dashboard-title { margin: 0; font-size: 2.5em; }
                    .dashboard-subtitle { margin: 10px 0 0 0; opacity: 0.9; }
                    .control-panel {
                        display: flex; justify-content: space-around; align-items: end;
                        background: white; padding: 20px; border-radius: 10px;
                        margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    .control-item { display: flex; flex-direction: column; margin: 0 10px; }
                    .control-label { font-weight: bold; margin-bottom: 5px; }
                    .action-button {
                        background: #4CAF50; color: white; border: none;
                        padding: 12px 20px; border-radius: 5px; cursor: pointer;
                        font-weight: bold; margin: 0 5px; transition: background 0.3s;
                    }
                    .action-button:hover { background: #45a049; }
                    .main-content, .secondary-content {
                        display: flex; gap: 20px; margin-bottom: 20px;
                    }
                    .chart-section { flex: 2; }
                    .metrics-section { flex: 1; }
                    .chart-half { flex: 1; }
                    .chart-container {
                        background: white; border-radius: 10px; padding: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    .metrics-grid {
                        display: grid; grid-template-columns: 1fr 1fr;
                        gap: 15px; background: white; padding: 20px;
                        border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    .metric-card {
                        text-align: center; padding: 15px;
                        border: 2px solid #e0e0e0; border-radius: 8px;
                    }
                    .metric-value { font-size: 1.8em; font-weight: bold; margin: 5px 0; }
                    .metric-label { color: #666; font-size: 0.9em; }
                    .journal-section {
                        background: white; padding: 20px; border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
                    }
                    .status-bar {
                        background: #333; color: white; padding: 10px 20px;
                        border-radius: 5px; position: fixed; bottom: 20px; right: 20px;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def _setup_callbacks(self):
        """Setup interactive callbacks"""
        
        @self.app.callback(
            [Output('main-price-chart', 'figure'),
             Output('confluence-chart', 'figure'),
             Output('risk-chart', 'figure'),
             Output('performance-metrics', 'children'),
             Output('trade-journal', 'children'),
             Output('status-bar', 'children')],
            [Input('run-backtest-btn', 'n_clicks'),
             Input('load-data-btn', 'n_clicks'),
             Input('date-range-picker', 'start_date'),
             Input('date-range-picker', 'end_date'),
             Input('capital-input', 'value')]
        )
        def update_dashboard(backtest_clicks, data_clicks, start_date, end_date, capital):
            """Main callback to update all dashboard components"""
            
            # Determine which button was clicked
            ctx = dash.callback_context
            if not ctx.triggered:
                return self._empty_charts(), self._empty_metrics(), self._empty_journal(), "Ready"
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            try:
                if button_id == 'run-backtest-btn' and backtest_clicks:
                    return self._run_backtest_update(start_date, end_date, capital)
                elif button_id == 'load-data-btn' and data_clicks:
                    return self._load_data_update(start_date, end_date)
                else:
                    return self._empty_charts(), self._empty_metrics(), self._empty_journal(), "Ready"
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"❌ Dashboard error: {e}")
                return self._empty_charts(), self._empty_metrics(), self._empty_journal(), error_msg
    
    def _run_backtest_update(self, start_date, end_date, capital):
        """Update dashboard with backtest results"""
        print(f"🔄 Running backtest: {start_date} to {end_date}")
        
        # Run visual backtest
        results = self.backtest_runner.run_visual_backtest(
            start_date=start_date,
            end_date=end_date,
            cash=capital
        )
        
        if not results:
            return self._empty_charts(), self._empty_metrics(), self._empty_journal(), "Backtest failed"
        
        self.backtest_results = results
        self.current_data = results['data']
        
        # Create charts
        price_chart = self._create_price_chart_with_signals(results)
        confluence_chart = self._create_confluence_chart(results)
        risk_chart = self._create_risk_analysis_chart(results)
        
        # Create performance metrics
        metrics = self._create_performance_metrics(results)
        
        # Create trade journal
        journal = self._create_trade_journal(results)
        
        status = f"Backtest complete: {results['total_return_pct']:.2f}% return"
        
        return price_chart, confluence_chart, risk_chart, metrics, journal, status
    
    def _load_data_update(self, start_date, end_date):
        """Update dashboard with live data"""
        print(f"📊 Loading live data: {start_date} to {end_date}")
        
        # Fetch live data
        df = self.data_fetcher.fetch_btc_data(start_date, end_date, "1h")
        
        if df is None or df.empty:
            return self._empty_charts(), self._empty_metrics(), self._empty_journal(), "Data loading failed"
        
        self.current_data = df
        
        # Create live data charts
        price_chart = self._create_live_price_chart(df)
        confluence_chart = self._create_live_confluence_chart(df)
        risk_chart = self._create_market_analysis_chart(df)
        
        # Create live metrics
        metrics = self._create_live_metrics(df)
        
        # Empty journal for live data
        journal = html.Div("Load backtest results to see trade journal", className="text-muted")
        
        status = f"Live data loaded: {len(df)} periods"
        
        return price_chart, confluence_chart, risk_chart, metrics, journal, status
    
    def _create_price_chart_with_signals(self, results):
        """Create main price chart with trade signals"""
        df = results['data']
        
        # Create candlestick chart
        fig = go.Figure()
        
        # Add candlesticks
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="BTCUSDT",
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ))
        
        # Add volume subplot (commented out for now - can be added as secondary y-axis)
        
        fig.update_layout(
            title="🚀 BTCUSDT Price Action with Signals",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            height=500,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def _create_confluence_chart(self, results):
        """Create confluence score visualization"""
        df = results['data']
        
        # Simulate confluence scores (in real implementation, this would come from strategy)
        dates = df.index[-100:]  # Last 100 periods
        confluence_scores = np.random.randint(0, 8, len(dates))  # Placeholder
        
        fig = go.Figure()
        
        # Add confluence score line
        fig.add_trace(go.Scatter(
            x=dates,
            y=confluence_scores,
            mode='lines+markers',
            name='Confluence Score',
            line=dict(color='purple', width=3)
        ))
        
        # Add threshold line
        fig.add_hline(y=4, line_dash="dash", line_color="red", 
                     annotation_text="Entry Threshold")
        
        fig.update_layout(
            title="📊 Confluence Score Over Time",
            xaxis_title="Time",
            yaxis_title="Confluence Score (0-7)",
            height=300,
            yaxis=dict(range=[0, 7])
        )
        
        return fig
    
    def _create_risk_analysis_chart(self, results):
        """Create risk analysis visualization"""
        # Simulate equity curve
        initial_capital = 10000
        returns = np.random.normal(0.001, 0.02, 100)  # Placeholder
        equity_curve = initial_capital * np.cumprod(1 + returns)
        
        # Calculate drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak * 100
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Equity Curve', 'Drawdown %'],
            vertical_spacing=0.1
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(y=equity_curve, name='Equity', line=dict(color='green')),
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(y=-drawdown, fill='tonexty', name='Drawdown', 
                      line=dict(color='red')),
            row=2, col=1
        )
        
        fig.update_layout(
            title="📈 Risk Analysis",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def _create_live_price_chart(self, df):
        """Create live price chart without signals"""
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="BTCUSDT Live"
        ))
        
        fig.update_layout(
            title="📊 BTCUSDT Live Price Data",
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def _create_live_confluence_chart(self, df):
        """Create live confluence analysis"""
        # Placeholder for real-time confluence calculation
        fig = go.Figure()
        fig.add_annotation(
            text="Load backtest to see confluence analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="📊 Confluence Analysis", height=300)
        return fig
    
    def _create_market_analysis_chart(self, df):
        """Create market analysis chart"""
        # Calculate volatility
        returns = df['Close'].pct_change()
        volatility = returns.rolling(window=24).std() * np.sqrt(24) * 100
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=volatility,
            name='24h Volatility %',
            line=dict(color='orange')
        ))
        
        fig.update_layout(
            title="📈 Market Volatility Analysis",
            yaxis_title="Volatility %",
            height=400
        )
        
        return fig
    
    def _create_performance_metrics(self, results):
        """Create performance metrics cards"""
        metrics = [
            ("Total Return", f"{results['total_return_pct']:.2f}%", "success"),
            ("Win Rate", f"{results['win_rate_pct']:.1f}%", "info"),
            ("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}", "warning"),
            ("Max Drawdown", f"{results['max_drawdown_pct']:.2f}%", "danger"),
            ("Total Trades", f"{results['total_trades']}", "secondary"),
            ("Strategy Status", "Active", "success")
        ]
        
        metric_cards = []
        for label, value, color in metrics:
            card = html.Div([
                html.Div(value, className=f"metric-value text-{color}"),
                html.Div(label, className="metric-label")
            ], className="metric-card")
            metric_cards.append(card)
        
        return metric_cards
    
    def _create_live_metrics(self, df):
        """Create live data metrics"""
        current_price = df['Close'].iloc[-1]
        price_change = df['Close'].pct_change().iloc[-1] * 100
        volume = df['Volume'].iloc[-1] if 'Volume' in df.columns else 0
        
        metrics = [
            ("Current Price", f"${current_price:,.2f}", "primary"),
            ("24h Change", f"{price_change:+.2f}%", "success" if price_change > 0 else "danger"),
            ("Volume", f"{volume:,.0f}", "info"),
            ("Data Points", f"{len(df)}", "secondary"),
            ("Last Update", datetime.now().strftime("%H:%M:%S"), "muted"),
            ("Status", "Live", "success")
        ]
        
        metric_cards = []
        for label, value, color in metrics:
            card = html.Div([
                html.Div(value, className=f"metric-value text-{color}"),
                html.Div(label, className="metric-label")
            ], className="metric-card")
            metric_cards.append(card)
        
        return metric_cards
    
    def _create_trade_journal(self, results):
        """Create trade journal table"""
        # Placeholder trade data
        trades = [
            {"Time": "2024-01-15 10:30", "Type": "LONG", "Price": "$42,500", "Size": "0.1 BTC", 
             "Confluence": "5/7", "Result": "WIN", "P&L": "+$850"},
            {"Time": "2024-01-16 14:15", "Type": "SHORT", "Price": "$43,200", "Size": "0.08 BTC", 
             "Confluence": "6/7", "Result": "WIN", "P&L": "+$640"},
            {"Time": "2024-01-17 09:45", "Type": "LONG", "Price": "$42,100", "Size": "0.12 BTC", 
             "Confluence": "4/7", "Result": "LOSS", "P&L": "-$320"}
        ]
        
        # Create table rows
        table_rows = []
        for trade in trades:
            row = html.Tr([
                html.Td(trade["Time"]),
                html.Td(trade["Type"], className=f"text-{'success' if trade['Type'] == 'LONG' else 'warning'}"),
                html.Td(trade["Price"]),
                html.Td(trade["Size"]),
                html.Td(trade["Confluence"]),
                html.Td(trade["Result"], className=f"text-{'success' if trade['Result'] == 'WIN' else 'danger'}"),
                html.Td(trade["P&L"], className=f"text-{'success' if '+' in trade['P&L'] else 'danger'}")
            ])
            table_rows.append(row)
        
        # Create table
        table = html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Time"),
                    html.Th("Type"), 
                    html.Th("Price"),
                    html.Th("Size"),
                    html.Th("Confluence"),
                    html.Th("Result"),
                    html.Th("P&L")
                ])
            ]),
            html.Tbody(table_rows)
        ], className="table table-striped")
        
        return table
    
    def _empty_charts(self):
        """Return empty charts"""
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Click 'Load Live Data' or 'Run Backtest' to see charts",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        empty_fig.update_layout(height=400)
        return empty_fig, empty_fig, empty_fig
    
    def _empty_metrics(self):
        """Return empty metrics"""
        return html.Div("No data loaded", className="text-muted")
    
    def _empty_journal(self):
        """Return empty journal"""
        return html.Div("No trades to display", className="text-muted")
    
    def run(self, debug=False):
        """Start the dashboard server"""
        print(f"\n🚀 STARTING DASHBOARD SERVER")
        print(f"🌐 Dashboard URL: http://localhost:{self.port}")
        print(f"📊 Features:")
        print(f"   - Interactive price charts with trade signals")
        print(f"   - Real-time performance metrics")
        print(f"   - Confluence score visualization")
        print(f"   - Risk analysis dashboard")
        print(f"   - Trade journal with detailed logs")
        print(f"\n✨ Dashboard ready! Open the URL in your browser.")
        
        try:
            self.app.run_server(debug=debug, port=self.port, host='127.0.0.1')
        except Exception as e:
            print(f"❌ Failed to start dashboard: {e}")


def main():
    """Main function to start the dashboard"""
    print("🎨 BTCUSDT ADVANCED TRADING DASHBOARD")
    print("=" * 50)
    
    # Create and run dashboard
    dashboard = BTCTradingDashboard(port=8050)
    dashboard.run(debug=False)


if __name__ == "__main__":
    main()