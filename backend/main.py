from fastapi import FastAPI
from backend.api.routes import (
    authentication,
    create,
    read,
    update,
    delete
)
from backend.api import schemas
from backend.db import models
from backend.services.notifications import NotificationService
from backend.services.search import TopicTrie, TopicRanker
from backend.db.database import get_db
import logging
from backend.db import crud
from strawberry.fastapi import GraphQLRouter
from backend.graphql.schema import schema
from contextlib import asynccontextmanager

# Initialize FastAPI app
app = FastAPI(title="Discussion Forum API", version="1.0")

from fastapi.middleware.cors import CORSMiddleware

# Add this right after creating your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize services
topic_trie = TopicTrie()
topic_ranker = TopicRanker()
notification_service = NotificationService()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Include GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Include all routers with tags
app.include_router(
    authentication.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    create.router,
    prefix="",
    tags=["Create"]
)

app.include_router(
    read.router,
    prefix="",
    tags=["Read"]
)

app.include_router(
    update.router,
    prefix="",
    tags=["Update"]
)

app.include_router(
    delete.router,
    prefix="",
    tags=["Delete"]
)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting application and loading topics into trie")
    db = next(get_db())
    try:
        all_topics = db.query(models.Topic).all()
        logging.info(f"Found {len(all_topics)} topics in database")

        for topic in all_topics:
            try:
                topic_trie.insert(topic.title, topic.id)
                logging.info(f"Loaded topic '{topic.title}' with ID {topic.id} into trie")
            except Exception as e:
                logging.error(f"Error loading topic into trie: {str(e)}")
    except Exception as e:
        logging.error(f"Error loading topics from database: {str(e)}")
    finally:
        db.close()

    # Yield control to the application
    yield

    # Perform cleanup actions here if needed
    logging.info("Shutting down application")

# Attach the lifespan context manager to the app
app.router.lifespan_context = lifespan

# Run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    logging.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
