#!/usr/bin/env python3
"""
Cloudflare Worker Configuration for FTMO 1H Enhanced Strategy
Production webhook configuration using your existing Cloudflare Worker
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class CloudflareWebhookConfig:
    """Cloudflare Worker webhook configuration"""
    
    # Your Cloudflare Worker endpoints
    base_url: str = "https://tradingview-webhook.karloestrada.workers.dev"
    enqueue_endpoint: str = "/enqueue"
    dequeue_endpoint: str = "/dequeue"
    status_endpoint: str = "/status"
    
    # Authentication (required for /enqueue)
    webhook_secret: str = "k9P$Xz83!vW@b12N#rTe"  # Add to request body as "token"
    account_key: str = "FTMO_1H_LIVE"
    
    # Request settings
    timeout_seconds: int = 10
    retry_attempts: int = 3
    retry_delay: int = 5
    
    # Headers
    def get_headers(self):
        """Get request headers with authentication if needed"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'FTMO-1H-Enhanced/1.0'
        }
        
        # Add authentication if token is set
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
            # Or if using custom header:
            # headers['X-API-Token'] = self.api_token
        
        return headers
    
    def get_enqueue_url(self):
        """Get full enqueue URL"""
        return f"{self.base_url}{self.enqueue_endpoint}"
    
    def get_dequeue_url(self, account=None):
        """Get full dequeue URL with optional account parameter"""
        url = f"{self.base_url}{self.dequeue_endpoint}"
        if account:
            url += f"?account={account}"
        return url
    
    def get_status_url(self):
        """Get full status URL"""
        return f"{self.base_url}{self.status_endpoint}"

@dataclass
class CloudflareFTMOConfig:
    """Complete configuration for Cloudflare Worker + FTMO"""
    
    # FTMO Settings
    account_size: int = 100000
    challenge_phase: int = 1
    max_daily_risk: float = 1.5
    emergency_daily_limit: float = 0.8
    overall_emergency_limit: float = 5.0
    
    # Trading Settings
    symbol: str = "XAUUSD"
    timeframe: str = "1H"
    min_trend_strength: float = 3.0
    signal_cooldown: int = 300  # seconds
    max_daily_signals: int = 10
    max_daily_trades: int = 15
    
    # Position Sizing
    base_risk_pct: float = 1.25  # 1H Enhanced standard
    atr_stop_multiplier: float = 2.0
    atr_target_multiplier: float = 3.0
    
    # Webhook Configuration
    webhook: CloudflareWebhookConfig = None
    
    def __post_init__(self):
        if self.webhook is None:
            self.webhook = CloudflareWebhookConfig()

# Pre-configured setups
class CloudflarePresets:
    """Ready-to-use configurations for different scenarios"""
    
    @staticmethod
    def production():
        """Production configuration with Cloudflare Worker"""
        config = CloudflareFTMOConfig()
        config.webhook = CloudflareWebhookConfig(
            account_key="FTMO_PROD",
            api_token=os.getenv('CLOUDFLARE_API_TOKEN')  # Set via environment variable
        )
        return config
    
    @staticmethod
    def testing():
        """Testing configuration"""
        config = CloudflareFTMOConfig()
        config.account_size = 10000
        config.webhook = CloudflareWebhookConfig(
            account_key="FTMO_TEST"
        )
        config.min_trend_strength = 2.0  # Lower for more signals in testing
        return config
    
    @staticmethod
    def conservative():
        """Conservative production settings"""
        config = CloudflareFTMOConfig()
        config.webhook = CloudflareWebhookConfig(
            account_key="FTMO_CONSERVATIVE"
        )
        config.max_daily_risk = 1.0
        config.emergency_daily_limit = 0.6
        config.base_risk_pct = 1.0
        config.min_trend_strength = 3.5
        config.signal_cooldown = 600  # 10 minutes
        return config

def test_cloudflare_connection(config: CloudflareWebhookConfig):
    """Test Cloudflare Worker connectivity"""
    import requests
    
    print("🔍 Testing Cloudflare Worker Connection")
    print(f"📡 URL: {config.base_url}")
    
    try:
        # Test status endpoint (if it exists)
        status_url = config.get_status_url()
        response = requests.get(
            status_url,
            headers=config.get_headers(),
            timeout=config.timeout_seconds
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Cloudflare Worker is accessible")
            try:
                data = response.json()
                print(f"📊 Worker Status: {data}")
            except:
                print(f"📄 Response: {response.text}")
            return True
        elif response.status_code == 404:
            print("⚠️ Status endpoint not found (might be normal)")
            # Try enqueue endpoint with GET to test
            test_url = config.get_enqueue_url()
            test_response = requests.get(
                test_url,
                headers=config.get_headers(),
                timeout=config.timeout_seconds
            )
            print(f"Enqueue endpoint test: {test_response.status_code}")
            return test_response.status_code in [200, 405]  # 405 = Method not allowed (GET on POST endpoint)
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Test Cloudflare Worker configuration"""
    print("🌐 CLOUDFLARE WORKER CONFIGURATION")
    print("=" * 60)
    
    # Test with different presets
    configs = {
        "Production": CloudflarePresets.production(),
        "Testing": CloudflarePresets.testing(),
        "Conservative": CloudflarePresets.conservative()
    }
    
    for name, config in configs.items():
        print(f"\n📊 {name} Configuration:")
        print(f"  Account: {config.webhook.account_key}")
        print(f"  URL: {config.webhook.base_url}")
        print(f"  Auth: {'Yes' if config.webhook.api_token else 'No'}")
        print(f"  Risk: {config.max_daily_risk}%")
        print(f"  Signals: {config.max_daily_signals}/day")
    
    print("\n" + "=" * 60)
    print("🧪 Testing Connection...")
    
    # Test default configuration
    test_config = CloudflareWebhookConfig()
    success = test_cloudflare_connection(test_config)
    
    if success:
        print("\n✅ Ready to use Cloudflare Worker!")
        print("\n📝 Next Steps:")
        print("1. Set CLOUDFLARE_API_TOKEN environment variable (if auth required)")
        print("2. Update xauusd_ftmo_1h_live_trader.py to use cloudflare_config")
        print("3. Test with: python xauusd_ftmo_1h_live_trader.py")
    else:
        print("\n⚠️ Connection test failed - check configuration")

if __name__ == "__main__":
    main()