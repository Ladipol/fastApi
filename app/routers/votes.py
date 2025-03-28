# Import necessary modules from FastAPI for creating API routes and handling HTTP requests
from fastapi import APIRouter, status, HTTPException, Depends

# Import SQLModel's select function for database queries
from sqlmodel import select

# Import the VoteCreate schema from the schema module
from ..schema import VoteCreate

# Import the configuration for getting the current user
from ..config import get_current_user

# Import the database session dependency
from ..database import SessionDep

# Import the Vote and Post models from the models module
from ..models import Vote, Post

# Create an APIRouter instance with the prefix "/votes" and tag "Vote" for Swagger documentation
router = APIRouter(
    prefix="/votes",
    tags=["Vote"],
)


# Define a POST endpoint for creating votes with a 201 status code
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(
    # The vote data to be created, following the VoteCreate schema
    vote: VoteCreate,
    # The database session to interact with the database
    session: SessionDep,
    # The currently authenticated user (retrieved using get_current_user)
    current_user=Depends(get_current_user),
):

    # Check if there is no current_user, meaning the user is not authenticated
    if not current_user:
        # Raise an HTTPException with a 401 status code if not authenticated
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to vote",
        )

    # Try to get the post from the database using the post_id from the vote data
    post = session.get(Post, vote.post_id)
    # If the post does not exist, raise an HTTPException with a 404 status code
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote.post_id} does not exist",
        )

    # Create a SQL query to check if the user has already voted on this post
    statement = select(Vote).where(
        Vote.user_id == current_user.id, Vote.post_id == vote.post_id
    )
    # Execute the query and get the first result
    existing_vote = session.exec(statement).first()

    # If the vote direction is 1 (upvote)
    if vote.dir == 1:
        # If there is already an existing vote, raise a 409 conflict error
        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"You have already voted on post {vote.post_id}.",
            )
        # Create a new vote instance with the current user's ID and the post ID
        new_vote = Vote(user_id=current_user.id, post_id=vote.post_id)
        # Add the new vote to the database session
        session.add(new_vote)
        # Commit the transaction to save the vote
        session.commit()
        # Refresh the new_vote object to get the generated database fields
        session.refresh(new_vote)
        # Return a success message with the created vote
        return {"message": "Vote created successfully"}

    # If the vote direction is -1 (downvote)
    else:
        # If there is no existing vote to delete, raise a 404 error
        if not existing_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vote with id {vote.id} does not exist",
            )
        # Delete the existing vote from the database
        session.delete(existing_vote)
        # Commit the transaction to save the deletion
        session.commit()
        # Return a success message after deleting the vote
        return {"message": "Vote deleted successfully"}
