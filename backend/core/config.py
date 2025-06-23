from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:1234@localhost/discussion_forum"
    FIREBASE_CONFIG_PATH: str = "backend/firebase-private-key.json"
    FIREBASE_WEB_API_KEY: str = "AIzaSyBcmeWI2m7RpSB1ScUKdnAxpc34GwDL5EU"
    REDIS_URL: str = "redis://localhost:6379"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672"

settings = Settings()
