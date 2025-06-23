import strawberry
from strawberry.types import Info
from backend.db import models
from backend.api.dependencies import get_db
from sqlalchemy.orm import Session
from backend.graphql.types.user_type import UserType
from fastapi import HTTPException

@strawberry.input
class UserUpdateInput:
    username: str | None = None
    email: str | None = None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_user(self, info: Info, user_id: int, input: UserUpdateInput) -> UserType:
        try:
            db: Session = next(get_db())
            db_user = db.query(models.User).filter(models.User.id == user_id).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            if input.username:
                db_user.username = input.username
            if input.email:
                db_user.email = input.email
            
            db.commit()
            db.refresh(db_user)

            return UserType(id=db_user.id, username=db_user.username, email=db_user.email)

        except Exception as e:
            print("GraphQL Error:", e)
            raise Exception("Failed to update user. Please check the logs.")