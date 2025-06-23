# from fastapi import Depends, HTTPException, Security
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from backend.database import get_db
# from backend.auth.firebase_auth import validate_firebase_token
# from backend.notifications import NotificationService
# from backend.search import TopicTrie, TopicRanker
# from typing import Generator

# # Initialize services
# security = HTTPBearer()
# topic_trie = TopicTrie()
# topic_ranker = TopicRanker()
# notification_service = NotificationService()

# def get_db_session() -> Generator[Session, None, None]:
#     """
#     Database session dependency that yields a SQLAlchemy session.
#     Properly handles session cleanup after the request is complete.
#     """
#     db = next(get_db())
#     try:
#         yield db
#     finally:
#         db.close()
# 
# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Security(security), 
#     token: str = None
# ):
#     if credentials:
#         token = credentials.credentials
    
#     if not token:
#         raise HTTPException(status_code=403, detail="Token required")

#     user = validate_firebase_token(token)
#     if not user:
#         raise HTTPException(status_code=403, detail="Invalid authentication credentials")
#     return user




# from fastapi import Depends, HTTPException, Security, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# import logging
# from typing import Generator, Optional
# from backend.database import get_db
# from backend.auth.firebase_auth import validate_firebase_token
# from backend.notifications import NotificationService
# from backend.search import TopicTrie, TopicRanker
# from backend import models

# # Initialize services
# security = HTTPBearer()
# topic_trie = TopicTrie()
# topic_ranker = TopicRanker()
# notification_service = NotificationService()
# logger = logging.getLogger(__name__)

# def get_db_session() -> Generator[Session, None, None]:
#     """
#     Database session dependency that yields a SQLAlchemy session.
#     Properly handles session cleanup after the request is complete.
#     """
#     db = next(get_db())
#     try:
#         yield db
#     finally:
#         db.close()

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Security(security),
#     db: Session = Depends(get_db_session)
# ) -> dict:
#     """
#     Enhanced current user dependency that:
#     1. Validates Firebase token
#     2. Maps Firebase UID to local database user
#     3. Returns combined user data
#     """
#     try:
#         # Extract token from credentials
#         token = credentials.credentials if credentials else None
#         if not token:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Authentication token required"
#             )

#         # Validate Firebase token
#         firebase_user = validate_firebase_token(token)
#         if not firebase_user or "uid" not in firebase_user:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid authentication credentials"
#             )

#         # Get local database user
#         db_user = db.query(models.User).filter(
#             models.User.firebase_uid == firebase_user["uid"]
#         ).first()

#         if not db_user:
#             logger.error(f"No local user found for Firebase UID: {firebase_user['uid']}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found in local database"
#             )

#         # Return combined user data
#         return {
#             "firebase_uid": firebase_user["uid"],
#             "id": db_user.id,
#             "email": firebase_user.get("email"),
#             "name": db_user.username,
#             "is_admin": getattr(db_user, "is_admin", False),
#             # Include any other relevant fields
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in get_current_user: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error authenticating user"
#         )
    
# # Export all dependencies and services
# __all__ = [
#     'get_db_session',
#     'get_current_user',
#     'security',
#     'topic_trie',
#     'topic_ranker', 
#     'notification_service'
# ]

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.auth.firebase_auth import validate_firebase_token
from backend.services.notifications import NotificationService
from backend.services.search import TopicTrie, TopicRanker
from typing import Generator

# Initialize services
security = HTTPBearer()
topic_trie = TopicTrie()
topic_ranker = TopicRanker()
notification_service = NotificationService()

def get_db_session() -> Generator[Session, None, None]:
    """
    Database session dependency that yields a SQLAlchemy session.
    Properly handles session cleanup after the request is complete.
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security), 
    token: str = None
):
    if credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=403, detail="Token required")

    user = validate_firebase_token(token)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")
    return user

# Export all dependencies and services
__all__ = [
    'get_db_session',
    'get_current_user',
    'security',
    'topic_trie',
    'topic_ranker', 
    'notification_service'
]
