# backend/notifications.py
import redis
import json
from threading import Thread
from datetime import datetime
from backend.core.config import settings

class NotificationService:
    def __init__(self):
        # Redis for Pub/Sub and storage
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def send_notification(self, user_id: str, message: str, topic_id=None):
        """Publish notification to Redis Pub/Sub and store it."""
        notification = {
            "user_id": user_id,
            "message": message,
            "topic_id": topic_id,
            "created_at": datetime.utcnow().isoformat()
        }

        # Publish to Redis Pub/Sub
        self.redis_client.publish(f"user:{user_id}:notifications", json.dumps(notification))

        # Save in Redis list (Latest 20 notifications)
        self.redis_client.lpush(f"user:{user_id}:notifications_list", json.dumps(notification))
        self.redis_client.ltrim(f"user:{user_id}:notifications_list", 0, 19)

    def get_notifications(self, user_id: str):
        """Retrieve stored notifications from Redis."""
        notifications = self.redis_client.lrange(f"user:{user_id}:notifications_list", 0, -1)
        return [json.loads(notif) for notif in notifications] if notifications else []

    def subscribe_to_notifications(self, user_id: str):
        """Subscribe to real-time notifications via Redis Pub/Sub."""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(f"user:{user_id}:notifications")

        def listen():
            for message in pubsub.listen():
                if message["type"] == "message":
                    print(f"New Notification for {user_id}: {message['data']}")

        thread = Thread(target=listen, daemon=True)
        thread.start()
        return pubsub
    
    def publish_comment_notification(self, topic_id: int, comment_data: dict):
        """Publishes a comment notification to a Redis Pub/Sub channel."""
        self.redis_client.publish(f"topic:{topic_id}:comments", json.dumps(comment_data))

    def subscribe_to_topic(self, topic_id: int):
        """Subscribes to a topic to receive real-time notifications."""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(f"topic:{topic_id}:comments")
        return pubsub

# Initialize the service instance here
notification_service = NotificationService()

__all__ = ['NotificationService', 'notification_service']