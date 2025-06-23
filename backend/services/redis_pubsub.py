import redis
from backend.core.config import REDIS_URL

redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

def publish_notification(user_id, message):
    redis_client.publish(f"user_{user_id}_notifications", message)
