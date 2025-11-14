from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import sys

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ai-chat-memory-gumx.vercel.app",
            "https://*.vercel.app",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Add CORS headers manually for OPTIONS requests
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = [
        "https://ai-chat-memory-gumx.vercel.app",
        "https://*.vercel.app", 
        "http://localhost:3000"
    ]
    
    if origin and any(origin.endswith(domain.replace('*', '')) for domain in allowed_origins):
        response.headers.add('Access-Control-Allow-Origin', origin)
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Handle OPTIONS requests for CORS preflight
@app.route('/api/chat', methods=['OPTIONS'])
def options_chat():
    return '', 200

# Try to import dependencies with error handling
try:
    from utils.gemini_client import GeminiClient
    from utils.vector_store import VectorStore
    gemini_client = GeminiClient()
    vector_store = VectorStore()
    dependencies_loaded = True
except ImportError as e:
    print(f"Import error: {e}")
    dependencies_loaded = False
except Exception as e:
    print(f"Initialization error: {e}")
    dependencies_loaded = False

# In-memory session storage
sessions = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    if not dependencies_loaded:
        return jsonify({'error': 'Backend dependencies not loaded'}), 500
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        print(f"Received message: {user_message}")
        
        # Create new session if doesn't exist
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'created_at': datetime.now().isoformat(),
                'conversation_history': []
            }
            print(f"Created new session: {session_id}")
        
        # Search for relevant context
        context = vector_store.search_similar_conversations(session_id, user_message)
        
        if context:
            context_lines = context.split('\n\n')
            print(f"Using context from {len(context_lines)} previous conversations")
        else:
            print("No relevant context found - starting fresh")
        
        # Generate AI response
        ai_response = gemini_client.generate_response(user_message, context)
        
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
        
        print(f"Response generated for session {session_id}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in /api/chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy' if dependencies_loaded else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Chat with Memory Backend',
        'dependencies_loaded': dependencies_loaded
    })

@app.route('/api/test', methods=['GET', 'OPTIONS'])
def test():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'message': 'Backend is running!',
        'dependencies_loaded': dependencies_loaded,
        'sessions_count': len(sessions)
    })

# Root endpoint
@app.route('/')
def root():
    return jsonify({
        'message': 'AI Chat with Memory Backend',
        'endpoints': {
            'health': '/api/health',
            'test': '/api/test', 
            'chat': '/api/chat (POST)'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)