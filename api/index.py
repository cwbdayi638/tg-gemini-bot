from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import requests
from functools import wraps
import threading
import logging

from .handle import handle_message
from .config import STATIC_DIR, API_ACCESS_TOKEN, HF_SPACE_URL

app = Flask(__name__)
logger = logging.getLogger(__name__)


def ping_hf_space():
    """Ping Hugging Face Space to prevent it from sleeping.
    
    This function sends a simple GET request to the configured HF Space URL
    to keep it awake when using free HF Spaces.
    """
    if HF_SPACE_URL:
        try:
            response = requests.get(HF_SPACE_URL, timeout=10)
            response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
            logger.info(f"HF Space ping successful: {HF_SPACE_URL} (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"HF Space ping failed: {e}")


# Ping HF Space on module load to prevent sleeping
# Using a daemon thread to avoid blocking the application startup
threading.Thread(target=ping_hf_space, daemon=True).start()


def require_token(f):
    """Decorator to require authentication token for API endpoints
    
    Supports both x-access-token (custom) and X-Telegram-Bot-Api-Secret-Token (Telegram standard) headers.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If API_ACCESS_TOKEN is not set, skip authentication
        if not API_ACCESS_TOKEN:
            return f(*args, **kwargs)
        
        # Check for token in headers (support both custom and Telegram's secret token header)
        token = request.headers.get('x-access-token') or request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        
        if not token or token != API_ACCESS_TOKEN:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing authentication token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=["POST", "GET"])
@require_token
def home():
    if request.method == "POST":
        update = request.json
        handle_message(update)
        return "ok"
    return render_template("status.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files (e.g., generated earthquake maps)."""
    return send_from_directory(STATIC_DIR, filename)
