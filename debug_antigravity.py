import os
import requests
import json
import google.auth
from google.auth.transport.requests import Request

# Load token from file or env (assuming env is set or we use library)
# For this script we need the token.
# Helper function to get token (copying from earlier scripts logic simplified)

def get_token():
    # If we have the token in a file "antigravity_token.json", usage it
    if os.path.exists("antigravity_token.json"):
        with open("antigravity_token.json") as f:
            data = json.load(f)
            return data.get("access_token")
    
    # Fallback: Use default credentials if available (e.g. gcloud auth application-default login)
    try:
        creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(Request())
        return creds.token
    except Exception as e:
        print(f"Could not get default credentials: {e}")
        return None

token = get_token()
if not token:
    print("FATAL: No token found. Please run get_antigravity_token.py or set up application default credentials.")
    exit(1)

print(f"Got Token: {token[:10]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 5. Testing Vertex AI (Standard Host)
print("\n--- 5. Testing Vertex AI (Standard Host) ---")

# Discovery from earlier: Project ID "cloudaicompanion"
project_ids = ["cloudaicompanion"] 
regions = ["us-central1"]

# Models to try on Vertex
models_vertex = ["gemini-1.5-pro", "gemini-3-pro-high", "gemini-3-pro-preview"]

payload_vertex = {
    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
}

success = False

for pid in project_ids:
    for reg in regions:
        for m in models_vertex:
            url = f"https://{reg}-aiplatform.googleapis.com/v1/projects/{pid}/locations/{reg}/publishers/google/models/{m}:generateContent"
            print(f"\nTesting Vertex: {url}")
            try:
                resp = requests.post(url, headers=headers, json=payload_vertex)
                print(f"  Status: {resp.status_code}")
                if resp.ok:
                    print("  SUCCESS!")
                    print(resp.text[:500])
                    success = True
                    break
                else:
                    print(f"  Error: {resp.status_code}")
                    print(f"  Body: {resp.text[:200]}")
            except Exception as e:
                print(f"  Exception: {e}")
        if success: break
    if success: break
