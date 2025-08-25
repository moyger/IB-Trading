#!/usr/bin/env python3
"""
Local Webhook Server
Backup webhook server for FTMO 1H Enhanced Strategy
Runs locally to receive signals and forward to MT5
"""

from flask import Flask, request, jsonify
import json
import time
import uuid
from datetime import datetime
from collections import deque
import threading
import requests

app = Flask(__name__)

class LocalWebhookServer:
    """Local webhook server for signal processing"""
    
    def __init__(self, port=5000):
        self.port = port
        self.signal_queue = deque(maxlen=100)
        self.signal_history = []
        self.active_signals = {}
        self.mt5_bridge_url = None  # Can be set to forward to MT5 bridge
        
        print(f"🚀 LOCAL WEBHOOK SERVER INITIALIZED")
        print(f"📡 Port: {port}")
        print(f"🔗 Endpoint: http://localhost:{port}/webhook")
    
    def add_signal(self, signal_data):
        """Add signal to queue"""
        signal_id = signal_data.get('signalId', str(uuid.uuid4()))
        timestamp = datetime.now().isoformat()
        
        processed_signal = {
            'id': signal_id,
            'timestamp': timestamp,
            'received_at': time.time(),
            'data': signal_data,
            'status': 'queued'
        }
        
        self.signal_queue.append(processed_signal)
        self.signal_history.append(processed_signal)
        
        if signal_data.get('event') == 'entry':
            self.active_signals[signal_id] = processed_signal
        elif signal_data.get('event') == 'exit':
            # Remove from active signals
            original_id = signal_data.get('original_signal_id')
            if original_id in self.active_signals:
                del self.active_signals[original_id]
        
        print(f"📨 Signal added: {signal_id}")
        return signal_id
    
    def get_next_signal(self):
        """Get next signal from queue"""
        if self.signal_queue:
            signal = self.signal_queue.popleft()
            signal['status'] = 'processed'
            signal['processed_at'] = time.time()
            return signal
        return None
    
    def forward_to_mt5_bridge(self, signal_data):
        """Forward signal to MT5 bridge if configured"""
        if not self.mt5_bridge_url:
            return False
        
        try:
            response = requests.post(
                self.mt5_bridge_url,
                json=signal_data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Forward to MT5 failed: {e}")
            return False

# Global server instance
webhook_server = LocalWebhookServer()

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "service": "FTMO 1H Enhanced Webhook Server",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "webhook": "/webhook",
            "status": "/status", 
            "queue": "/queue",
            "dequeue": "/dequeue"
        }
    })

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """Receive webhook signals"""
    try:
        signal_data = request.json
        
        if not signal_data:
            return jsonify({"error": "No data received"}), 400
        
        # Validate basic structure
        required_fields = ['signalId', 'symbol', 'event']
        missing_fields = [f for f in required_fields if f not in signal_data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {missing_fields}"
            }), 400
        
        # Add signal to queue
        signal_id = webhook_server.add_signal(signal_data)
        
        # Forward to MT5 bridge if configured
        if webhook_server.mt5_bridge_url:
            forwarded = webhook_server.forward_to_mt5_bridge(signal_data)
            if forwarded:
                print(f"✅ Signal forwarded to MT5: {signal_id}")
            else:
                print(f"⚠️ Failed to forward to MT5: {signal_id}")
        
        return jsonify({
            "ok": True,
            "signal_id": signal_id,
            "status": "queued",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dequeue', methods=['GET'])
def dequeue_signal():
    """Dequeue next signal (compatible with MT5 EA polling)"""
    try:
        account = request.args.get('account', 'DEFAULT')
        
        signal = webhook_server.get_next_signal()
        
        if signal:
            print(f"📤 Signal dequeued for {account}: {signal['id']}")
            return jsonify(signal['data'])
        else:
            return jsonify({"message": "No signals available"}), 204
            
    except Exception as e:
        print(f"❌ Dequeue error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/enqueue', methods=['POST'])
def enqueue_signal():
    """Enqueue signal (alternative endpoint name)"""
    return receive_webhook()

@app.route('/status')
def status():
    """Server status"""
    return jsonify({
        "status": "running",
        "queue_size": len(webhook_server.signal_queue),
        "total_signals": len(webhook_server.signal_history),
        "active_signals": len(webhook_server.active_signals),
        "uptime": time.time(),
        "mt5_bridge_configured": webhook_server.mt5_bridge_url is not None
    })

@app.route('/queue')
def view_queue():
    """View current queue"""
    return jsonify({
        "queue": list(webhook_server.signal_queue),
        "active_signals": list(webhook_server.active_signals.keys()),
        "queue_size": len(webhook_server.signal_queue)
    })

@app.route('/history')
def view_history():
    """View signal history"""
    return jsonify({
        "history": webhook_server.signal_history[-20:],  # Last 20 signals
        "total_count": len(webhook_server.signal_history)
    })

@app.route('/clear', methods=['POST'])
def clear_queue():
    """Clear signal queue"""
    webhook_server.signal_queue.clear()
    return jsonify({"ok": True, "message": "Queue cleared"})

def run_server(host='0.0.0.0', port=5000):
    """Run the webhook server"""
    print(f"\n🚀 STARTING LOCAL WEBHOOK SERVER")
    print(f"📡 Address: http://{host}:{port}")
    print(f"🎯 Webhook endpoint: http://{host}:{port}/webhook")
    print(f"📊 Status endpoint: http://{host}:{port}/status")
    print("=" * 60)
    
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='FTMO 1H Enhanced Webhook Server')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--mt5-bridge', help='MT5 bridge URL for forwarding')
    
    args = parser.parse_args()
    
    if args.mt5_bridge:
        webhook_server.mt5_bridge_url = args.mt5_bridge
        print(f"🔗 MT5 Bridge configured: {args.mt5_bridge}")
    
    run_server(args.host, args.port)