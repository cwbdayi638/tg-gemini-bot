from flask import Flask, render_template, request, send_from_directory
import os

from .handle import handle_message
from .config import STATIC_DIR

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
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
