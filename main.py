import time
from random import randrange
from typing import Optional

import psycopg
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI()


# try:
#     conn = psycopg.connect(
#         dbname="postgres", user="postgres", password="azim", host="172.17.0.3"
#     )
#     print("db connected")
# except Exception as error:
#     print("connection failed to db")
#     print("Error", error)

# Connection string with credentials and database name

conn_string = "postgresql://postgres:azim@172.17.0.3:5432/postgres"
while True:
    try:
        # Connect to the database
        conn = psycopg.connect(conn_string)
        print("Connected to PostgreSQL database")
        break
    except Exception as error:
        print("Connection failed to db")
        print("Error", error)
        time.sleep(2)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


class Updatepost(BaseModel):
    content: str
    published: bool = True


@app.get("/")
def root():
    return RedirectResponse(url="/docs", status_code=303)


@app.get("/posts")
async def get_all_posts():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM blogs")
        # Fetch all results as a list of tuples
        posts = cur.fetchall()
        field_names = [desc[0] for desc in cur.description]

    formatted_posts = [dict(zip(field_names, post)) for post in posts]
    # Return a JSON response with the retrieved posts
    return {"message": "Data retrieved successfully", "payload": formatted_posts}


@app.get("/posts/latest/")
async def get_latest_post():
    with conn.cursor() as cur:
        # Retrieve the latest post from the database
        cur.execute("SELECT * FROM blogs ORDER BY id DESC LIMIT 1")
        latest_post = cur.fetchone()

        if latest_post:
            # If the latest post exists, return it
            field_names = [desc[0] for desc in cur.description]
            formatted_post = dict(zip(field_names, latest_post))
            return {"message": "Data retrieved successfully", "payload": formatted_post}
        else:
            # If no posts are found, raise a 404 Not Found exception
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts found in the database",
            )


@app.get("/posts/{postid}/")
def get_all_post(postid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM blogs WHERE id = %s", (str(postid),))
        post = cur.fetchone()
        field_names = [desc[0] for desc in cur.description]

    if post:
        formatted_post = dict(zip(field_names, post))
        return {"message": "Data retrieved successfully", "payload": formatted_post}
    else:
        raise HTTPException(status_code=404, detail="Post not found")


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO blogs (title,content,published) VALUES(%s,%s,%s) RETURNING *",
            (post.title, post.content, post.published),
        )
        new_post = cur.fetchone()
        column_names = [desc[0] for desc in cur.description]

        # Create a dictionary with column names as keys
        post_dict = dict(zip(column_names, new_post))
        conn.commit()

    return {"message": "post create successfully", "payload": post_dict}


@app.delete("/posts/{postid}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(postid: int):
    with conn.cursor() as cur:
        # Check if the post exists before deleting
        cur.execute("SELECT * FROM blogs WHERE id = %s", (str(postid),))
        existing_post = cur.fetchone()

        if existing_post:
            # If the post exists, delete it
            cur.execute("DELETE FROM blogs WHERE id = %s", (str(postid),))
            conn.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            # If the post doesn't exist, raise a 404 Not Found exception
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post not found for this {postid} id",
            )


@app.put("/posts/{postid}/", status_code=status.HTTP_201_CREATED)
def updatePost(postid: int, update_post: Updatepost):
    with conn.cursor() as cur:
        # Check if the post exists before deleting
        cur.execute("SELECT * FROM blogs WHERE id = %s", (str(postid),))
        existing_post = cur.fetchone()

        if existing_post:
            cur.execute(
                "UPDATE blogs SET content=%s, published=%s  WHERE id = %s RETURNING *",
                (
                    update_post.content,
                    update_post.published,
                    str(postid),
                ),
            )
            new_post = cur.fetchone()
            column_names = [desc[0] for desc in cur.description]
            # Create a dictionary with column names as keys
            post_dict = dict(zip(column_names, new_post))
            conn.commit()
            return {"message": "post create successfully", "payload": post_dict}
        else:
            # If the post doesn't exist, raise a 404 Not Found exception
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post not found for this {postid} id",
            )
