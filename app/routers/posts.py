# Import FastAPI modules for handling HTTP exceptions, queries, status codes, routing, and dependencies
from fastapi import HTTPException, Query, status, APIRouter, Depends

# Import typing modules for handling optional and annotated types
from typing import Annotated, Optional

# Import SQLModel modules for database querying and functions
from sqlmodel import select, func

# Import custom modules for database models, schemas, sessions, and authentication
from .. import models, schema
from ..database import SessionDep
from ..config import get_current_user

# Create an APIRouter instance for handling posts-related endpoints
# The prefix "/posts" groups all post-related routes together under this path
# The tags parameter groups the endpoints in the API documentation
router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.PostPublic)
def create_post(
    post: schema.PostCreate,  # The post data to be created
    session: SessionDep,  # Database session dependency
    current_user: models.Users = Depends(
        get_current_user
    ),  # Current authenticated user
):
    # Print the current user's email for debugging purposes
    print(current_user.email)

    # Create a new Post database model with the current user as the owner
    db_post = models.Post(owner_id=current_user.id, **post.model_dump())

    # Add the new post to the database session
    session.add(db_post)

    # Commit the transaction to persist the data
    session.commit()

    # Refresh the model to get the latest data from the database
    session.refresh(db_post)

    # Return the created post with all its data
    return db_post


@router.get("/", response_model=list[schema.PostVote])
def read_posts(
    session: SessionDep,  # Database session dependency
    # current_user: models.Users = Depends(get_current_user),  # [Commented Out] Current authenticated user
    offset: int = 0,  # Pagination offset parameter
    limit: Annotated[int, Query(le=100)] = 100,  # Pagination limit parameter (max 100)
    search: Optional[str] = "",  # Optional search query parameter
):
    # Build the base SQL query to get posts with their vote counts
    query = (
        select(
            models.Post,  # Select the Post model
            func.count(models.Vote.post_id).label("votes"),  # Count votes for each post
        )
        .join(  # Join with the Vote model
            models.Vote,
            models.Vote.post_id == models.Post.id,  # Join condition
            isouter=True,  # Use outer join to include posts with no votes
        )
        .where(  # Apply search filter
            (
                (models.Post.title.like(f"%{search}%"))  # Search in title
                | (models.Post.content.like(f"%{search}%"))  # Search in content
            )
            # [Commented Out] & (models.Post.owner_id == current_user.id)  # [Commented Out] Filter by current user
        )
        .group_by(models.Post.id)  # Group by post ID
        .offset(offset)  # Apply offset for pagination
        .limit(limit)  # Apply limit for pagination
    )

    # Execute the query to get posts with their vote counts
    posts_with_votes_data = session.exec(query).all()

    # List to store posts with their vote counts
    posts_with_votes = []

    # Iterate over each post and its vote count
    for post, vote_count in posts_with_votes_data:
        # Get the post owner from the database
        owner = session.get(models.Users, post.owner_id)

        # If owner exists, create a UserPublic schema from it
        if owner:
            owner_public = schema.UserPublic.model_validate(owner)
        else:
            owner_public = None

        # Create a PostPublic schema from the post data
        post_public = schema.PostPublic(
            id=post.id,
            title=post.title,
            content=post.content,
            published=post.published,
            created_at=post.created_at,
            owner_id=post.owner_id,
            owner=owner_public,
        )

        # Create a PostVote schema combining post and vote data
        post_with_votes = schema.PostVote(PostPublic=post_public, votes=vote_count)

        # Add the post with votes to the result list
        posts_with_votes.append(post_with_votes)

    # Return the list of posts with their vote counts
    return posts_with_votes


@router.get("/{post_id}", response_model=schema.PostVote)
def read_post(
    post_id: int,  # ID of the post to retrieve
    session: SessionDep,  # Database session dependency
    # current_user: models.Users = Depends(get_current_user),  # [Commented Out] Current authenticated user
):
    # Get the post from the database by its ID
    post = session.get(models.Post, post_id)

    # If the post does not exist, raise a 404 error
    if not post:
        raise HTTPException(
            status_code=404, detail=f"Post with post_id of {post_id} not found"
        )

    # [Commented Out] if post.owner_id != current_user.id:
    # [Commented Out]     raise HTTPException(
    # [Commented Out]         status_code=status.HTTP_403_FORBIDDEN,
    # [Commented Out]         detail="Not authorized to perform request action",
    # [Commented Out]     )

    # Return the retrieved post
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,  # ID of the post to delete
    session: SessionDep,  # Database session dependency
    current_user: models.Users = Depends(
        get_current_user
    ),  # Current authenticated user
):
    # Get the post from the database by its ID
    post = session.get(models.Post, post_id)

    # If the post does not exist, raise a 404 error
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with post_id of {post_id} not found",
        )

    # Check if the current user is the owner of the post
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform request action",
        )

    # Delete the post from the database
    session.delete(post)

    # Commit the transaction to persist the deletion
    session.commit()

    # Return a success message
    return {"message": "Post deleted successfully"}


@router.put(
    "/{post_id}", status_code=status.HTTP_200_OK, response_model=schema.PostPublic
)
def update_post(
    post_id: int,  # ID of the post to update
    post: schema.PostUpdate,  # Updated post data
    session: SessionDep,  # Database session dependency
    current_user: models.Users = Depends(
        get_current_user
    ),  # Current authenticated user
):
    # Get the post from the database by its ID
    db_post = session.get(models.Post, post_id)

    # If the post does not exist, raise a 404 error
    if not db_post:
        raise HTTPException(
            status_code=404, detail=f"Post with post_id of {post_id} not found"
        )

    # Check if the current user is the owner of the post
    if db_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform request action",
        )

    # Update the post data, excluding unset fields
    post_data = post.model_dump(exclude_unset=True)

    # Update the database model with the new data
    db_post.sqlmodel_update(post_data)

    # Add the updated post to the session
    session.add(db_post)

    # Commit the transaction to persist the changes
    session.commit()

    # Refresh the model to get the latest data from the database
    session.refresh(db_post)

    # Return the updated post
    return db_post


@router.patch("/{post_id}", response_model=schema.PostPublic)
def update_post(
    post_id: int,  # ID of the post to update
    post: schema.PostUpdate,  # Updated post data
    session: SessionDep,  # Database session dependency
    current_user: models.Users = Depends(
        get_current_user
    ),  # Current authenticated user
):
    # Get the post from the database by its ID
    post_db = session.get(models.Post, post_id)

    # If the post does not exist, raise a 404 error
    if not post_db:
        raise HTTPException(
            status_code=404, detail=f"Post with post_id of {post_id} not found"
        )

    # Check if the current user is the owner of the post
    if post_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform request action",
        )

    # Update the post data, excluding unset fields
    post_data = post.model_dump(exclude_unset=True)

    # Update the database model with the new data
    post_db.sqlmodel_update(post_data)

    # Add the updated post to the session
    session.add(post_db)

    # Commit the transaction to persist the changes
    session.commit()

    # Refresh the model to get the latest data from the database
    session.refresh(post_db)

    # Return the updated post
    return post_db
