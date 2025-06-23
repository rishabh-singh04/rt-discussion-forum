import firebase_admin
from firebase_admin import credentials, auth
import os
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.config import settings

# Security scheme for token authentication
security = HTTPBearer()

# Initialize Firebase Admin SDK only once
if not firebase_admin._apps:
    firebase_config_path = settings.FIREBASE_CONFIG_PATH
    if not os.path.exists(firebase_config_path):
        raise ValueError(f"Firebase config file not found: {firebase_config_path}")
    cred = credentials.Certificate(firebase_config_path)
    firebase_admin.initialize_app(cred)

def generate_firebase_token(uid: str):
    """Generate a Firebase custom token for a given user UID."""
    try:
        custom_token = auth.create_custom_token(uid)
        return custom_token  # Already a string, no need to decode
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {str(e)}")

def validate_firebase_token(token: str):
    """Validate a Firebase authentication token and return the decoded user information."""
    try:
        return auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Retrieve the current user's UID from the Firebase token."""
    token = credentials.credentials
    decoded_token = validate_firebase_token(token)

    if not decoded_token or "uid" not in decoded_token:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    return decoded_token["uid"]
