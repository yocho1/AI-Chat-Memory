import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("ERROR: No API key found in .env file")
    print("Please add: GOOGLE_API_KEY=your_actual_key_here")
    exit(1)

try:
    genai.configure(api_key=api_key)
    
    print("Discovering available models...")
    models = genai.list_models()
    
    print("\nAvailable models that support generateContent:")
    found_models = []
    
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            found_models.append(model.name)
            print(f"Model: {model.name}")
            print(f"   Description: {model.description}")
            print(f"   Methods: {model.supported_generation_methods}")
            print("   ---")
    
    if found_models:
        print(f"Found {len(found_models)} models that support generateContent:")
        for model in found_models:
            print(f"   - {model}")
            
        # Test the first available model
        print("\nTesting the first model...")
        first_model_name = found_models[0].replace('models/', '')
        try:
            model = genai.GenerativeModel(first_model_name)
            test_response = model.generate_content("Say 'TEST SUCCESS'")
            print(f"SUCCESS: Model {first_model_name} works!")
            print(f"Test response: {test_response.text}")
        except Exception as e:
            print(f"ERROR testing {first_model_name}: {e}")
            
    else:
        print("No models found that support generateContent")
        
except Exception as e:
    print(f"Error: {e}")