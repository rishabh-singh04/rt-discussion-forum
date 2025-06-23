# from fastapi import FastAPI, Depends, HTTPException, Security, Query
# from sqlalchemy.orm import Session
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import requests
# from pydantic import BaseModel

# # Importing required modules
# from backend.auth.firebase_auth import get_current_user, generate_firebase_token
# from backend import crud, models, schemas
# from backend.database import engine, get_db
# from backend.search import TopicTrie, TopicRanker
# from backend.notifications import NotificationService

# # Initialize FastAPI app and services
# app = FastAPI(title="Discussion Forum API", version="1.0")
# security = HTTPBearer()
# topic_trie, topic_ranker, notification_service = TopicTrie(), TopicRanker(), NotificationService()

# # Create database tables
# models.Base.metadata.create_all(bind=engine)

# # Pydantic model for login request
# class LoginRequest(BaseModel):
#     email: str
#     password: str

# # Firebase Web API Key (Replace with your actual API key)
# FIREBASE_WEB_API_KEY = "YOUR_FIREBASE_WEB_API_KEY"

# @app.post("/topics", response_model=schemas.Topic)
# def create_topic(topic: schemas.TopicCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
#     """Create a new discussion topic."""
#     db_user = db.query(models.User).filter(models.User.firebase_uid == current_user).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     new_topic = crud.create_topic(db, topic, db_user.id)
#     db.commit()
#     topic_trie.insert(new_topic.title, new_topic.id)

#     return new_topic

# @app.post("/comments/{topic_id}", response_model=schemas.Comment)
# def create_comment(topic_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
#     """Add a comment to an existing topic."""
#     db_user = db.query(models.User).filter(models.User.firebase_uid == current_user).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     db_topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
#     if not db_topic:
#         raise HTTPException(status_code=404, detail="Topic not found")

#     db_comment = crud.create_comment(db, comment, topic_id, db_user.id)
#     db.commit()
    
#     notification_service.publish_comment_notification(topic_id, {"id": db_comment.id, "content": db_comment.content, "author_id": db_comment.author_id})
    
#     return db_comment

# @app.get("/search", response_model=list[schemas.Topic])
# def search_topics(query: str, db: Session = Depends(get_db)):
#     """Search for topics using keyword-based matching."""
#     topic_ids = topic_trie.search(query)
#     if not topic_ids:
#         raise HTTPException(status_code=404, detail="No topics found")

#     return db.query(models.Topic).filter(models.Topic.id.in_(topic_ids)).all()

# @app.get("/notifications")
# def get_notifications(current_user: str = Depends(get_current_user)):
#     """Retrieve notifications for the authenticated user."""
#     return {"message": "Notifications endpoint (to be implemented)"}

# @app.get("/protected")
# def protected_route(credentials: HTTPAuthorizationCredentials = Security(security)):
#     """Test route for Firebase authentication."""
#     token = credentials.credentials
#     user = get_current_user(token)
#     if not user:
#         raise HTTPException(status_code=403, detail="Invalid token")

#     return {"message": "Access granted", "user": user}

# @app.get("/generate-token", tags=["Authentication"], include_in_schema=True)
# def generate_token(uid: str = Query(..., description="Firebase user UID")):
#     """Generate a Firebase token using a UID."""
#     token = generate_firebase_token(uid)
#     if not token:
#         raise HTTPException(status_code=400, detail="Failed to generate token")

#     return {"firebase_token": token}

# @app.post("/get-firebase-token", tags=["Authentication"], include_in_schema=True)
# def get_firebase_token(login_data: LoginRequest):
#     """Authenticate user with email & password and return Firebase token."""
#     # url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
#     # response = requests.post(url, json={"email": login_data.email, "password": login_data.password, "returnSecureToken": True})
    
#     # data = response.json()
#     # if "idToken" not in data:
#     #     raise HTTPException(status_code=400, detail="Invalid email or password")

#     # return {"firebase_token": data["idToken"]}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



@app.post("/topics", response_model=schemas.Topic, dependencies=[Security(security)])
# def create_topic(
#     topic: schemas.TopicCreate,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user),
# ):
#     # Debugging: Print the current_user structure
#     print("DEBUG: current_user =", current_user)

#     # Ensure firebase_uid is extracted properly
#     firebase_uid = current_user.get("user_id")  # Extract user_id from the dictionary
#     print("DEBUG: firebase_uid =", firebase_uid) 
#     print("current_user[user_id] : ", current_user["user_id"])
#     # print("models.User.firebase_uid : ", models.User.firebase_uid)
#     db_user = db.query(models.User).filter(models.User.firebase_uid == current_user.get("user_id")).first()
#     logger.debug(f"Database user: {db_user}")

#     if db_user:
#         print(f"User found: {db_user}")
#     else:
#         print("User not found in DB.")


#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Ensure that the author_id passed is valid
#     if topic.author_id != db_user.id:
#         raise HTTPException(status_code=400, detail="Author ID does not match the current user")
    
#     new_topic = models.Topic(title=topic.title, content=topic.content, author_id=db_user.id)
#     db.add(new_topic)
#     db.commit()
#     db.refresh(new_topic)

#     try:
#         topic_trie.insert(new_topic.title, new_topic.id)
#         logging.info(f"Successfully inserted topic '{new_topic.title}' with ID {new_topic.id} into trie")
#     except Exception as e:
#         logging.error(f"Error inserting topic into trie: {str(e)}")
    
#     return new_topic
