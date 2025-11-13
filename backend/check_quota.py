import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("ERROR: No API key found")
    exit(1)

genai.configure(api_key=api_key)

print("Checking available free-tier models...")

free_tier_models = [
    'gemini-2.0-flash-001',
    'gemini-2.0-flash-lite-001', 
    'gemini-1.5-flash',
    'gemini-1.5-pro',
]

for model_name in free_tier_models:
    print(f"\nTesting {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        # Very simple test to avoid quota
        response = model.generate_content("Say 'OK'", 
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10
            )
        )
        print(f"SUCCESS: {model_name} is available!")
        break
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            print(f"QUOTA EXCEEDED: {model_name}")
            # Extract retry time if available
            if "retry in" in error_msg:
                print(f"  Retry time: {error_msg.split('retry in')[-1].split('.')[0]} seconds")
        else:
            print(f"ERROR: {error_msg}")

print("\n" + "="*50)
print("QUOTA STATUS: You've exceeded free tier limits.")
print("SOLUTIONS:")
print("1. Wait 24 hours for quota reset")
print("2. Upgrade to paid plan at: https://aistudio.google.com/")
print("3. Use demo mode (memory system still works)")
print("="*50)