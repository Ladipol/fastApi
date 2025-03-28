# Description: This file contains the configuration for the FastAPI application. It includes the database connection URL, OAuth2 scheme, and functions for creating access tokens, getting a database session, and getting the current authenticated user from the request token. The configuration is loaded from environment variables using pydantic_settings. The file also includes a function to create a JWT access token with expiration, a dependency to get a database session, and a dependency to get the current authenticated user from the request token. The configuration class uses the .env file for environment variables, and the SQLAlchemy engine is created with echo=True for debugging. The file also includes a function to create a JWT access token with expiration, a dependency to get a database session, and a dependency to get the current authenticated user from the request token. The configuration class uses the .env file for environment variables, and the SQLAlchemy engine is created with echo=True for debugging.

from urllib.parse import quote_plus

# Import Annotated type for dependency injection with type hints
from typing import Annotated

# Import OAuth2PasswordBearer for handling password flow with bearer tokens
from fastapi.security import OAuth2PasswordBearer

# Import dependencies for handling HTTP requests and exceptions
from fastapi import Depends, HTTPException, status

# Import JWT library for token creation and validation
import jwt

# Import exception for handling invalid tokens
from jwt.exceptions import InvalidTokenError

# Import datetime and timezone for token expiration handling
from datetime import datetime, timedelta, timezone

# Import BaseSettings for environment configuration
from pydantic_settings import BaseSettings

# Import Session and create_engine from SQLAlchemy for database operations
from sqlmodel import Session, create_engine

# Import Users model for database interactions
from app.models import Users

# Import TokenData schema for token payload validation
from app.schema import TokenData


# Configuration class for environment variables using pydantic_settings
class Settings(BaseSettings):
    # Hostname for the database connection
    database_hostname: str
    # Port for the database connection
    database_port: str
    # Password for the database connection
    database_password: str
    # Name of the database
    database_name: str
    # Username for the database connection
    database_username: str
    # Secret key for JWT token signing
    secret_key: str
    # Algorithm used for JWT signing
    algorithm: str
    # Expiration time in minutes for access tokens
    access_token_expire_minutes: int

    # Configuration class to specify the .env file location
    class Config:
        # Path to the environment file
        env_file = ".env"


# Initialize the settings object
settings = Settings()

# Encode the password here
encoded_password = quote_plus(settings.database_password)

# Create the database connection URL string
DATABASE_URL = f"postgresql://{settings.database_username}:{encoded_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# Create the SQLAlchemy engine with echo=True for debugging
engine = create_engine(DATABASE_URL, echo=True)

# Initialize OAuth2 scheme with token endpoint at "login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Load secret key from settings for JWT operations
SECRET_KEY = settings.secret_key
# Load algorithm from settings for JWT operations
ALGORITHM = settings.algorithm
# Load token expiration time from settings
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# Function to create a JWT access token with expiration
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # Copy the input data to avoid modifying the original
    to_encode = data.copy()

    # Set expiration time based on expires_delta or default
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Validate that user ID is present in the data
    if not data.get("id"):
        raise ValueError("User ID is required to create a token")

    # Add expiration and subject (user ID) to the token payload
    to_encode.update({"exp": expire, "sub": str(data["id"])})

    # Encode the payload to a JWT token using secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependency to get a database session
def get_session():
    # Use context manager to create and yield a new session
    with Session(engine) as session:
        yield session


# Dependency to get the current authenticated user from the request token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session=Depends(get_session)
):
    # Create an HTTP exception for unauthorized access
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Print the token being decoded for debugging purposes
        print(f"Decoding token: {token}")

        # Decode the JWT token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")

        # Extract the user ID from the payload
        id: str = payload.get("sub")

        # Validate that the user ID exists and is a digit
        if id is None or not id.isdigit():
            raise credentials_exception

        # Create a TokenData object with the user ID
        token_data = TokenData(id=int(id))
        print(f"Querying user with ID: {token_data.id}")

        # Query the database for the user with the given ID
        user: str = session.query(Users).filter(Users.id == token_data.id).first()

        # Validate that the user exists in the database
        if user is None:
            print("User not found")
            raise credentials_exception

        # Print the authenticated user's email for debugging
        print(f"Authenticated user: {user.email}")
        return user

    # Catch invalid token errors and raise HTTP exception
    except InvalidTokenError as e:
        print(f"Token error: {e}")
        raise credentials_exception

    # Catch any other exceptions and raise HTTP exception
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise credentials_exception
