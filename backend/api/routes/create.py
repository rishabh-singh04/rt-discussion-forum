from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from backend.api.dependencies import get_db, get_current_user
from backend.db import crud
from backend.api import schemas
from backend.db import models
from backend.services.search import topic_trie
from backend.services.notifications import notification_service
from backend.api.dependencies import (
    get_db_session as get_db,
    get_current_user,
    topic_trie,
    notification_service
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/topics", response_model=schemas.Topic)
async def create_topic(
    topic: schemas.TopicCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    logging.debug(f"DEBUG: current_user = {current_user}")
    firebase_uid = current_user.get("user_id")
    logging.debug(f"DEBUG: firebase_uid = {firebase_uid}")
    
    db_user = db.query(models.User).filter(models.User.firebase_uid == current_user.get("user_id")).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if topic.author_id != db_user.id:
        raise HTTPException(status_code=400, detail="Author ID does not match the current user")
    
    new_topic = models.Topic(title=topic.title, content=topic.content, author_id=db_user.id)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    logging.info(f"Created new topic: id={new_topic.id}, title='{new_topic.title}'")

    try:
        topic_trie.insert(new_topic.title, new_topic.id)
        logging.info(f"Inserted topic '{new_topic.title}' with ID {new_topic.id} into trie")
    except Exception as e:
        logging.error(f"Error inserting topic into trie: {str(e)}")
    
    try:
        subscribers = db.query(models.Subscription).filter_by(category_id=new_topic.category_id).all()
        for subscriber in subscribers:
            notification_service.send_notification(
                subscriber.user_id,
                f"New topic '{new_topic.title}' was created in a category you follow."
            )
        logging.info(f"Notifications sent to {len(subscribers)} subscribers")
    except Exception as e:
        logging.error(f"Error sending notifications: {str(e)}")

    return new_topic

@router.post("/comments/{topic_id}", response_model=schemas.Comment)
def create_comment(
    topic_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_user = db.query(models.User).filter(models.User.firebase_uid == current_user["uid"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db_comment = crud.create_comment(db, comment, topic_id, db_user.id)
    db.commit()
    db.refresh(db_comment)

    notification_service.send_notification(
        user_id=db_topic.author_id,
        message=f"User {db_user.username} added a comment on your topic '{db_topic.title}'",
        topic_id=topic_id
    )

    logging.info(f"Notification sent to user {db_topic.author_id}")
    notification_service.publish_comment_notification(
        topic_id,
        {"id": db_comment.id, "content": db_comment.content, "author_id": db_comment.author_id},
    )

    return db_comment
