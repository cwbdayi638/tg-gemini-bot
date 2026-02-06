import hashlib
import os
import base64
import requests
import secrets

# Constants from OpenClaw reference
CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:51121/oauth-callback"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = [
  "https://www.googleapis.com/auth/cloud-platform",
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/userinfo.profile",
  "https://www.googleapis.com/auth/cclog",
  "https://www.googleapis.com/auth/experimentsandconfigs",
]

def generate_pkce():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
    return verifier, challenge

def get_auth_url(challenge):
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent"
    }
    req = requests.Request('GET', AUTH_URL, params=params)
    return req.prepare().url

def exchange_code(code, verifier):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()

def main():
    print("--- Antigravity Config Helper ---")
    print("This script will help you generate the ANTIGRAVITY_KEY (Refresh Token).")
    
    verifier, challenge = generate_pkce()
    auth_url = get_auth_url(challenge)
    
    print("\n1. Go to the following URL in your browser:")
    print("-" * 20)
    print(auth_url)
    print("-" * 20)
    
    print("\n2. Log in with your Google account and approve the permissions.")
    print("3. You will be redirected to a 'localhost' URL (which might fail to load).")
    print("4. Copy the ENTIRE URL from your browser's address bar and paste it below.")
    
    redirect_url = input("\nPaste the full redirected URL here: ").strip()
    
    try:
        # Extract code from URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        
        if 'code' not in params:
            print("Error: Could not find 'code' in the pasted URL.")
            return

        code = params['code'][0]
        print("\nExchanging code for tokens...")
        
        tokens = exchange_code(code, verifier)
        
        if 'refresh_token' in tokens:
            print("\nSUCCESS! Here is your ANTIGRAVITY_KEY:")
            print("-" * 40)
            print(tokens['refresh_token'])
            print("-" * 40)
            print("\nAdd this to your environment variables or .env file:")
            print(f"ANTIGRAVITY_KEY={tokens['refresh_token']}")
        else:
            print("\nFailed to get refresh token.")
            print("Response:", tokens)
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
