# app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from pydantic import field_validator, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class LoginRequest(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    firebase_uid: str

class User(UserBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class TopicBase(BaseModel):
    title: str
    content: str

class TopicCreate(BaseModel):
    title: str
    content: str
    author_id: int

    class Config:
        from_attributes = True  # Updated from `orm_mode`

# Define the response model if needed
class TopicResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime

class Topic(TopicBase):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    comments: List['Comment'] = []

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    topic_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Pydantic model to define the notification structure for Swagger.
class Notification(BaseModel):
    message: str
    topic_id: Optional[int] = None  # Optional field for topic context
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Example for Swagger UI
    class Config:
        json_schema_extra = {
            "example": {
                "message": "New comment on your post",
                "topic_id": 1,
                "created_at": "2023-01-01T00:00:00Z"
            }
        }

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        extra = "forbid"  # Prevent extra fields