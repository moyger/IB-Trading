#!/usr/bin/env python3
"""
Webhook Manager for Edgerunner Framework
Integrates existing Cloudflare Worker and local webhook infrastructure
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import threading
from flask import Flask, request, jsonify

from ..utils.config import Config


@dataclass
class WebhookConfig:
    """Webhook configuration"""
    name: str
    base_url: str
    enqueue_endpoint: str = "/enqueue"
    dequeue_endpoint: str = "/dequeue"
    status_endpoint: str = "/status"
    webhook_secret: str = ""
    timeout_seconds: int = 10
    retry_attempts: int = 3
    
    def get_enqueue_url(self) -> str:
        return f"{self.base_url}{self.enqueue_endpoint}"
    
    def get_dequeue_url(self) -> str:
        return f"{self.base_url}{self.dequeue_endpoint}"
    
    def get_status_url(self) -> str:
        return f"{self.base_url}{self.status_endpoint}"


class WebhookManager:
    """
    Manages webhook integrations for MT5 and other external systems
    Integrates existing Cloudflare Worker and local webhook server
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Webhook configurations
        self.webhooks = {}
        self.webhook_health = {}
        
        # Signal tracking
        self.signal_queue = []
        self.signal_history = []
        self.active_signals = {}
        
        # Local webhook server
        self.local_server = None
        self.local_server_thread = None
        
        # Initialize webhooks
        self._initialize_webhooks()
        
        self.logger.info("Webhook Manager initialized")
    
    def _initialize_webhooks(self):
        """Initialize webhook configurations"""
        webhook_config = self.config.get('webhooks', {})
        
        # Cloudflare Webhook
        if webhook_config.get('cloudflare_webhook', {}).get('enabled', False):
            cf_config = webhook_config['cloudflare_webhook']
            
            self.webhooks['cloudflare'] = WebhookConfig(
                name='cloudflare',
                base_url=cf_config['base_url'],
                enqueue_endpoint=cf_config['endpoints']['enqueue'],
                dequeue_endpoint=cf_config['endpoints']['dequeue'],
                status_endpoint=cf_config['endpoints']['status'],
                webhook_secret=cf_config.get('webhook_secret', ''),
                timeout_seconds=cf_config.get('timeout_seconds', 10),
                retry_attempts=cf_config.get('retry_attempts', 3)
            )
            
            self.webhook_health['cloudflare'] = {'status': 'unknown', 'last_check': None}
            self.logger.info("Cloudflare webhook configured")
        
        # Local Webhook
        if webhook_config.get('local_webhook', {}).get('enabled', False):
            local_config = webhook_config['local_webhook']
            
            local_url = f"http://{local_config['host']}:{local_config['port']}"
            self.webhooks['local'] = WebhookConfig(
                name='local',
                base_url=local_url,
                timeout_seconds=5
            )
            
            self.webhook_health['local'] = {'status': 'unknown', 'last_check': None}
            self.logger.info("Local webhook configured")
    
    def start_local_webhook_server(self, host='0.0.0.0', port=5000):
        """Start local webhook server in background thread"""
        if self.local_server_thread and self.local_server_thread.is_alive():
            self.logger.warning("Local webhook server already running")
            return True
        
        try:
            # Initialize Flask app
            app = Flask(__name__)
            
            @app.route('/')
            def home():
                return jsonify({
                    "service": "Edgerunner Webhook Server",
                    "status": "running",
                    "version": "1.0",
                    "endpoints": {
                        "webhook": "/webhook",
                        "enqueue": "/enqueue", 
                        "dequeue": "/dequeue",
                        "status": "/status"
                    }
                })
            
            @app.route('/webhook', methods=['POST'])
            @app.route('/enqueue', methods=['POST'])
            def receive_signal():
                try:
                    signal_data = request.json
                    if not signal_data:
                        return jsonify({"error": "No data received"}), 400
                    
                    # Add signal to queue
                    signal_id = self._add_signal_to_queue(signal_data)
                    
                    return jsonify({
                        "ok": True,
                        "signal_id": signal_id,
                        "status": "queued",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    self.logger.error(f"Local webhook error: {e}")
                    return jsonify({"error": str(e)}), 500
            
            @app.route('/dequeue', methods=['GET'])
            def dequeue_signal():
                try:
                    account = request.args.get('account', 'DEFAULT')
                    
                    if self.signal_queue:
                        signal = self.signal_queue.pop(0)
                        self.logger.info(f"Signal dequeued for {account}: {signal.get('signalId', 'unknown')}")
                        return jsonify(signal)
                    else:
                        return jsonify({"message": "No signals available"}), 204
                        
                except Exception as e:
                    self.logger.error(f"Dequeue error: {e}")
                    return jsonify({"error": str(e)}), 500
            
            @app.route('/status')
            def status():
                return jsonify({
                    "status": "running",
                    "queue_size": len(self.signal_queue),
                    "total_signals": len(self.signal_history),
                    "active_signals": len(self.active_signals),
                    "uptime": time.time()
                })
            
            # Start server in background thread
            def run_server():
                try:
                    app.run(host=host, port=port, debug=False, use_reloader=False)
                except Exception as e:
                    self.logger.error(f"Local webhook server error: {e}")
            
            self.local_server_thread = threading.Thread(target=run_server, daemon=True)
            self.local_server_thread.start()
            
            # Give server time to start
            time.sleep(2)
            
            self.logger.info(f"Local webhook server started on {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start local webhook server: {e}")
            return False
    
    def _add_signal_to_queue(self, signal_data: Dict) -> str:
        """Add signal to internal queue"""
        signal_id = signal_data.get('signalId', f"signal_{int(time.time())}")
        
        processed_signal = {
            **signal_data,
            'signalId': signal_id,
            'timestamp': datetime.now().isoformat(),
            'received_at': time.time(),
            'status': 'queued'
        }
        
        self.signal_queue.append(processed_signal)
        self.signal_history.append(processed_signal)
        
        if signal_data.get('event') == 'entry':
            self.active_signals[signal_id] = processed_signal
        elif signal_data.get('event') == 'exit':
            original_id = signal_data.get('original_signal_id')
            if original_id in self.active_signals:
                del self.active_signals[original_id]
        
        self.logger.info(f"Signal added to queue: {signal_id}")
        return signal_id
    
    def send_signal(self, signal_data: Dict, webhook_name: str = None) -> bool:
        """
        Send signal to webhook endpoint
        
        Args:
            signal_data: Signal payload
            webhook_name: Specific webhook to use (default: cloudflare)
            
        Returns:
            Success status
        """
        webhook_name = webhook_name or 'cloudflare'
        
        if webhook_name not in self.webhooks:
            self.logger.error(f"Webhook {webhook_name} not configured")
            return False
        
        webhook = self.webhooks[webhook_name]
        
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Edgerunner/1.0'
            }
            
            # Add authentication if configured
            if webhook.webhook_secret:
                signal_data['token'] = webhook.webhook_secret
            
            # Send request with retries
            for attempt in range(webhook.retry_attempts):
                try:
                    response = requests.post(
                        webhook.get_enqueue_url(),
                        json=signal_data,
                        headers=headers,
                        timeout=webhook.timeout_seconds
                    )
                    
                    if response.status_code == 200:
                        self.logger.info(f"Signal sent via {webhook_name}: {signal_data.get('signalId', 'unknown')}")
                        self._update_webhook_health(webhook_name, True)
                        
                        # Track signal locally
                        self._add_signal_to_queue(signal_data)
                        
                        return True
                    else:
                        self.logger.warning(f"Signal failed via {webhook_name}: {response.status_code} - {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
                    if attempt < webhook.retry_attempts - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            # All attempts failed
            self._update_webhook_health(webhook_name, False)
            self.logger.error(f"All webhook attempts failed for {webhook_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Webhook send error: {e}")
            self._update_webhook_health(webhook_name, False)
            return False
    
    def _update_webhook_health(self, webhook_name: str, success: bool):
        """Update webhook health status"""
        if webhook_name in self.webhook_health:
            self.webhook_health[webhook_name] = {
                'status': 'healthy' if success else 'unhealthy',
                'last_check': datetime.now().isoformat(),
                'success': success
            }
    
    def check_webhook_health(self) -> Dict[str, Any]:
        """Check health of all configured webhooks"""
        health_results = {}
        
        for name, webhook in self.webhooks.items():
            try:
                # Test with status endpoint or basic connectivity
                response = requests.get(
                    webhook.get_status_url(),
                    timeout=webhook.timeout_seconds
                )
                
                healthy = response.status_code in [200, 404]  # 404 might be normal if status endpoint doesn't exist
                
                if not healthy and response.status_code == 404:
                    # Try enqueue endpoint with GET to test connectivity
                    test_response = requests.get(
                        webhook.get_enqueue_url(),
                        timeout=webhook.timeout_seconds
                    )
                    healthy = test_response.status_code in [200, 405]  # 405 = Method not allowed (normal)
                
                health_results[name] = {
                    'status': 'healthy' if healthy else 'unhealthy',
                    'response_code': response.status_code,
                    'last_check': datetime.now().isoformat()
                }
                
                self._update_webhook_health(name, healthy)
                
            except Exception as e:
                health_results[name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
                self._update_webhook_health(name, False)
        
        return health_results
    
    def get_routing_config(self) -> Dict[str, Any]:
        """Get webhook routing configuration"""
        routing_config = self.config.get('webhooks', {}).get('routing', {})
        
        return {
            'strategy_routing': routing_config.get('strategy_routing', {}),
            'fallback': routing_config.get('fallback', {}),
            'default_webhook': routing_config.get('fallback', {}).get('primary', 'cloudflare')
        }
    
    def route_signal(self, signal_data: Dict, strategy_name: str = None) -> bool:
        """
        Route signal to appropriate webhook based on strategy
        
        Args:
            signal_data: Signal payload
            strategy_name: Name of strategy (for routing)
            
        Returns:
            Success status
        """
        routing = self.get_routing_config()
        
        # Determine webhook to use
        webhook_name = None
        
        if strategy_name and strategy_name in routing['strategy_routing']:
            strategy_config = routing['strategy_routing'][strategy_name]
            webhook_name = strategy_config.get('webhook')
        
        # Use fallback if no specific routing
        if not webhook_name:
            webhook_name = routing.get('default_webhook', 'cloudflare')
        
        # Send signal
        success = self.send_signal(signal_data, webhook_name)
        
        # Try fallback if primary fails
        if not success and routing.get('fallback', {}).get('retry_on_failure', False):
            fallback_webhook = routing.get('fallback', {}).get('secondary')
            if fallback_webhook and fallback_webhook != webhook_name:
                self.logger.info(f"Trying fallback webhook: {fallback_webhook}")
                success = self.send_signal(signal_data, fallback_webhook)
        
        return success
    
    def get_signal_queue_status(self) -> Dict[str, Any]:
        """Get current signal queue status"""
        return {
            'queue_size': len(self.signal_queue),
            'history_count': len(self.signal_history),
            'active_signals': len(self.active_signals),
            'queue_signals': [s.get('signalId', 'unknown') for s in self.signal_queue[-10:]],  # Last 10
            'active_signal_ids': list(self.active_signals.keys())
        }
    
    def stop(self):
        """Stop webhook manager and local server"""
        self.logger.info("Stopping webhook manager...")
        
        # Local server runs in daemon thread, will stop when main program exits
        if self.local_server_thread and self.local_server_thread.is_alive():
            self.logger.info("Local webhook server will stop with main process")
        
        self.logger.info("Webhook manager stopped")