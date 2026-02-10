from flask import Flask, render_template, request, send_from_directory, jsonify
import os
from functools import wraps

from .handle import handle_message
from .config import STATIC_DIR, API_ACCESS_TOKEN

app = Flask(__name__)


def require_token(f):
    """Decorator to require x-access-token header for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If API_ACCESS_TOKEN is not set, skip authentication
        if not API_ACCESS_TOKEN:
            return f(*args, **kwargs)
        
        # Check for x-access-token in headers
        token = request.headers.get('x-access-token')
        
        if not token or token != API_ACCESS_TOKEN:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing x-access-token'}), 401
        
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
