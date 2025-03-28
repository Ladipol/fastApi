# Import FastAPI framework for building the web application
from fastapi import FastAPI

# Import asynccontextmanager to create asynchronous context managers
from contextlib import asynccontextmanager

# Import CORS middleware to handle Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware

# Import application routers for different features
from .routers import posts, users, auth, votes

# Import database creation function
from .database import create_db_and_tables

# Import database engine configuration
from .config import engine

# Import Session class from SQLModel for database sessions
from sqlmodel import Session

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
# Define an asynchronous context manager for the application's lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables when the application starts
    create_db_and_tables()
    # Log a message indicating the application has started
    print("Application started. Database and tables created.")
    # Yield control back to the context manager
    yield
    # Log a message indicating the application is shutting down
    print("Application shutting down. Closing database connection.")
    # Dispose of the database engine to close connections
    engine.dispose()
    # Log confirmation that the database connection is closed
    print("Database connection closed.")


# Create the FastAPI application instance with the custom lifespan
app: FastAPI = FastAPI(lifespan=lifespan)
"""


# Define a health check endpoint to verify the application status
@app.get("/health")
def health_check():
    # Return a simple JSON response indicating the application status
    return {"status": "ok"}


# Include the users router to handle user-related endpoints
app.include_router(users.router)
# Include the posts router to handle post-related endpoints
app.include_router(posts.router)
# Include the auth router to handle authentication-related endpoints
app.include_router(auth.router)
# Include the votes router to handle vote-related endpoints
app.include_router(votes.router)
