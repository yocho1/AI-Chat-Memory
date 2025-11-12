from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.gemini_client import GeminiClient
from utils.vector_store import VectorStore
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize clients
gemini_client = GeminiClient()
vector_store = VectorStore()

# In-memory session storage (replace with database in production)
sessions = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
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
        
        # Search for relevant context from user's past conversations
        context = vector_store.search_similar_conversations(session_id, user_message)
        
        if context:
            print(f"Using context from {len(context.split('\\n\\n'))} previous conversations")
        else:
            print("No relevant context found - starting fresh")
        
        # Generate AI response
        ai_response = gemini_client.generate_response(user_message, context)
        
        # Store conversation in vector database
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

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get conversation history for a session"""
    try:
        if session_id in sessions:
            return jsonify(sessions[session_id]['conversation_history'])
        else:
            return jsonify([])
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        return jsonify([])

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions (for demo purposes)"""
    return jsonify(list(sessions.keys()))

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about stored conversations"""
    try:
        total_conversations = vector_store.get_conversation_count()
        active_sessions = len(sessions)
        
        stats = {
            'total_conversations': total_conversations,
            'active_sessions': active_sessions,
            'storage_path': vector_store.data_dir
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Chat with Memory Backend'
    })

if __name__ == '__main__':
    print("Starting AI Chat with Memory Backend...")
    print("Data will be stored in: ./chroma_db/")
    print("Server running on: http://localhost:5000")
    app.run(debug=True, port=5000)