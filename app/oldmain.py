from fastapi import FastAPI, status, HTTPException, Depends, Query
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from .database import Post, engine, get_session


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favorite foods", "content": "I like pizza", "id": 2},
]

try:
    conn = psycopg2.connect(
        "dbname=fastapi user=postgres password=D@t@b@se host=localhost",
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()
    print("Database connection was successful!")
except Exception as error:
    print("Connecting to database failed!")
    print("Error: ", error)


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}


@app.get("/posts")
async def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# async def create_posts(post: Post):
#     post_dict = post.model_dump()
#     post_dict["id"] = randrange(0, 1000000)
#     my_posts.append(post_dict)
#     return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) RETURNING * """,
        (
            post.title,
            post.content,
            post.published,
        ),
    )
    new_post = cursor.fetchone()

    conn.commit()

    return {"data": new_post}


# @app.get("/posts/latest")
# async def get_latest_post():
#     post = my_posts[len(my_posts) - 1]
#     return {"detail": post}


# @app.get("/posts/{id}")
# async def get_post(id: int):
#     post = find_post(id)
#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"post with id: {id} was not found",
#         )
#     return {"data": post}


@app.get("/posts/{id}")
async def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return {"data": post}


# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(id: int):
#     index = find_index_post(id)
#     if index is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"post with id: {id} was not found",
#         )
#     my_posts.pop(index)
#     return {"message": "post was successfully deleted"}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    if delete_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return {"message": "post was successfully deleted"}


# @app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
# async def update_post(id: int, post: Post):
#     index = find_index_post(id)
#     if index is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"post with id: {id} was not found",
#         )
#     post_dict = post.model_dump()
#     post_dict["id"] = id
#     my_posts[index] = post_dict
#     return {"data": post_dict}


@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, (str(id))),
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    return {"data": updated_post}
