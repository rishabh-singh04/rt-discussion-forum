from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db, get_current_user
from backend.db import models
from backend.api.dependencies import (
    get_db_session as get_db,
    get_current_user,
    topic_trie,
    notification_service
)

router = APIRouter()

@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db_user = db.query(models.User).filter(models.User.firebase_uid == current_user["uid"]).first()
    if not db_user or db_comment.author_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(db_comment)
    db.commit()
    return Response(status_code=204)

@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    current_db_user = db.query(models.User).filter(models.User.firebase_uid == current_user["uid"]).first()
    if not current_db_user or (current_db_user.id != db_user.id and not current_db_user.is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.query(models.Comment).filter(models.Comment.author_id == user_id).delete()
    db.query(models.Topic).filter(models.Topic.author_id == user_id).delete()
    db.delete(db_user)
    db.commit()
    return Response(status_code=204)