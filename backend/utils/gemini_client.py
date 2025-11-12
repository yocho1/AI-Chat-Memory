import google.generativeai as genai
from config import Config

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_response(self, prompt, context=""):
        try:
            full_prompt = f"""
            Context from previous conversations: {context}
            
            Current question: {prompt}
            
            Please provide a helpful and relevant response based on the context and current question.
            """
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"