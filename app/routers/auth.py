# Import necessary modules from FastAPI for API routing, dependencies, status codes, HTTP exceptions, and responses
from fastapi import APIRouter, Depends, status, HTTPException, Response

# Import SQLModel functionality for database queries
from sqlmodel import select, Session

# Import OAuth2 password request form for handling login data
from fastapi.security import OAuth2PasswordRequestForm

# Import the Users model for database interactions
from ..models import Users

# Import utility functions for password verification and token creation
from ..utils import verify_password

# Import configuration for database session management
from ..config import get_session, create_access_token


# Import the Token schema for response modeling
from ..schema import Token

# Create an API router with a tag for authentication-related endpoints
router = APIRouter(tags=["Authentication"])


# Define a POST endpoint for user login with a 200 status code and Token response model
@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
def login(
    # Use OAuth2PasswordRequestForm to handle username and password from request form data
    user: OAuth2PasswordRequestForm = Depends(),
    # Get database session using dependency injection
    session: Session = Depends(get_session),
    # Access response object to set cookies
    response: Response = Response(),
):
    # Query the database for a user with the provided email
    statement = select(Users).where(Users.email == user.username)
    # Execute the query and get the first result
    user_db = session.exec(statement).first()

    # Check if user exists in the database
    if not user_db:
        # Raise HTTP exception for invalid credentials if user not found
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    # Verify the provided password against the stored password
    if not verify_password(user.password, user_db.password):
        # Raise HTTP exception for invalid credentials if password mismatch
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    # Create an access token with user ID (replacing "sub" with "id" in data)
    access_token = create_access_token(data={"id": user_db.id})
    # Set the access token as a cookie in the HTTP response
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    # Return the access token and token type in the response body
    return {"access_token": access_token, "token_type": "bearer"}
