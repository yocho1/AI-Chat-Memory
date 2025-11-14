from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import sys
import traceback

def create_app():
    app = Flask(__name__)
    
    # SIMPLIFIED CORS - Allow all origins initially for debugging
    CORS(app, 
        origins='*',  # Temporarily allow all
        supports_credentials=True,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
        expose_headers=['Content-Type'],
        max_age=3600
    )
    
    # Global variables
    gemini_client = None
    vector_store = None
    dependencies_loaded = False
    sessions = {}

    def initialize_dependencies():
        nonlocal gemini_client, vector_store, dependencies_loaded
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

    # Initialize dependencies
    print("🔧 Starting application initialization...")
    initialize_dependencies()

    # Root route - important for Railway health checks
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'AI Chat with Memory Backend',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'test': '/api/test',
                'ping': '/api/ping',
                'chat': '/api/chat (POST)'
            }
        }), 200

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy' if dependencies_loaded else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'service': 'AI Chat with Memory Backend',
            'dependencies_loaded': dependencies_loaded,
            'sessions_count': len(sessions),
            'gemini_available': gemini_client is not None,
            'vector_store_available': vector_store is not None
        }), 200

    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({
            'message': 'Backend is running!',
            'dependencies_loaded': dependencies_loaded,
            'sessions_count': len(sessions),
            'gemini_working': dependencies_loaded and gemini_client is not None,
            'vector_store_working': dependencies_loaded and vector_store is not None,
            'timestamp': datetime.now().isoformat()
        }), 200

    @app.route('/api/ping', methods=['GET'])
    def ping():
        return jsonify({
            'message': 'pong',
            'status': 'ok',
            'timestamp': datetime.now().isoformat()
        }), 200

    @app.route('/api/chat', methods=['POST', 'OPTIONS'])
    def handle_chat():
        # Handle preflight
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response, 200
        
        try:
            print(f"📨 Received POST /api/chat")
            print(f"📋 Headers: {dict(request.headers)}")
            print(f"📦 Content-Type: {request.content_type}")
            
            if not dependencies_loaded:
                print("❌ Dependencies not loaded")
                return jsonify({
                    'error': 'Backend dependencies not loaded. Check server logs.',
                    'dependencies_loaded': False
                }), 500
            
            data = request.get_json(force=True)
            if not data:
                print("❌ No JSON data received")
                return jsonify({'error': 'No JSON data received'}), 400
            
            print(f"📊 Received data: {data}")
                
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not user_message:
                print("❌ Empty message")
                return jsonify({'error': 'Message is required'}), 400
            
            print(f"📨 Processing message: {user_message[:50]}...")
            
            # Create new session if doesn't exist
            if not session_id or session_id not in sessions:
                session_id = str(uuid.uuid4())
                sessions[session_id] = {
                    'created_at': datetime.now().isoformat(),
                    'conversation_history': []
                }
                print(f"🆕 Created new session: {session_id}")
            
            # Search for relevant context
            print(f"🔍 Searching for context...")
            context = vector_store.search_similar_conversations(session_id, user_message)
            
            if context:
                context_lines = context.split('\n\n')
                print(f"📚 Found {len(context_lines)} relevant conversations")
            else:
                print("🆕 No relevant context found")
            
            # Generate AI response
            print("🤖 Generating AI response...")
            ai_response = gemini_client.generate_response(user_message, context)
            print(f"✅ Response generated: {ai_response[:100]}...")
            
            # Store conversation
            print("💾 Storing conversation...")
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
            
            print(f"✅ Request completed successfully for session {session_id}")
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"❌ Error in /api/chat: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': f'Internal server error: {str(e)}',
                'type': type(e).__name__
            }), 500

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'error': 'Endpoint not found',
            'path': request.path
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

    # After request handler to add CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    print(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    app.run(host='0.0.0.0', port=port, debug=False)