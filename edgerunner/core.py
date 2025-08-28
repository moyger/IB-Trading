"""
Edgerunner Framework Core
========================

Main framework class that orchestrates all components.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .alpha import AlphaEngine
from .strategies import StrategyManager
from .execution import ExecutionEngine
from .brokers import BrokerManager
from .risk import RiskManager
from .backtest import BacktestEngine
from .monitor import MonitoringSystem
from .reports import ReportGenerator
from .utils import ConfigManager, Logger


class EdgerunnerFramework:
    """
    Main Edgerunner framework class.
    
    Provides unified interface to all trading system components.
    """
    
    def __init__(self, config_path: str = "config/", environment: str = "dev"):
        """
        Initialize Edgerunner framework.
        
        Args:
            config_path: Path to configuration directory
            environment: Environment (dev, prod, test)
        """
        self.config_path = Path(config_path)
        self.environment = environment
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing Edgerunner Framework v{self.__version__}")
        
        # Initialize components
        self._initialize_components()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML files."""
        config = {}
        
        # Load base configs
        config_files = [
            "brokers.yaml",
            "risk.yaml", 
            "strategy.yaml"
        ]
        
        for config_file in config_files:
            config_path = self.config_path / config_file
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config[config_file.replace('.yaml', '')] = yaml.safe_load(f)
        
        # Load environment-specific config
        env_config_path = self.config_path / "environments" / f"{self.environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                config['environment'] = yaml.safe_load(f)
                
        return config
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('environment', {}).get('logging', {})
        
        # Create logs directory
        log_file = log_config.get('file', 'logs/edgerunner.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if log_config.get('console', True) else logging.NullHandler()
            ]
        )
    
    def _initialize_components(self):
        """Initialize all framework components."""
        self.logger.info("Initializing framework components...")
        
        # Core components
        self.risk = RiskManager(self.config.get('risk', {}))
        self.brokers = BrokerManager(self.config.get('brokers', {}))
        self.alpha = AlphaEngine(self.config.get('strategy', {}))
        self.strategies = StrategyManager(self.config.get('strategy', {}))
        self.execution = ExecutionEngine(
            brokers=self.brokers,
            risk_manager=self.risk,
            config=self.config.get('brokers', {}).get('execution', {})
        )
        
        # Analysis and reporting
        self.backtest = BacktestEngine(self.config.get('strategy', {}).get('backtest', {}))
        self.reports = ReportGenerator(output_dir="reports")
        
        # Monitoring (only in production)
        if self.environment == 'prod':
            self.monitor = MonitoringSystem(self.config.get('environment', {}).get('monitoring', {}))
        else:
            self.monitor = None
            
        self.logger.info("All components initialized successfully")
    
    def start(self):
        """Start the trading framework."""
        self.logger.info("Starting Edgerunner Framework...")
        
        # Start monitoring if available
        if self.monitor:
            self.monitor.start()
            
        # Initialize broker connections
        self.brokers.connect_all()
        
        # Start strategy execution
        self.strategies.start_all()
        
        self.logger.info("Edgerunner Framework started successfully")
    
    def stop(self):
        """Stop the trading framework."""
        self.logger.info("Stopping Edgerunner Framework...")
        
        # Stop strategies
        self.strategies.stop_all()
        
        # Disconnect brokers
        self.brokers.disconnect_all()
        
        # Stop monitoring
        if self.monitor:
            self.monitor.stop()
            
        self.logger.info("Edgerunner Framework stopped")
    
    @property
    def __version__(self):
        """Get framework version."""
        from . import __version__
        return __version__
    
    def status(self) -> Dict[str, Any]:
        """Get framework status."""
        return {
            "version": self.__version__,
            "environment": self.environment,
            "brokers": self.brokers.status() if self.brokers else {},
            "strategies": self.strategies.status() if self.strategies else {},
            "risk": self.risk.status() if self.risk else {},
            "execution": self.execution.status() if self.execution else {}
        }