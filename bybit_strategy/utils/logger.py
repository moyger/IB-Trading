"""
Logging utilities for the Bybit strategy
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
import json
import csv
from typing import Dict, Any

class StrategyLogger:
    """Custom logger for trading strategy"""
    
    def __init__(self, log_dir: str = 'logs', log_level: str = 'INFO'):
        """Initialize logger"""
        
        # Create log directory
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up main logger
        self.logger = logging.getLogger('BybitStrategy')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = self.log_dir / f"strategy_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s | %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Trade logger (CSV)
        self.trade_log = self.log_dir / 'trades.csv'
        self._init_trade_log()
        
        # Signal logger (JSON)
        self.signal_log = self.log_dir / 'signals.json'
        
        # Performance logger
        self.performance_log = self.log_dir / 'performance.json'
    
    def _init_trade_log(self):
        """Initialize trade log CSV"""
        if not self.trade_log.exists():
            with open(self.trade_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'symbol', 'side', 'entry_price', 'exit_price',
                    'size', 'pnl', 'pnl_pct', 'duration_hours', 'strategy'
                ])
    
    def log_trade(self, trade: Dict[str, Any]):
        """Log a completed trade"""
        with open(self.trade_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade.get('timestamp', datetime.now().isoformat()),
                trade.get('symbol'),
                trade.get('side'),
                trade.get('entry_price'),
                trade.get('exit_price'),
                trade.get('size'),
                trade.get('pnl'),
                trade.get('pnl_pct'),
                trade.get('duration_hours'),
                trade.get('strategy', 'Bybit_1H_Trend')
            ])
    
    def log_signal(self, signal: Dict[str, Any]):
        """Log a trading signal"""
        signal_data = {
            'timestamp': datetime.now().isoformat(),
            **signal
        }
        
        # Read existing signals
        signals = []
        if self.signal_log.exists():
            with open(self.signal_log, 'r') as f:
                try:
                    signals = json.load(f)
                except:
                    signals = []
        
        # Append new signal
        signals.append(signal_data)
        
        # Write back
        with open(self.signal_log, 'w') as f:
            json.dump(signals, f, indent=2)
    
    def log_performance(self, metrics: Dict[str, Any]):
        """Log performance metrics"""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            **metrics
        }
        
        # Read existing performance data
        performance = []
        if self.performance_log.exists():
            with open(self.performance_log, 'r') as f:
                try:
                    performance = json.load(f)
                except:
                    performance = []
        
        # Append new metrics
        performance.append(perf_data)
        
        # Keep only last 1000 entries
        performance = performance[-1000:]
        
        # Write back
        with open(self.performance_log, 'w') as f:
            json.dump(performance, f, indent=2)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

# Global logger instance
logger = StrategyLogger()