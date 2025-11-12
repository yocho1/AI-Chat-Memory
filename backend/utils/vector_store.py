import json
import uuid
import numpy as np
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self):
        self.data_dir = "./chroma_db"
        self.data_file = os.path.join(self.data_dir, "conversations.json")
        self.embeddings_file = os.path.join(self.data_dir, "embeddings.npy")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize storage
        self.conversations = self._load_json(self.data_file, [])
        self.metadata = self._load_json(self.metadata_file, [])
        self.embeddings = self._load_embeddings()
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
        
        # Fit vectorizer if we have existing data
        if self.conversations:
            texts = [conv["text"] for conv in self.conversations]
            self.vectorizer.fit(texts)
    
    def _load_json(self, filepath, default):
        """Load JSON file or return default if not exists"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _load_embeddings(self):
        """Load embeddings from file or return empty array"""
        if os.path.exists(self.embeddings_file):
            try:
                return np.load(self.embeddings_file)
            except Exception as e:
                print(f"Error loading embeddings: {e}")
        return np.array([]).reshape(0, 384)
    
    def _save_json(self, data, filepath):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {filepath}: {e}")
    
    def _save_embeddings(self):
        """Save embeddings to file"""
        try:
            np.save(self.embeddings_file, self.embeddings)
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def _get_embedding(self, text):
        """Generate TF-IDF embedding for text"""
        try:
            if hasattr(self.vectorizer, 'vocabulary_'):
                # Vectorizer is already fitted
                embedding = self.vectorizer.transform([text]).toarray()[0]
            else:
                # First time - fit the vectorizer
                embedding = self.vectorizer.fit_transform([text]).toarray()[0]
            
            # Ensure consistent dimensions (384)
            if len(embedding) < 384:
                embedding = np.pad(embedding, (0, 384 - len(embedding)))
            elif len(embedding) > 384:
                embedding = embedding[:384]
                
            return embedding
        except Exception as e:
            print(f"Embedding generation error: {e}")
            # Return random embedding as fallback
            return np.random.rand(384)
    
    def add_conversation(self, user_id, message, response):
        """Store conversation in vector database"""
        conversation_id = str(uuid.uuid4())
        text = f"User: {message}\nAssistant: {response}"
        timestamp = datetime.now().isoformat()
        
        # Create conversation data
        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "user_message": message,
            "assistant_response": response,
            "text": text
        }
        
        # Generate embedding
        embedding = self._get_embedding(text)
        
        # Update conversations list
        self.conversations.append(conversation_data)
        
        # Update metadata
        self.metadata.append({
            "id": conversation_id,
            "user_id": user_id,
            "timestamp": timestamp
        })
        
        # Update embeddings matrix
        if self.embeddings.shape[0] == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])
        
        # Save to disk
        self._save_json(self.conversations, self.data_file)
        self._save_json(self.metadata, self.metadata_file)
        self._save_embeddings()
        
        print(f"Stored conversation {conversation_id} for user {user_id}")
        return conversation_id
    
    def search_similar_conversations(self, user_id, query, n_results=3):
        """Search for similar past conversations for a specific user"""
        try:
            if len(self.conversations) == 0 or self.embeddings.shape[0] == 0:
                return ""
            
            # Generate query embedding
            query_embedding = self._get_embedding(query).reshape(1, -1)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get indices of conversations for this user
            user_indices = []
            for i, meta in enumerate(self.metadata):
                if i < len(self.conversations) and meta.get("user_id") == user_id:
                    user_indices.append(i)
            
            if not user_indices:
                return ""
            
            # Get top N most similar conversations for this user
            user_similarities = [(idx, similarities[idx]) for idx in user_indices]
            user_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Build context from top results
            context_parts = []
            for idx, similarity_score in user_similarities[:n_results]:
                if similarity_score > 0.1:  # Only include if somewhat relevant
                    conv = self.conversations[idx]
                    context_parts.append(conv["text"])
            
            context = "\n\n".join(context_parts)
            print(f"Found {len(context_parts)} relevant conversations for user {user_id}")
            return context
            
        except Exception as e:
            print(f"Search error: {e}")
            return ""
    
    def get_user_conversations(self, user_id, limit=10):
        """Get recent conversations for a specific user"""
        user_convos = [
            conv for conv in self.conversations 
            if conv.get("user_id") == user_id
        ]
        # Sort by timestamp (newest first)
        user_convos.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_convos[:limit]
    
    def get_conversation_count(self, user_id=None):
        """Get total number of conversations (optionally for a specific user)"""
        if user_id:
            return len([conv for conv in self.conversations if conv.get("user_id") == user_id])
        return len(self.conversations)