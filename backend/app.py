from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import sys
import traceback
import signal
import atexit

app = Flask(__name__)

# Configure CORS properly
CORS(app, origins=["https://ai-chat-memory-gumx.vercel.app", "http://localhost:3000"])

# Global variables
gemini_client = None
vector_store = None
dependencies_loaded = False
sessions = {}

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("💥 CRITICAL: Uncaught exception:", file=sys.stderr)
    print(f"Type: {exc_type}", file=sys.stderr)
    print(f"Value: {exc_value}", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

# Set global exception handler
sys.excepthook = handle_exception

def initialize_dependencies():
    global gemini_client, vector_store, dependencies_loaded
    try:
        print("🚀 Initializing dependencies...")
        
        # Import and initialize Gemini client
        from utils.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        print("✅ Gemini client initialized")
        
        # Import and initialize vector store
        from utils.vector_store import VectorStore
        vector_store = VectorStore()
        print("✅ Vector store initialized")
        
        dependencies_loaded = True
        print("✅ All dependencies loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Dependency initialization failed: {e}")
        traceback.print_exc()
        dependencies_loaded = False
        return False

def safe_import_check():
    """Check if all required modules can be imported safely"""
    try:
        # Test imports that happen at runtime
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        print("✅ All runtime imports successful")
        return True
    except Exception as e:
        print(f"❌ Runtime import failed: {e}")
        traceback.print_exc()
        return False

# Initialize application
print("🔧 Starting application initialization...")

# Test basic imports first
if safe_import_check():
    print("✅ Basic imports check passed")
else:
    print("❌ Basic imports check failed")

# Initialize dependencies
if initialize_dependencies():
    print("🎉 Application started successfully!")
else:
    print("⚠️ Application started with degraded functionality")

@app.before_request
def before_request():
    print(f"📥 Incoming request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    print(f"📤 Response: {response.status_code} for {request.method} {request.path}")
    return response

@app.errorhandler(500)
def handle_500(error):
    print(f"💥 Internal Server Error: {error}")
    traceback.print_exc()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def handle_404(error):
    print(f"🔍 404 Not Found: {request.path}")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    print("🟡 Chat endpoint called")
    try:
        if not dependencies_loaded:
            print("🔴 Dependencies not loaded")
            return jsonify({'error': 'Backend dependencies not loaded. Check server logs.'}), 500
        
        data = request.json
        if not data:
            print("🔴 No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400
            
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            print("🔴 Empty message")
            return jsonify({'error': 'Message is required'}), 400
        
        print(f"📨 Received message: {user_message}")
        
        # Create new session if doesn't exist
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'created_at': datetime.now().isoformat(),
                'conversation_history': []
            }
            print(f"🆕 Created new session: {session_id}")
        
        # Search for relevant context
        context = vector_store.search_similar_conversations(session_id, user_message)
        
        if context:
            context_lines = context.split('\n\n')
            print(f"📚 Using context from {len(context_lines)} previous conversations")
        else:
            print("🆕 No relevant context found - starting fresh")
        
        # Generate AI response
        print("🤖 Generating AI response...")
        ai_response = gemini_client.generate_response(user_message, context)
        print(f"✅ AI response generated: {ai_response[:100]}...")
        
        # Store conversation
        vector_store.add_conversation(session_id, user_message, ai_response)
        
        # Update session history
        sessions[session_id]['conversation_history'].append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        response_data = {
            'response': ai_response,
            'session_id': session_id,
            'context_used': bool(context),
            'conversation_count': vector_store.get_conversation_count(session_id)
        }
        
        print(f"✅ Response generated for session {session_id}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in /api/chat: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    print("🟡 Health endpoint called")
    return jsonify({
        'status': 'healthy' if dependencies_loaded else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Chat with Memory Backend',
        'dependencies_loaded': dependencies_loaded,
        'sessions_count': len(sessions)
    })

@app.route('/api/test', methods=['GET'])
def test():
    print("🟡 Test endpoint called")
    return jsonify({
        'message': 'Backend is running!',
        'dependencies_loaded': dependencies_loaded,
        'sessions_count': len(sessions),
        'gemini_working': dependencies_loaded and gemini_client is not None,
        'vector_store_working': dependencies_loaded and vector_store is not None
    })

# Simple test endpoint
@app.route('/api/ping', methods=['GET'])
def ping():
    print("🟡 Ping endpoint called")
    return jsonify({
        'message': 'pong',
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

# Root endpoint
@app.route('/')
def root():
    print("🟡 Root endpoint called")
    return jsonify({
        'message': 'AI Chat with Memory Backend',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'test': '/api/test',
            'ping': '/api/ping',
            'chat': '/api/chat (POST)'
        }
    })

@app.route('/api/debug', methods=['GET'])
def debug():
    print("🟡 Debug endpoint called")
    return jsonify({
        'python_version': sys.version,
        'flask_ready': True,
        'dependencies_loaded': dependencies_loaded,
        'sessions_count': len(sessions),
        'timestamp': datetime.now().isoformat()
    })

# Add a simple sync worker test
@app.route('/api/simple', methods=['GET'])
def simple():
    print("🟡 Simple endpoint called")
    return jsonify({
        'message': 'Simple endpoint working!',
        'status': 'success'
    })

def signal_handler(signum, frame):
    print(f"🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@atexit.register
def cleanup():
    print("🧹 Application shutting down...")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    print(f"✅ Dependencies loaded: {dependencies_loaded}")
    app.run(host='0.0.0.0', port=port, debug=False)