# from fastapi import APIRouter, Depends, HTTPException
# import datetime
# import time
# import redis
# from sqlalchemy.orm import Session
# from backend.api.dependencies import get_db

# from backend import crud, models
# from backend.api.dependencies import (
#     get_db_session as get_db,
#     get_current_user,
#     notification_service,
#     topic_trie
# )
# from backend import models
# from backend.api import schemas

# import logging
# logger = logging.getLogger(__name__)

# router = APIRouter()

# @router.get("/users", response_model=list[schemas.User])
# def get_all_users(db: Session = Depends(get_db)):
#     return db.query(models.User).all()

# @router.get("/users/{user_id}", response_model=schemas.User)
# def get_user(
#     user_id: int, 
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user)  # Add auth
# ):
#     try:
#         user = db.query(models.User).filter(models.User.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         logger.debug(f"Found user: {user.__dict__}")
#         return user
#     except Exception as e:
#         logger.error(f"Error fetching user: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Internal server error")
#     return user

# @router.get("/topics", response_model=list[schemas.Topic])
# def get_all_topics(db: Session = Depends(get_db)):
#     return db.query(models.Topic).all()

# @router.get("/comments/{topic_id}", response_model=list[schemas.Comment])
# def get_comments(topic_id: int, db: Session = Depends(get_db)):
#     comments = db.query(models.Comment).filter(models.Comment.topic_id == topic_id).all()
#     return comments

# @router.get("/search", response_model=list[schemas.Topic])
# def search_topics(query: str, db: Session = Depends(get_db)):
#     topic_ids = topic_trie.search(query)
#     if not topic_ids:
#         like_pattern = f"%{query}%"
#         topics_from_db = db.query(models.Topic).filter(models.Topic.title.ilike(like_pattern)).all()
#         if topics_from_db:
#             return topics_from_db
#         raise HTTPException(status_code=404, detail="No topics found")
#     return db.query(models.Topic).filter(models.Topic.id.in_(topic_ids)).all()

# @router.get("/notifications")
# async def get_notifications(
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Get the local database user
#         db_user = db.query(models.User).filter(
#             models.User.firebase_uid == current_user.get("uid")
#         ).first()
        
#         if not db_user:
#             raise HTTPException(status_code=404, detail="User not found in local database")

#         # Get notifications from Redis
#         notifications = notification_service.get_notifications(db_user.id)
        
#         if notifications is None:
#             return {"notifications": []}

#         # Format notifications with topic details
#         formatted = []
#         for notif in notifications:
#             try:
#                 topic_id = notif.get("topic_id")
#                 topic = db.query(models.Topic).get(topic_id) if topic_id else None
#                 formatted.append({
#                     "id": notif.get("id"),
#                     "message": notif.get("message", "New notification"),
#                     "topic_title": topic.title if topic else "Deleted Topic",
#                     "created_at": notif.get("created_at"),
#                     "read": notif.get("read", False)
#                 })
#             except Exception as e:
#                 logger.error(f"Error formatting notification: {str(e)}")
#                 continue
        
#         return {"notifications": formatted}

#     except redis.exceptions.RedisError as e:
#         logger.error(f"Redis error: {str(e)}")
#         raise HTTPException(
#             status_code=503,
#             detail="Notification service temporarily unavailable"
#         )
#     except Exception as e:
#         logger.error(f"Unexpected error in notifications: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail="Error retrieving notifications"
#         )

from fastapi import APIRouter, Depends, HTTPException
import datetime
import time
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db

from backend.db import crud
from backend.api.dependencies import (
    get_db_session as get_db,
    get_current_user,
    notification_service,
    topic_trie
)
from backend.db import models
from backend.api import schemas

import logging

from backend.db import models
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/users", response_model=list[schemas.User])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth
):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.debug(f"Found user: {user.__dict__}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    return user

@router.get("/topics", response_model=list[schemas.Topic])
def get_all_topics(db: Session = Depends(get_db)):
    return db.query(models.Topic).all()

@router.get("/comments/{topic_id}", response_model=list[schemas.Comment])
def get_comments(topic_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.topic_id == topic_id).all()
    return comments

@router.get("/search", response_model=list[schemas.Topic])
def search_topics(query: str, db: Session = Depends(get_db)):
    topic_ids = topic_trie.search(query)
    if not topic_ids:
        like_pattern = f"%{query}%"
        topics_from_db = db.query(models.Topic).filter(models.Topic.title.ilike(like_pattern)).all()
        if topics_from_db:
            return topics_from_db
        raise HTTPException(status_code=404, detail="No topics found")
    return db.query(models.Topic).filter(models.Topic.id.in_(topic_ids)).all()

@router.get("/notifications")
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get the DB user to ensure proper ID mapping
        db_user = db.query(models.User).filter(
            models.User.firebase_uid == current_user.get("uid")
        ).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        notifications = notification_service.get_notifications(str(db_user.id))
        
        # Format notifications with topic details
        formatted = []
        for notif in notifications:
            topic = db.query(models.Topic).get(notif.get("topic_id"))
            formatted.append({
                "id": notif.get("id"),
                "message": notif.get("message"),
                "topic_title": topic.title if topic else "Deleted Topic",
                "created_at": notif.get("created_at"),
                "read": notif.get("read", False)
            })
        
        return {"notifications": formatted}

    except Exception as e:
        logger.error(f"Notification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving notifications")
