from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import sys
import traceback

def create_app():
    app = Flask(__name__)
    
    # Production CORS configuration
    CORS_ORIGINS = [
        'https://ai-chat-memory-gumx.vercel.app',
        'http://localhost:3000'
    ]
    
    CORS(app, 
        origins=CORS_ORIGINS,
        supports_credentials=True,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        max_age=600
    )
    
    # Global variables
    gemini_client = None
    vector_store = None
    dependencies_loaded = False
    sessions = {}

    def initialize_dependencies():
        nonlocal gemini_client, vector_store, dependencies_loaded
        try:
            print("🚀 Initializing AI Chat dependencies...")
            
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

    # Health check endpoint (critical for Railway)
    @app.route('/')
    def root():
        return jsonify({
            'message': 'AI Chat with Memory Backend',
            'status': 'running',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'dependencies_loaded': dependencies_loaded
        }), 200

    @app.route('/api/health')
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

    @app.route('/api/test')
    def test():
        return jsonify({
            'message': 'Backend is running!',
            'dependencies_loaded': dependencies_loaded,
            'sessions_count': len(sessions),
            'timestamp': datetime.now().isoformat()
        }), 200

    @app.route('/api/ping')
    def ping():
        return jsonify({
            'message': 'pong',
            'status': 'ok',
            'timestamp': datetime.now().isoformat()
        }), 200

    # Main chat endpoint with comprehensive error handling
    @app.route('/api/chat', methods=['POST', 'OPTIONS'])
    def handle_chat():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            print(f"📨 Received chat request from {request.remote_addr}")
            
            if not dependencies_loaded:
                return jsonify({
                    'error': 'Service initializing. Please try again in a moment.',
                    'dependencies_loaded': False
                }), 503
            
            # Parse JSON data
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
                
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data received'}), 400
                
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400
            
            print(f"💬 Processing message: {user_message[:100]}...")
            
            # Create new session if doesn't exist
            if not session_id or session_id not in sessions:
                session_id = str(uuid.uuid4())
                sessions[session_id] = {
                    'created_at': datetime.now().isoformat(),
                    'conversation_history': [],
                    'message_count': 0
                }
                print(f"🆕 Created new session: {session_id}")
            
            # Search for relevant context
            context = vector_store.search_similar_conversations(session_id, user_message)
            
            if context:
                context_lines = context.split('\n\n')
                print(f"📚 Found {len(context_lines)} relevant conversation contexts")
            else:
                print("🆕 No relevant context found - starting fresh conversation")
            
            # Generate AI response
            print("🤖 Generating AI response...")
            ai_response = gemini_client.generate_response(user_message, context)
            print(f"✅ Response generated ({len(ai_response)} characters)")
            
            # Store conversation in memory
            vector_store.add_conversation(session_id, user_message, ai_response)
            
            # Update session history
            sessions[session_id]['conversation_history'].append({
                'user': user_message,
                'assistant': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            sessions[session_id]['message_count'] += 1
            
            # Prepare response
            response_data = {
                'response': ai_response,
                'session_id': session_id,
                'context_used': bool(context),
                'conversation_count': vector_store.get_conversation_count(session_id),
                'session_message_count': sessions[session_id]['message_count'],
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Chat request completed successfully")
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"❌ Chat endpoint error: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': 'Internal server error',
                'message': 'Please try again in a moment'
            }), 500

    # Session management endpoints
    @app.route('/api/session/<session_id>', methods=['GET'])
    def get_session(session_id):
        if session_id in sessions:
            session_data = sessions[session_id].copy()
            # Don't send full history to client for privacy
            session_data['conversation_history'] = []
            return jsonify(session_data), 200
        else:
            return jsonify({'error': 'Session not found'}), 404

    @app.route('/api/session/<session_id>', methods=['DELETE'])
    def delete_session(session_id):
        if session_id in sessions:
            del sessions[session_id]
            return jsonify({'message': 'Session deleted'}), 200
        else:
            return jsonify({'error': 'Session not found'}), 404

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    print("✅ Flask app configured successfully")
    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting AI Chat with Memory Backend on port {port}")
    print(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    app.run(host='0.0.0.0', port=port, debug=False)