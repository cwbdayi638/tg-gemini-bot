import os
import requests
import json
import time

# Constants
TOKEN_URL = "https://oauth2.googleapis.com/token"
CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
CLIENT_SECRET = "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"
BASE_URL = "https://cloudcode-pa.googleapis.com"
LOAD_CODE_ASSIST_PATH = "/v1internal:loadCodeAssist"

# Get Refresh Token from environment
REFRESH_TOKEN = os.environ.get("ANTIGRAVITY_KEY")

if not REFRESH_TOKEN:
    print("Error: ANTIGRAVITY_KEY not found in environment.")
    exit(1)

def get_access_token(refresh_token):
    print("Refreshing access token...")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def discover_project(access_token):
    print("Calling loadCodeAssist...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
        "User-Agent": "antigravity"
    }
    # From openclaw metadata
    payload = {
        "metadata": {
            "ideType": "ANTIGRAVITY",
            "platform": "PLATFORM_UNSPECIFIED",
            "pluginType": "GEMINI"
        }
    }
    response = requests.post(f"{BASE_URL}{LOAD_CODE_ASSIST_PATH}", headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    print("\nFull Response:")
    print(json.dumps(data, indent=2))
    
    project = data.get("cloudaicompanionProject")
    if not project:
        print("\nProject ID NOT found in response.")
        return None
    
    if isinstance(project, str):
        project_id = project
    else:
        project_id = project.get("id")
        
    print(f"\nDISCOVERED PROJECT ID: {project_id}")
    return project_id

try:
    access_token = get_access_token(REFRESH_TOKEN)
    discover_project(access_token)
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
