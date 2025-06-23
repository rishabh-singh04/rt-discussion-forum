from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import requests
import logging
from datetime import datetime
from backend.api.dependencies import get_db
from backend.api.schemas import SignupRequest, LoginRequest
from backend.db import models
from backend.core.config import settings
from backend.services.notifications import NotificationService
from backend.services.search import TopicTrie, TopicRanker

from backend.api.dependencies import (
    get_db_session as get_db,
    get_current_user,
    security
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """Sign up a new user and return a Firebase token."""
    try:
        logger.info(f"Starting signup process for {user_data.email}")
        
        # 1. Check if user already exists in our DB
        existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
        if existing_user:
            logger.warning(f"User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # 2. Create Firebase account
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={settings.FIREBASE_WEB_API_KEY}"
        payload = {
            "email": user_data.email,
            "password": user_data.password,
            "returnSecureToken": True
        }
        
        logger.debug(f"Sending request to Firebase: {url}")
        response = requests.post(url, json=payload)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get("error", {}).get("message", "Unknown Firebase error")
            logger.error(f"Firebase signup failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Firebase error: {error_msg}"
            )

        firebase_uid = data["localId"]
        firebase_token = data["idToken"]
        logger.info(f"Firebase user created: {firebase_uid}")

        # 3. Create local database user
        db_user = models.User(
            firebase_uid=firebase_uid,
            username=user_data.display_name,
            email=user_data.email
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Database user created with ID: {db_user.id}")

        return {
            "firebase_token": firebase_token,
            "user_id": db_user.id,
            "email": user_data.email,
            "display_name": user_data.display_name
        }

    except HTTPException:
        # Re-raise HTTP exceptions we created
        raise
    except Exception as e:
        logger.error(f"Unexpected signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during signup"
        )
        
@router.post("/login")
def get_firebase_token(login_data: LoginRequest):
    """Authenticate user with email & password and return Firebase token."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}"
    response = requests.post(url, json={
        "email": login_data.email,
        "password": login_data.password,
        "returnSecureToken": True
    })

    data = response.json()
    if "idToken" not in data:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    myfirebasetoken = data["idToken"]
    logger.info(f"myfirebasetoken: {myfirebasetoken}")
    return {"firebase_token": myfirebasetoken}

@router.get("/me")
def get_current_user_details(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "bio": current_user.get("bio", ""),
        "createdAt": datetime.utcnow().isoformat(),
        "profilePicture": current_user.get("profile_picture", "")
    }
