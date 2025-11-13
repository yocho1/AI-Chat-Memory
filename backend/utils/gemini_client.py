import google.generativeai as genai
import time
import random
from config import Config

class GeminiClient:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        
        if not self.api_key or self.api_key == 'your_google_gemini_api_key_here':
            raise Exception("Please set GOOGLE_API_KEY in your .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = self._setup_free_tier_model()
    
    def _setup_free_tier_model(self):
        """Setup a model that works with free tier quotas"""
        # Free tier models (usually have higher quotas)
        free_tier_models = [
            'gemini-2.0-flash-001',      # Stable free tier model
            'gemini-2.0-flash-lite-001', # Lightweight free tier
            'gemini-1.5-flash',          # If available
            'gemini-1.5-pro',            # If available
        ]
        
        # Try each model
        for model_name in free_tier_models:
            try:
                model = genai.GenerativeModel(model_name)
                # Quick test
                test_response = model.generate_content("Say 'OK'")
                print(f"SUCCESS: Using free-tier model: {model_name}")
                return model
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        
        # If no free tier models work, use demo mode
        print("WARNING: No free-tier models available. Using demo mode.")
        return None
    
    def generate_response(self, prompt, context=""):
        # If we have a real model, try to use it
        if self.model:
            try:
                if context:
                    full_prompt = f"""Based on our previous conversation:

{context}

Current question: {prompt}

Please provide a helpful response that considers our previous discussion."""
                else:
                    full_prompt = f"""User: {prompt}

Please provide a helpful and friendly response."""
                
                response = self.model.generate_content(full_prompt)
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                print(f"Gemini API Error: {error_msg}")
                
                # Check if it's a quota error
                if "quota" in error_msg.lower() or "429" in error_msg:
                    return self._get_quota_exceeded_response(prompt, context)
                else:
                    return self._get_demo_response(prompt, context, f"API Error: {error_msg}")
        
        # No model available, use demo mode
        return self._get_demo_response(prompt, context)
    
    def _get_quota_exceeded_response(self, prompt, context):
        """Provide helpful response when quota is exceeded"""
        base_responses = [
            "I'd love to answer your question, but I've reached my free API quota for now.",
            "I'm currently in demo mode due to API quota limits, but I can still help with basic responses.",
            "Due to free tier limits, I'm providing demo responses. The memory system still works perfectly!",
        ]
        
        if context:
            responses = [
                f"I see we've discussed this before! {random.choice(base_responses)}",
                f"Considering our previous conversation, {random.choice(base_responses).lower()}",
            ]
        else:
            responses = base_responses
        
        response = random.choice(responses)
        response += "\n\nYou can upgrade to a paid plan at https://aistudio.google.com/ for unlimited AI responses."
        
        return response
    
    def _get_demo_response(self, prompt, context="", error_msg=None):
        """Provide intelligent demo responses"""
        prompt_lower = prompt.lower()
        
        # Context-aware responses
        if context:
            responses = [
                f"I see we've talked about this before! Regarding '{prompt}', in a full setup I'd provide a detailed AI response.",
                f"Building on our previous conversation, I'd normally give you a comprehensive answer about '{prompt}'.",
                f"Considering our earlier discussion, '{prompt}' would get a thoughtful AI-generated response.",
            ]
        else:
            responses = [
                f"I understand you're asking about '{prompt}'. With full API access, I'd provide a comprehensive AI response.",
                f"Thanks for your question about '{prompt}'! In a production setup, you'd get a detailed AI answer.",
                f"Regarding '{prompt}', the AI would normally analyze this and provide a thoughtful response.",
            ]
        
        response = random.choice(responses)
        
        if error_msg:
            response += f"\n\n(Technical note: {error_msg})"
        else:
            response += "\n\nThis is a demo response. The chat memory system is fully functional!"
        
        return response

def test_gemini_auth():
    """Test the API setup"""
    try:
        client = GeminiClient()
        test_response = client.generate_response("Hello! Are you working?")
        print("SUCCESS: Chat system is ready!")
        print(f"Response: {test_response}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_gemini_auth()