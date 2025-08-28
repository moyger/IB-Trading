"""
Report Generation System

Professional report generation with markdown, JSON, and HTML export
for strategy backtesting results.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
import logging

try:
    from .html_generator import HTMLReportGenerator
    HTML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"HTML generator not available: {e}")
    HTML_AVAILABLE = False


class ReportGenerator:
    """
    Professional report generator for backtesting results.
    
    Generates comprehensive reports in multiple formats:
    - Markdown for documentation
    - JSON for programmatic access
    - HTML for web viewing (future)
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize HTML generator if available
        if HTML_AVAILABLE:
            self.html_generator = HTMLReportGenerator(output_dir)
        else:
            self.html_generator = None
        
        # Report templates
        self.templates = {
            'single_strategy': self._single_strategy_template,
            'multi_asset': self._multi_asset_template,
            'optimization': self._optimization_template,
            'comparison': self._comparison_template
        }
    
    def generate_single_strategy_report(self, results: Dict[str, Any], 
                                      filename: Optional[str] = None) -> str:
        """
        Generate report for single strategy backtest.
        
        Args:
            results: Backtest results dictionary
            filename: Custom filename (optional)
            
        Returns:
            Path to generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            strategy_name = results['strategy']['name'].lower().replace(' ', '_')
            symbol = results['symbol'].replace('-', '').lower()
            filename = f"{strategy_name}_{symbol}_{timestamp}"
        
        # Generate markdown report
        markdown_content = self._generate_markdown_report(results, 'single_strategy')
        markdown_path = self.output_dir / f"{filename}.md"
        
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        
        # Generate JSON report
        json_content = self._prepare_json_data(results)
        json_path = self.output_dir / f"{filename}.json"
        
        with open(json_path, 'w') as f:
            json.dump(json_content, f, indent=2, default=str)
        
        # Generate HTML report if available
        html_path = None
        if self.html_generator and 'portfolio' in results:
            try:
                html_path = self.html_generator.generate_strategy_report(results, f"{filename}.html")
                logging.info(f"HTML report generated: {html_path}")
            except Exception as e:
                logging.warning(f"HTML report generation failed: {e}")
        
        logging.info(f"Reports generated: {markdown_path}, {json_path}" + (f", and {html_path}" if html_path else ""))
        return str(markdown_path)
    
    def generate_comparison_report(self, results_list: List[Dict[str, Any]],
                                 comparison_title: str = "Strategy Comparison",
                                 filename: Optional[str] = None) -> str:
        """
        Generate comparison report for multiple strategies/configurations.
        
        Args:
            results_list: List of backtest results
            comparison_title: Title for comparison report
            filename: Custom filename (optional)
            
        Returns:
            Path to generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_comparison_{timestamp}"
        
        # Generate markdown comparison
        markdown_content = self._generate_comparison_markdown(results_list, comparison_title)
        markdown_path = self.output_dir / f"{filename}.md"
        
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        
        # Generate JSON data
        json_content = {
            'comparison_title': comparison_title,
            'strategies': [self._prepare_json_data(result) for result in results_list],
            'summary_table': self._create_comparison_table(results_list),
            'timestamp': datetime.now().isoformat()
        }
        
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump(json_content, f, indent=2, default=str)
        
        # Generate HTML comparison report if available
        html_path = None
        if self.html_generator and all('portfolio' in result for result in results_list if result):
            try:
                html_path = self.html_generator.generate_comparison_report(
                    results_list, comparison_title, f"{filename}.html"
                )
                logging.info(f"HTML comparison report generated: {html_path}")
            except Exception as e:
                logging.warning(f"HTML comparison report generation failed: {e}")
        
        logging.info(f"Comparison report generated: {markdown_path}" + (f" and {html_path}" if html_path else ""))
        return str(markdown_path)
    
    def _generate_markdown_report(self, results: Dict[str, Any], 
                                template_type: str) -> str:
        """Generate markdown report using templates"""
        template_func = self.templates.get(template_type, self._single_strategy_template)
        return template_func(results)
    
    def _single_strategy_template(self, results: Dict[str, Any]) -> str:
        """Markdown template for single strategy report"""
        strategy = results['strategy']
        performance = results['performance']
        
        # Format monthly summaries
        monthly_table = self._format_monthly_table(results.get('monthly_summaries', []))
        
        # Format trade analysis
        trade_analysis = results.get('trade_analysis', {})
        
        # Risk metrics
        risk_metrics = results.get('risk_metrics', {})
        
        markdown = f"""# {strategy['name']} - Backtest Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Strategy**: {strategy['name']}  
**Symbol**: {results['symbol']}  
**Period**: {results['period']}  
**Asset Type**: {strategy['asset_type'].title()}  
**Risk Profile**: {strategy['risk_profile'].title()}

---

## Executive Summary

**Total Return**: {performance['total_return']:.2f}%  
**Annualized Return**: {performance['annualized_return']:.2f}%  
**Maximum Drawdown**: {performance['max_drawdown']:.2f}%  
**Sharpe Ratio**: {performance['sharpe_ratio']:.2f}  
**Win Rate**: {performance['win_rate']:.1f}%

---

## Performance Metrics

### Return Metrics
- **Total Return**: {performance['total_return']:.2f}%
- **Annualized Return**: {performance['annualized_return']:.2f}%
- **CAGR**: {performance['cagr']:.2f}%

### Risk Metrics  
- **Volatility**: {performance['volatility']:.2f}%
- **Maximum Drawdown**: {performance['max_drawdown']:.2f}%
- **VaR (95%)**: {performance['var_95']:.2f}%
- **VaR (99%)**: {performance['var_99']:.2f}%
- **Expected Shortfall (95%)**: {performance['expected_shortfall_95']:.2f}%
- **Downside Deviation**: {performance['downside_deviation']:.2f}%

### Risk-Adjusted Metrics
- **Sharpe Ratio**: {performance['sharpe_ratio']:.2f}
- **Sortino Ratio**: {performance['sortino_ratio']:.2f}
- **Calmar Ratio**: {performance['calmar_ratio']:.2f}
- **Omega Ratio**: {performance['omega_ratio']:.2f}

---

## Trade Analysis

- **Total Trades**: {trade_analysis.get('total_trades', 0)}
- **Win Rate**: {performance['win_rate']:.1f}%
- **Profit Factor**: {performance['profit_factor']:.2f}
- **Average Trade Return**: {performance['avg_trade_return']:.2f}%
- **Best Trade**: {performance['best_trade']:.2f}%
- **Worst Trade**: {performance['worst_trade']:.2f}%
- **Average Trade Duration**: {performance['avg_trade_duration']:.1f} days
- **Max Consecutive Wins**: {performance['max_consecutive_wins']}
- **Max Consecutive Losses**: {performance['max_consecutive_losses']}

---

## Monthly Performance

{monthly_table}

---

## Strategy Configuration

### Risk Management
- **Risk per Trade**: {strategy['risk_per_trade']:.1%}
- **Max Daily Loss**: {strategy['max_daily_loss']:.1%}
- **Position Sizing**: {strategy['position_sizing'].title()}
- **FTMO Compliant**: {"Yes" if strategy['ftmo_compliant'] else "No"}

### Parameters
{self._format_parameters(strategy.get('parameters', {}))}

---

## Risk Analysis

### Distribution Metrics
- **Skewness**: {performance['skewness']:.2f}
- **Kurtosis**: {performance['kurtosis']:.2f}
- **Tail Ratio**: {performance['tail_ratio']:.2f}

### Consistency Metrics
- **Monthly Win Rate**: {performance['monthly_win_rate']:.1f}%
- **Recovery Factor**: {performance['recovery_factor']:.2f}

---

*Report generated using IB Trading Universal Backtesting Framework*  
*Built on VectorBT, Pandas, and NumPy for professional-grade analysis*
"""
        
        return markdown
    
    def _format_monthly_table(self, monthly_summaries: List[Dict[str, Any]]) -> str:
        """Format monthly summaries as markdown table"""
        if not monthly_summaries:
            return "No monthly data available."
        
        header = "| Month | Starting Balance | Ending Balance | P&L Amount | P&L % | Trades |\n"
        separator = "|-------|------------------|----------------|------------|-------|--------|\n"
        
        rows = []
        for month in monthly_summaries:
            emoji = "📈" if month['pnl'] > 0 else "📉"
            row = f"| {month['month']} | ${month['starting_balance']:,.0f} | ${month['ending_balance']:,.0f} | ${month['pnl']:+,.0f} | {month['pnl_pct']:+.2f}% | {month['trades']} {emoji} |"
            rows.append(row)
        
        return header + separator + '\n'.join(rows)
    
    def _format_parameters(self, params: Dict[str, Any]) -> str:
        """Format strategy parameters"""
        if not params:
            return "No custom parameters configured."
        
        formatted = []
        for key, value in params.items():
            formatted.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        
        return '\n'.join(formatted)
    
    def _generate_comparison_markdown(self, results_list: List[Dict[str, Any]], 
                                    title: str) -> str:
        """Generate comparison report in markdown"""
        
        # Create comparison table
        comparison_table = self._create_comparison_table(results_list)
        
        markdown = f"""# {title}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Strategies Compared**: {len(results_list)}

---

## Performance Comparison

{comparison_table}

---

## Detailed Analysis

"""
        
        # Add individual strategy summaries
        for i, result in enumerate(results_list, 1):
            strategy = result['strategy']
            performance = result['performance']
            
            markdown += f"""### {i}. {strategy['name']} ({result['symbol']})

**Return**: {performance['total_return']:.2f}% | **Max DD**: {performance['max_drawdown']:.2f}% | **Sharpe**: {performance['sharpe_ratio']:.2f} | **Win Rate**: {performance['win_rate']:.1f}%

"""
        
        markdown += "\n---\n\n*Generated using IB Trading Universal Backtesting Framework*"
        
        return markdown
    
    def _create_comparison_table(self, results_list: List[Dict[str, Any]]) -> str:
        """Create markdown comparison table"""
        if not results_list:
            return "No results to compare."
        
        # Table header
        header = "| Strategy | Symbol | Total Return | Max Drawdown | Sharpe | Win Rate | Total Trades |\n"
        separator = "|----------|--------|--------------|--------------|---------|----------|---------------|\n"
        
        # Table rows
        rows = []
        for result in results_list:
            strategy = result['strategy']
            performance = result['performance']
            
            row = (f"| {strategy['name']} | {result['symbol']} | "
                  f"{performance['total_return']:.2f}% | "
                  f"{performance['max_drawdown']:.2f}% | "
                  f"{performance['sharpe_ratio']:.2f} | "
                  f"{performance['win_rate']:.1f}% | "
                  f"{performance['total_trades']} |")
            rows.append(row)
        
        return header + separator + '\n'.join(rows)
    
    def _prepare_json_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare results data for JSON serialization"""
        # Remove non-serializable objects
        json_data = {}
        
        for key, value in results.items():
            if key in ['portfolio', 'portfolios']:
                continue  # Skip VectorBT objects
            
            # Convert numpy types
            if isinstance(value, np.ndarray):
                json_data[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                json_data[key] = float(value)
            elif isinstance(value, pd.Timestamp):
                json_data[key] = value.isoformat()
            elif isinstance(value, dict):
                json_data[key] = self._convert_dict_for_json(value)
            elif isinstance(value, list):
                json_data[key] = [self._convert_value_for_json(item) for item in value]
            else:
                json_data[key] = self._convert_value_for_json(value)
        
        return json_data
    
    def _convert_dict_for_json(self, d: Dict) -> Dict:
        """Recursively convert dictionary for JSON serialization"""
        converted = {}
        for key, value in d.items():
            converted[key] = self._convert_value_for_json(value)
        return converted
    
    def _convert_value_for_json(self, value: Any) -> Any:
        """Convert individual values for JSON serialization"""
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif isinstance(value, pd.Timestamp):
            return value.isoformat()
        elif isinstance(value, pd.Series):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._convert_dict_for_json(value)
        elif hasattr(value, '__dict__'):
            # Skip complex objects
            return str(value)
        else:
            return value
    
    def generate_optimization_report(self, optimization_results: Dict[str, Any],
                                   filename: Optional[str] = None) -> str:
        """Generate parameter optimization report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            strategy_name = optimization_results['strategy_class'].lower()
            filename = f"{strategy_name}_optimization_{timestamp}"
        
        markdown_content = self._optimization_template(optimization_results)
        markdown_path = self.output_dir / f"{filename}.md"
        
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        
        # Save detailed JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump(optimization_results, f, indent=2, default=str)
        
        return str(markdown_path)
    
    def _optimization_template(self, results: Dict[str, Any]) -> str:
        """Template for optimization results"""
        
        best_params = results.get('best_parameters', {})
        top_results = results.get('top_10_results', [])
        
        # Format parameter table
        param_table = self._format_optimization_table(top_results[:5])
        
        markdown = f"""# Parameter Optimization Report - {results['strategy_class']}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Strategy**: {results['strategy_class']}  
**Symbol**: {results['symbol']}  
**Optimization Metric**: {results['optimization_metric']}  
**Total Combinations Tested**: {results['total_combinations']}  
**Successful Combinations**: {results['successful_combinations']}

---

## Best Parameters

**Optimization Score**: {results.get('best_metric_value', 0):.4f}

{self._format_best_parameters(best_params)}

---

## Top 5 Parameter Sets

{param_table}

---

## Optimization Summary

- **Success Rate**: {(results['successful_combinations'] / results['total_combinations'] * 100):.1f}%
- **Best {results['optimization_metric'].title()}**: {results.get('best_metric_value', 0):.4f}
- **Parameter Ranges Tested**: {len(best_params)} parameters

### Parameter Sensitivity

The optimization tested the following parameter ranges:
{self._format_parameter_ranges(top_results)}

---

*Optimization powered by VectorBT for ultra-fast parameter sweeps*
"""
        
        return markdown
    
    def _format_optimization_table(self, top_results: List[Dict]) -> str:
        """Format optimization results table"""
        if not top_results:
            return "No optimization results available."
        
        header = "| Rank | Parameters | Metric Value | Total Return | Max Drawdown | Win Rate |\n"
        separator = "|------|------------|--------------|--------------|--------------|----------|\n"
        
        rows = []
        for i, result in enumerate(top_results, 1):
            params_str = ', '.join([f"{k}={v}" for k, v in result['parameters'].items()])
            if len(params_str) > 30:
                params_str = params_str[:27] + "..."
            
            row = (f"| {i} | {params_str} | "
                  f"{result['metric_value']:.3f} | "
                  f"{result['total_return']:.2f}% | "
                  f"{result['max_drawdown']:.2f}% | "
                  f"{result['win_rate']:.1f}% |")
            rows.append(row)
        
        return header + separator + '\n'.join(rows)
    
    def _format_best_parameters(self, params: Dict[str, Any]) -> str:
        """Format best parameters section"""
        if not params:
            return "No parameters available."
        
        formatted = []
        for key, value in params.items():
            formatted.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        
        return '\n'.join(formatted)
    
    def _format_parameter_ranges(self, results: List[Dict]) -> str:
        """Format parameter ranges from results"""
        if not results:
            return "No parameter information available."
        
        # Extract all unique parameters
        all_params = {}
        for result in results:
            for param, value in result['parameters'].items():
                if param not in all_params:
                    all_params[param] = []
                all_params[param].append(value)
        
        formatted = []
        for param, values in all_params.items():
            unique_values = sorted(set(values))
            if len(unique_values) > 5:
                range_str = f"{min(unique_values)} to {max(unique_values)} ({len(unique_values)} values)"
            else:
                range_str = ', '.join(map(str, unique_values))
            
            formatted.append(f"- **{param.replace('_', ' ').title()}**: {range_str}")
        
        return '\n'.join(formatted)
    
    def _multi_asset_template(self, results: Dict[str, Any]) -> str:
        """Template for multi-asset portfolio report"""
        # Placeholder for multi-asset template
        return self._single_strategy_template(results)
    
    def _comparison_template(self, results: Dict[str, Any]) -> str:
        """Template for strategy comparison report"""
        # Placeholder for comparison template
        return ""
    
    def export_to_csv(self, results: Dict[str, Any], 
                     filename: Optional[str] = None) -> str:
        """Export key metrics to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_metrics_{timestamp}.csv"
        
        # Extract key metrics
        performance = results['performance']
        strategy = results['strategy']
        
        metrics_df = pd.DataFrame([{
            'strategy': strategy['name'],
            'symbol': results['symbol'],
            'total_return': performance['total_return'],
            'annualized_return': performance['annualized_return'],
            'max_drawdown': performance['max_drawdown'],
            'sharpe_ratio': performance['sharpe_ratio'],
            'sortino_ratio': performance['sortino_ratio'],
            'win_rate': performance['win_rate'],
            'total_trades': performance['total_trades'],
            'profit_factor': performance['profit_factor'],
            'timestamp': results['timestamp']
        }])
        
        csv_path = self.output_dir / filename
        metrics_df.to_csv(csv_path, index=False)
        
        return str(csv_path)
    
    def create_summary_dashboard(self, results_list: List[Dict[str, Any]]) -> str:
        """Create executive summary dashboard"""
        if not results_list:
            return "No results to summarize."
        
        # Calculate summary statistics
        returns = [r['performance']['total_return'] for r in results_list]
        sharpes = [r['performance']['sharpe_ratio'] for r in results_list]
        drawdowns = [r['performance']['max_drawdown'] for r in results_list]
        
        summary = f"""# Executive Dashboard

## Portfolio Performance Summary

**Total Strategies Tested**: {len(results_list)}  
**Average Return**: {np.mean(returns):.2f}%  
**Best Performing Strategy**: {max(returns):.2f}%  
**Average Sharpe Ratio**: {np.mean(sharpes):.2f}  
**Average Max Drawdown**: {np.mean(drawdowns):.2f}%

## Top Performers

"""
        
        # Sort by total return and show top 3
        sorted_results = sorted(results_list, 
                               key=lambda x: x['performance']['total_return'], 
                               reverse=True)
        
        for i, result in enumerate(sorted_results[:3], 1):
            strategy = result['strategy']
            performance = result['performance']
            
            summary += f"""### {i}. {strategy['name']} ({result['symbol']})
- **Return**: {performance['total_return']:.2f}%
- **Sharpe**: {performance['sharpe_ratio']:.2f}
- **Max Drawdown**: {performance['max_drawdown']:.2f}%

"""
        
        return summary