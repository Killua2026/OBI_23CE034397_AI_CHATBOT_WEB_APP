"""
AI Chat Application with Flask and Google Gemini
A web-based chat interface that queries the Gemini AI model and stores conversation history.
"""

import os
import sqlite3
import google.generativeai as genai
import traceback 
from contextlib import contextmanager
from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv

# Add import for specific API exception to detect NotFound model errors
from google.api_core.exceptions import NotFound

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Database Setup & Utilities ---

def init_db():
    """
    Initializes the database and creates the 'history' table if it doesn't exist.
    """
    try:
        conn = sqlite3.connect('queries.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    """
    conn = None
    try:
        conn = sqlite3.connect('queries.db')
        yield conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

# --- AI Configuration (Google Gemini) ---

try:
    # Get the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Make sure it's set in your .env file or Render environment.")
        
    genai.configure(api_key=api_key)

    # Discover available models that support generateContent
    def discover_available_models():
        """Query the API to find models that support generateContent."""
        try:
            models = genai.list_models()
            available = []
            for m in models:
                # Check if the model supports generateContent method
                if "generateContent" in m.supported_generation_methods:
                    available.append(m.name.replace("models/", ""))
            return available
        except Exception as e:
            print(f"Error discovering models: {e}")
            return []

    all_models = discover_available_models()
    
    # Prioritize models by tier: flash/lite first (better free tier), then pro
    priority_order = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-preview-05-20",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-2.5-pro",
        "gemini-2.0-pro-exp",
        "gemini-pro-latest",
    ]
    
    # Build candidate list respecting priority order
    model_candidates = []
    for priority_model in priority_order:
        if priority_model in all_models:
            model_candidates.append(priority_model)
    
    # Add any remaining models not in priority list
    for m in all_models:
        if m not in model_candidates:
            model_candidates.append(m)
    
    if not model_candidates:
        print("WARNING: No models with generateContent support found. Using fallback list.")
        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash"]
    else:
        print(f"✓ Model priority order: {model_candidates[:5]}... ({len(model_candidates)} total)")

    model = None
    selected_model_name = None

except ValueError as e:
    print(f"CRITICAL ERROR: {e}")
    model = None
    model_candidates = []

# Helper: extract text from various SDK response shapes
def extract_response_text(response):
    # Prefer common attributes
    if response is None:
        return None
    # newer SDK: response.text
    text = getattr(response, "text", None)
    if text:
        return text
    # some responses use 'content' or 'candidates'
    content = getattr(response, "content", None)
    if content:
        return content
    parts = getattr(response, "parts", None)
    if parts:
        try:
            return "".join(p.get("text", str(p)) if isinstance(p, dict) else str(p) for p in parts)
        except Exception:
            return str(parts)
    candidates = getattr(response, "candidates", None)
    if candidates and len(candidates) > 0:
        first = candidates[0]
        # candidate may have .content or .text
        return getattr(first, "content", None) or getattr(first, "text", None) or str(first)
    # fallback to string conversion
    return str(response)

# Helper: try generate_content across candidates until success
def generate_with_fallback(prompt, candidates):
    last_exc = None
    for name in candidates:
        try:
            print(f"Attempting model: {name}")
            m = genai.GenerativeModel(name)
            resp = m.generate_content(prompt)
            # If the call didn't raise, return both name and response
            return name, resp
        except NotFound as nf:
            # model not available for this account/version -> try next candidate
            print(f"Model {name} not found or not supported for generate_content: {nf}")
            last_exc = nf
            continue
        except Exception as ex:
            # for other errors, log and keep trying other candidates
            print(f"Error using model {name}: {ex}")
            last_exc = ex
            continue
    # if we exhausted candidates, raise the last exception (or a generic one)
    if last_exc:
        raise last_exc
    raise RuntimeError("No model candidates provided")

def validate_question(question):
    """
    Validates the user's question input.
    """
    if not question or not question.strip():
        abort(400, "Question cannot be empty.")
    
    if len(question.strip()) > 2000:
        abort(400, "Question too long. Please keep it under 2000 characters.")

# --- Flask Routes ---

@app.route('/')
def home():
    """
    Serves the main HTML page.
    """
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_api():
    """
    API endpoint that receives a question, queries the AI model,
    stores the conversation, and returns the response.
    """
    if not model and not model_candidates:
        return jsonify({"error": "AI model is not configured. Check API key configuration."}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON in request body."}), 400
    
    user_question = data.get('question', '').strip()

    try:
        # Input validation
        validate_question(user_question)
        
        # Query Google Gemini API
        print(f"Querying AI for question: {user_question[:100]}...")
        
        # Use the fallback generator that tries multiple candidate models
        selected_model_name = None
        response = None
        try:
            selected_model_name, response = generate_with_fallback(user_question, model_candidates)
            print(f"✓ Succeeded with model: {selected_model_name}")
        except Exception as gen_err:
            print(f"✗ AI generation failed for all candidates:")
            traceback.print_exc()
            raise

        # Extract a readable answer from the SDK response (robust to different shapes)
        ai_answer = extract_response_text(response)
        if not ai_answer or not ai_answer.strip():
            ai_answer = "I'm sorry, I couldn't generate a response. Please try again."

        print(f"AI response received: {ai_answer[:100]}...")

        # Store conversation in database
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO history (question, answer) VALUES (?, ?)", 
                    (user_question, ai_answer)
                )
                conn.commit()
                print("Conversation stored in database.")
        except Exception as db_error:
            print(f"Non-critical database error: {db_error}")

        # Return successful response
        return jsonify({
            "answer": ai_answer,
            "status": "success",
            "model": selected_model_name
        })

    except Exception as e:
        print("\n" + "="*50)
        print("UNEXPECTED ERROR IN ask_api ENDPOINT")
        print("="*50)
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        traceback.print_exc()
        print("="*50 + "\n")
        
        # Handle potential API errors (e.g., safety blocks)
        return jsonify({
            "error": f"An error occurred while processing your request: {str(e)}"
        }), 500

# --- Application Startup ---

if __name__ == '__main__':
    init_db()
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000))
    )