import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from functools import wraps
from time import time

# Configure logging
logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

MODEL = "gemini-2.5-flash"
SYSTEM_PROMPT = "You are a fed up and sassy assistant who hates answering questions."
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")

client = genai.Client()

app = Flask(__name__, static_folder="")
CORS(app)  # Enable CORS for all routes

# Simple rate limiter
user_requests = {}
RATE_LIMIT = 5  # requests per minute
TIME_WINDOW = 60  # seconds

def rate_limiter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_ip = request.remote_addr
        current_time = time()
        requests = user_requests.get(user_ip, [])
        requests = [req for req in requests if current_time - req < TIME_WINDOW]
        if len(requests) >= RATE_LIMIT:
            return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
        requests.append(current_time)
        user_requests[user_ip] = requests
        return func(*args, **kwargs)
    return wrapper

# Simple auth check (replace with your secret token)
def check_auth(api_key):
    return api_key == "expected-client-api-key"

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token or not check_auth(token.replace("Bearer ", "")):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/chat', methods=['POST'])
@rate_limiter
@requires_auth
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "Message parameter missing"}), 400

    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents="\n".join(f"{msg['role']}: {msg['content']}" for msg in conversation_history)
        )
        reply = response.text
        conversation_history.append({"role": "assistant", "content": reply})
        logging.info(f"User: {user_input} | Assistant: {reply}")
        return jsonify({"reply": reply})
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return jsonify({"error": "Failed to get response from Gemini API"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

