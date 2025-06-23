# backend/auth.py
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from backend.core.config import settings

# Security scheme for token authentication
security = HTTPBearer()

class FirebaseAuth:
    def __init__(self):
        """Initialize Firebase Admin SDK only once."""
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CONFIG_PATH)
            firebase_admin.initialize_app(cred)
    
    def verify_token(self, token: str):
        print(f"🔍 Received Token: {token}")  # Debugging line
        try:
            decoded_token = auth.verify_id_token(token)
            print(f"✅ Decoded Token: {decoded_token}")  # Debugging line
            return decoded_token
        except Exception as e:
            print(f"❌ Error verifying token: {e}")  # Debugging line
            raise HTTPException(status_code=403, detail="Invalid token")
    
    def get_user_id(self, token: str):
        """Extract user ID from verified token."""
        decoded_token = self.verify_token(token)
        return decoded_token.get("uid", None)

# Initialize Firebase authentication
firebase_auth = FirebaseAuth()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency function to retrieve current user ID from Firebase token.
    Used in protected routes.
    """
    token = credentials.credentials
    user_id = firebase_auth.get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=403, detail="User authentication failed")
    return user_id
