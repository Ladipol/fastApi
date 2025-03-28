from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import inspect
from .routers import posts, users, auth, votes
from .database import create_db_and_tables, engine


inspector = inspect(engine)

table_names = inspector.get_table_names()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if "users" in table_names and "post" in table_names and "vote" in table_names:
        print("Database and tables already exist. Connecting...")
    else:
        print("Database or tables do not exist. Creating...")
    create_db_and_tables()
    print("Database and tables created.")

    yield
    # Shutdown
    print("Application shutting down. Closing database connection.")
    engine.dispose()
    print("Database connection closed.")


app: FastAPI = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(users.router)
app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(votes.router)
