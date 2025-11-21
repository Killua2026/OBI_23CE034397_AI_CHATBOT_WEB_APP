import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY not found in .env file.")
    exit()

genai.configure(api_key=api_key)

# --- 1. Dynamic Model Discovery (Same as app.py) ---
def get_valid_model_name():
    """
    Dynamically finds a working model to avoid 404 errors.
    """
    try:
        # Ask Google which models are available
        all_models = [m.name.replace("models/", "") for m in genai.list_models() 
                      if "generateContent" in m.supported_generation_methods]
        
        # Priority list (preferred models first)
        priority_order = [
            "gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash",
            "gemini-pro", "gemini-1.0-pro"
        ]
        
        # Check priority list against available models
        for preferred in priority_order:
            if preferred in all_models:
                return preferred
        
        # Fallback: just take the first available one
        if all_models:
            return all_models[0]
            
    except Exception as e:
        print(f"[System Warning]: Model discovery failed ({e}). Defaulting to 'gemini-2.5-flash'.")
    
    # Hard fallback if discovery fails
    return "gemini-2.5-flash"

# Select the model ONCE at startup
SELECTED_MODEL_NAME = get_valid_model_name()
print(f"[System]: Selected AI Model: {SELECTED_MODEL_NAME}")

# --- 2. Preprocessing (Required) ---
def preprocess_text(text):
    """
    REQUIRED: Lowercasing, punctuation removal, tokenization.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.split()
    return tokens

def main():
    print("="*50)
    print(" NLP Q&A System - CLI Mode")
    print(" Type 'exit' to quit.")
    print("="*50)

    model = genai.GenerativeModel(SELECTED_MODEL_NAME)

    while True:
        try:
            user_input = input("\nEnter your question: ")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        # Step 1: Preprocess
        tokens = preprocess_text(user_input)
        print(f"\n[Processed Input (Tokens)]: {tokens}")
        
        # Step 2: Send to AI
        print("[System]: Querying LLM API...")
        
        try:
            response = model.generate_content(user_input)
            
            # Step 3: Display Answer
            if response.text:
                print(f"\n[AI Answer]:\n{response.text}")
            else:
                print("\n[AI Answer]: No text returned (Safety block or empty).")
                
        except Exception as e:
            if "429" in str(e):
                print("\n[Error]: Quota Exceeded (429). Please wait 1-2 minutes and try again.")
            else:
                print(f"\n[Error]: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()