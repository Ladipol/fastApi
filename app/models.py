# Import the datetime module to handle date and time operations
from datetime import datetime

# Import type hints for optional values and lists
from typing import Optional, List

# Import EmailStr from pydantic for email validation
from pydantic import EmailStr

# Import SQLModel, Field, and Relationship from sqlmodel for database modeling
from sqlmodel import Field, SQLModel, Relationship


# Define a Users database model with SQLModel
class Users(SQLModel, table=True):
    # Unique identifier for the user, automatically set as primary key
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    # Email address of the user, validated and unique
    email: EmailStr = Field(index=True, unique=True, nullable=False)
    # Password for the user with minimum length requirement
    password: str = Field(nullable=False, min_length=8)
    # Timestamp when the user was created, defaults to current time
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now().astimezone(), nullable=False
    )
    # Relationship to posts made by this user
    posts: List["Post"] = Relationship(back_populates="owner")
    phone_num: str = Field(nullable=True)


# Define a Post database model with SQLModel
class Post(SQLModel, table=True):
    # Unique identifier for the post, automatically set as primary key
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    # Title of the post, required and indexed for search
    title: str = Field(index=True, nullable=False)
    # Content of the post, required with maximum length
    content: str = Field(index=True, nullable=False, max_length=254)
    # Boolean indicating if the post is published, defaults to True
    published: bool = Field(default=True)
    # Timestamp when the post was created, defaults to current time
    created_at: datetime = Field(
        default_factory=lambda: datetime.now().astimezone(), nullable=False
    )
    # Foreign key referencing the Users table, nullable by default
    owner_id: Optional[int] = Field(
        default=None, foreign_key="users.id", ondelete="CASCADE", nullable=True
    )
    # Relationship to the owner of this post
    owner: Optional[Users] = Relationship(back_populates="posts")


# Define a Vote database model with SQLModel
class Vote(SQLModel, table=True):
    # Foreign key referencing the Users table, part of primary key
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", primary_key=True, nullable=False
    )
    # Foreign key referencing the Post table, part of primary key
    post_id: Optional[int] = Field(
        default=None, foreign_key="post.id", primary_key=True, nullable=False
    )
