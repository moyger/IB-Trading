"""
Reporting Module
===============

Professional reporting with HTML, PDF, and Markdown generation.

Components:
-----------
- ReportGenerator: Main report generation engine
- HTMLReportGenerator: Interactive HTML reports with Plotly
- PDFReportGenerator: Professional PDF reports
- MarkdownReportGenerator: Markdown documentation
- PerformanceReporter: Performance analytics reporting

Example:
--------
```python
from edgerunner.reports import ReportGenerator

reporter = ReportGenerator(output_dir="reports")
reporter.generate_html_report(backtest_results)
reporter.generate_pdf_summary(portfolio_metrics)
```
"""

from .generator import ReportGenerator
from .html_generator import HTMLReportGenerator
from .pdf_generator import PDFReportGenerator
from .markdown_generator import MarkdownReportGenerator
from .performance_reporter import PerformanceReporter

__all__ = [
    "ReportGenerator",
    "HTMLReportGenerator",
    "PDFReportGenerator",
    "MarkdownReportGenerator",
    "PerformanceReporter"
]