# Import Annotated for type annotations with metadata
from typing import Annotated

# Import Depends for dependency injection in FastAPI
from fastapi import Depends

# Import database engine and session factory from config module
from .config import engine, get_session

# Import SQLModel for database modeling and Session for database sessions
from sqlmodel import SQLModel, Session


# Function to create database and all tables based on SQLModel models
def create_db_and_tables():
    # Create all tables in the database using the engine
    SQLModel.metadata.create_all(engine)


# Create a type hint for Session with dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
