from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

print("🔧 Loading simple app...")

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    print("✅ Root endpoint called")
    return jsonify({'message': 'Simple app working!'})

@app.route('/api/health')
def health():
    print("✅ Health endpoint called")
    return jsonify({'status': 'healthy'})

@app.route('/api/ping')
def ping():
    print("✅ Ping endpoint called")
    return jsonify({'message': 'pong'})

@app.route('/api/test')
def test():
    print("✅ Test endpoint called")
    return jsonify({'message': 'test successful'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting simple server on port {port}")
    app.run(host='0.0.0.0', port=port)