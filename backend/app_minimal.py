from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

print("🔧 Starting ABSOLUTE MINIMAL Flask app...")

app = Flask(__name__)

# Simple CORS that definitely works
CORS(app)

@app.route('/')
def root():
    print("✅ ROOT endpoint called")
    return jsonify({'message': 'Minimal app working!'})

@app.route('/api/ping', methods=['GET'])
def ping():
    print("✅ PING endpoint called")
    return jsonify({'message': 'pong'})

@app.route('/api/health', methods=['GET'])
def health():
    print("✅ HEALTH endpoint called")
    return jsonify({'status': 'healthy'})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    print("✅ CHAT endpoint called")
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        user_message = data.get('message', '') if data else ''
        
        return jsonify({
            'response': f'Demo response to: {user_message}',
            'session_id': 'demo-session',
            'demo': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)