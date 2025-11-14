from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import sys
import traceback

app = Flask(__name__)

# Configure CORS properly - fix the origin URL
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://ai-chat-memory-gumx.vercel.app", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Or use this simpler CORS configuration for testing:
# CORS(app, origins=["https://ai-chat-memory-gumx.vercel.app", "http://localhost:3000"])

# Initialize dependencies with better error handling
def initialize_dependencies():
    try:
        print("Initializing dependencies...")
        
        # Import and initialize Gemini client
        from utils.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        print("✅ Gemini client initialized")
        
        # Import and initialize vector store
        from utils.vector_store import VectorStore
        vector_store = VectorStore()
        print("✅ Vector store initialized")
        
        return gemini_client, vector_store, True
        
    except Exception as e:
        print(f"❌ Dependency initialization failed: {e}")
        print(traceback.format_exc())
        return None, None, False

# Initialize on startup
gemini_client, vector_store, dependencies_loaded = initialize_dependencies()

# In-memory session storage
sessions = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not dependencies_loaded:
            return jsonify({'error': 'Backend dependencies not loaded. Check server logs.'}), 500
        
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
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
        print(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy' if dependencies_loaded else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Chat with Memory Backend',
        'dependencies_loaded': dependencies_loaded,
        'sessions_count': len(sessions)
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Backend is running!',
        'dependencies_loaded': dependencies_loaded,
        'sessions_count': len(sessions),
        'gemini_working': dependencies_loaded and gemini_client is not None,
        'vector_store_working': dependencies_loaded and vector_store is not None
    })

# Root endpoint
@app.route('/')
def root():
    return jsonify({
        'message': 'AI Chat with Memory Backend',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'test': '/api/test',
            'chat': '/api/chat (POST)'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    print(f"✅ Dependencies loaded: {dependencies_loaded}")
    app.run(host='0.0.0.0', port=port, debug=False)