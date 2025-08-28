#!/usr/bin/env python3
"""
Edgerunner Quick Start Example
==============================

Demonstrates basic usage of the Edgerunner trading framework.
"""

from edgerunner import EdgerunnerFramework
import logging

def main():
    """Quick start example."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Edgerunner Quick Start Example")
    
    try:
        # Initialize framework
        logger.info("Initializing Edgerunner Framework...")
        framework = EdgerunnerFramework(
            config_path="config/",
            environment="dev"
        )
        
        # Check framework status
        status = framework.status()
        logger.info(f"Framework Status: {status}")
        
        # Start framework (in dev mode, this won't actually trade)
        logger.info("Starting framework...")
        framework.start()
        
        # Run a backtest
        logger.info("Running backtest for BTCUSDT FTMO strategy...")
        try:
            results = framework.backtest.run_strategy('btcusdt_ftmo')
            logger.info(f"Backtest completed. Results keys: {list(results.keys()) if results else 'No results'}")
        except Exception as e:
            logger.warning(f"Backtest failed (expected in quick start): {e}")
        
        # Generate a sample HTML report using our demo data
        logger.info("Generating sample HTML report...")
        try:
            # Use the existing HTML demo
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            from test_simple_html import generate_html_report, create_sample_data
            
            # Create sample data and generate report
            portfolio_series, drawdown, monthly_data = create_sample_data()
            html_content = generate_html_report(portfolio_series, drawdown, monthly_data)
            
            # Save to edgerunner reports directory
            os.makedirs("reports", exist_ok=True)
            report_path = "reports/edgerunner_quick_start_demo.html"
            
            with open(report_path, 'w') as f:
                f.write(html_content)
                
            logger.info(f"✅ Sample HTML report generated: {report_path}")
            logger.info("📊 Open the file in your browser to view interactive charts!")
            
        except Exception as e:
            logger.warning(f"HTML report generation failed: {e}")
        
        # Show some framework capabilities
        logger.info("🎯 Framework Capabilities:")
        logger.info("  ✅ Multi-broker support (IBKR, Bybit, MT5)")
        logger.info("  ✅ Advanced risk management with Kelly criterion")
        logger.info("  ✅ Multi-engine backtesting (VectorBT, backtesting.py)")
        logger.info("  ✅ Professional HTML/PDF reporting")
        logger.info("  ✅ Real-time monitoring and alerts")
        logger.info("  ✅ FTMO compliance for prop trading")
        
        # Stop framework
        logger.info("Stopping framework...")
        framework.stop()
        
        logger.info("✅ Quick start example completed successfully!")
        logger.info("Next steps:")
        logger.info("  1. Configure your broker credentials in .env")
        logger.info("  2. Customize strategy parameters in config/strategy.yaml")
        logger.info("  3. Run your first live backtest")
        logger.info("  4. Deploy to production with environment=prod")
        
    except Exception as e:
        logger.error(f"❌ Quick start failed: {e}")
        raise

if __name__ == "__main__":
    main()