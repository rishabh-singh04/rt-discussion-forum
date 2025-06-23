# backend/crud.py
from sqlalchemy.orm import Session
from backend.db import models
from typing import List

from backend.api import schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        firebase_uid=user.firebase_uid,
        username=user.username,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_topic(db: Session, topic: schemas.TopicCreate, author_id: int):
    db_topic = models.Topic(
        **topic.dict(),
        author_id=author_id
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def create_comment(db: Session, comment: schemas.CommentCreate, 
                   topic_id: int, author_id: int):
    db_comment = models.Comment(
        **comment.dict(),
        topic_id=topic_id,
        author_id=author_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_topics(db: Session, skip: int = 0, limit: int = 100) -> List[models.Topic]:
    return db.query(models.Topic).offset(skip).limit(limit).all()

def get_comments_by_topic(db: Session, topic_id: int) -> List[models.Comment]:
    return db.query(models.Comment).filter(
        models.Comment.topic_id == topic_id
    ).all()

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False
