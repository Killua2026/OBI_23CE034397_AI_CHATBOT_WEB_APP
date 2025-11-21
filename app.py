"""
AI Chat Application with Flask and Google Gemini
Updated to meet "NLP Question‑and‑Answering System" requirements.
"""

import os
import re
import sqlite3
import google.generativeai as genai
import traceback 
from contextlib import contextmanager
from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv
from google.api_core.exceptions import NotFound

load_dotenv()

app = Flask(__name__)

# --- Database Setup ---
def init_db():
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
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn: conn.close()

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('queries.db')
        yield conn
    except sqlite3.Error as e:
        raise
    finally:
        if conn: conn.close()

# --- AI Setup ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: raise ValueError("GEMINI_API_KEY not found.")
    genai.configure(api_key=api_key)

    # Simplified candidate list based on what worked for you
    model_candidates = [
        "gemini-1.5-flash", "gemini-2.5-flash", "gemini-pro", 
        "gemini-1.0-pro", "gemini-flash-latest"
    ]
except ValueError as e:
    print(f"CRITICAL ERROR: {e}")
    model_candidates = []

# --- REQUIRED: Preprocessing Function ---
def preprocess_text(text):
    """
    Applies lowercasing, punctuation removal, and tokenization.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.split()
    return tokens

# --- Helper Functions ---
def extract_response_text(response):
    if not response: return None
    return getattr(response, "text", None) or str(response)

def generate_with_fallback(prompt, candidates):
    last_exc = None
    for name in candidates:
        try:
            m = genai.GenerativeModel(name)
            resp = m.generate_content(prompt)
            return name, resp
        except Exception as ex:
            last_exc = ex
            continue
    raise last_exc or RuntimeError("No models available")

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_api():
    if not model_candidates:
        return jsonify({"error": "AI configuration error."}), 500

    data = request.get_json(silent=True)
    user_question = data.get('question', '').strip()
    
    if not user_question:
        return jsonify({"error": "Empty question."}), 400

    try:
        # 1. Apply Preprocessing (Requirement)
        processed_tokens = preprocess_text(user_question)

        # 2. Query AI
        model_name, response = generate_with_fallback(user_question, model_candidates)
        ai_answer = extract_response_text(response)
        
        if not ai_answer: ai_answer = "No response."

        # 3. Store in DB
        try:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO history (question, answer) VALUES (?, ?)", (user_question, ai_answer))
                conn.commit()
        except Exception:
            pass

        # Return both Answer AND Processed Tokens
        return jsonify({
            "status": "success",
            "processed_tokens": processed_tokens, # New field for Frontend
            "answer": ai_answer,
            "model": model_name
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))