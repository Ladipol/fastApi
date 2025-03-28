# Import necessary modules from FastAPI for handling HTTP exceptions, query parameters, status codes, API routing, and dependencies
from fastapi import HTTPException, Query, status, APIRouter, Depends

# Import Annotated from typing for adding metadata to function parameters
from typing import Annotated

# Import select from sqlmodel for building SQL queries
from sqlmodel import select

# Import UserPublic and UserCreate schemas for input/output validation
from ..schema import UserPublic, UserCreate

# Import Users model for database operations
from ..models import Users

# Import get_password_hash utility for hashing passwords
from ..utils import get_password_hash

# Import SessionDep for database session dependency
from ..database import SessionDep

# Import get_current_user for authentication
from ..config import get_current_user

# Create an APIRouter instance with prefix and tags for Swagger documentation
router = APIRouter(prefix="/users", tags=["Users"])


# Define a POST endpoint to create a new user with status code 201 (Created)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    # Hash the user's password for secure storage
    hashed_password = get_password_hash(user.password)
    # Update the user's password with the hashed value
    user.password = hashed_password

    # Validate and create a new Users model instance
    db_user = Users.model_validate(user)
    # Add the new user to the database session
    session.add(db_user)
    # Commit the transaction to save the user
    session.commit()
    # Refresh the session to get the updated user instance
    session.refresh(db_user)
    # Return the created user
    return db_user


# Define a GET endpoint to read multiple users
@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    # Execute a query to get users with pagination
    users = session.exec(select(Users).offset(offset).limit(limit)).all()
    # Return the list of users
    return users


# Define a GET endpoint to read a single user by ID
@router.get("/{user_id}", response_model=UserPublic)
def read_user(
    user_id: int, session: SessionDep, current_user: Users = Depends(get_current_user)
):
    # Get the user from the database by ID
    user = session.get(Users, user_id)
    # Raise 404 if user not found
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with user_id of {user_id} not found"
        )
    # Raise 403 if current user is not the owner
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Return the user if all checks pass
    return user
