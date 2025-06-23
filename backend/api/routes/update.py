from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db, get_current_user
from backend.db import models
from backend.api.dependencies import (
    get_db_session as get_db,
    get_current_user,
    topic_trie,
    notification_service
)
from backend.api import schemas

router = APIRouter()

@router.patch("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    current_db_user = db.query(models.User).filter(models.User.firebase_uid == current_user["uid"]).first()
    if not current_db_user or current_db_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only update your own account")

    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user