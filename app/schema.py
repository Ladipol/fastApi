# Import the datetime module to handle date and time operations
from datetime import datetime

# Import the Optional type from the typing module for nullable fields
from typing import Optional

# Import EmailStr from pydantic to validate email addresses
from pydantic import EmailStr

# Import SQLModel and Field from sqlmodel for database modeling
from sqlmodel import SQLModel, Field

# Import datetime again (note: this is a duplicate import)
from datetime import datetime


# Define a UserPublic class that inherits from SQLModel
class UserPublic(SQLModel):
    # Unique identifier for the user (integer type)
    id: int
    # Email address of the user (validated by EmailStr)
    email: EmailStr
    # Timestamp when the user was created
    created_at: datetime


# Define a PostCreate class for creating new posts
class PostCreate(SQLModel):
    # Title of the post (string type)
    title: str
    # Content of the post (string type)
    content: str
    # Boolean indicating if the post is published
    published: bool


# Define a PostUpdate class that inherits from PostCreate
class PostUpdate(PostCreate):
    # This class inherits all fields from PostCreate for updating posts
    pass


# Define a PostPublic class that inherits from PostCreate
class PostPublic(PostCreate):
    # Unique identifier for the post (integer type)
    id: int
    # Timestamp when the post was created
    created_at: datetime
    # Foreign key referencing the owner's ID (nullable)
    owner_id: Optional[int] = None
    # Relationship to the owner's UserPublic model (nullable)
    owner: Optional["UserPublic"] = None


# Define a PostVote class that inherits from SQLModel
class PostVote(SQLModel):
    # Reference to the PostPublic model
    PostPublic: PostPublic
    # Number of votes (integer type)
    votes: int


# Define a UserCreate class for creating new users
class UserCreate(SQLModel):
    # Email address of the user (validated by EmailStr)
    email: EmailStr
    # Password for the user (string type)
    password: str


# Define a UserLogin class for user login operations
class UserLogin(SQLModel):
    # Email address of the user (validated by EmailStr)
    email: EmailStr
    # Password for the user (string type)
    password: str


# Define a Token class for authentication tokens
class Token(SQLModel):
    # The access token string
    access_token: str
    # Type of token (e.g., "bearer")
    token_type: str


# Define a TokenData class for token validation
class TokenData(SQLModel):
    # User ID associated with the token
    id: int


# Define a VoteCreate class for creating new votes
class VoteCreate(SQLModel):
    # Foreign key referencing the post's ID
    post_id: int
    # Direction of the vote (1 for upvote, -1 for downvote)
    dir: int = Field(..., ge=-1, le=1)  # Uses Field to enforce constraints


# Define a VotePublic class for public vote data
class VotePublic(SQLModel):
    # Foreign key referencing the post's ID
    post_id: int
    # Direction of the vote (1 for upvote, -1 for downvote)
    dir: int
    # Foreign key referencing the user's ID
    user_id: int
    # Timestamp when the vote was created
    created_at: datetime
