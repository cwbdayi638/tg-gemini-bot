import requests
import time

TOKEN_URL = "https://oauth2.googleapis.com/token"
CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
CLIENT_SECRET = "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"

class TokenManager:
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token
        self.access_token = None
        self.expires_at = 0

    def get_access_token(self):
        if self.access_token and time.time() < self.expires_at - 60:
            return self.access_token

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(TOKEN_URL, data=data)
            response.raise_for_status()
            tokens = response.json()
            
            self.access_token = tokens["access_token"]
            # Default to 1 hour expiry if not provided
            expires_in = tokens.get("expires_in", 3600)
            self.expires_at = time.time() + expires_in
            
            return self.access_token
        except Exception as e:
            print(f"Error refreshing token: {e}")
            raise
