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
    rating: Optional[int] = None
    published: bool = True


allposts = [
    {
        "id": 1,
        "title": "Lorem Ipsum Dolor Sit Amet",
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac justo eget sapien faucibus commodo.",
        "rating": 4.5,
        "published": True,
    },
    {
        "id": 2,
        "title": "Nulla Facilisi",
        "content": "Nulla facilisi. Curabitur ac arcu nec urna tristique tincidunt. Suspendisse potenti.",
        "rating": 3.8,
        "published": True,
    },
    {
        "id": 3,
        "title": "Vestibulum Ante Ipsum Primis",
        "content": "Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Proin euismod nisi nec justo vestibulum.",
        "rating": 4.2,
        "published": True,
    },
    {
        "id": 4,
        "title": "Aenean Consectetur Elit",
        "content": "Aenean consectetur elit et ligula vulputate, a aliquam lacus varius. Vivamus vel turpis vitae leo imperdiet luctus.",
        "rating": 4.8,
        "published": True,
    },
    {
        "id": 5,
        "title": "Fusce Euismod Mollis Elit",
        "content": "Fusce euismod mollis elit, nec consectetur metus vestibulum sit amet. Integer sed lectus in justo hendrerit aliquet.",
        "rating": 3.5,
        "published": True,
    },
]


def findpost(id, posts):
    for post in posts:
        if post["id"] == id:
            return post


def findpostindex(id, posts):
    for index, post in enumerate(posts):
        if post["id"] == id:
            return index


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
def get_all_post():
    post = allposts[len(allposts) - 1]
    return {"message": "data get successfully", "payload": post}


# @app.get("/posts/{postid}/")
# def get_all_post(postid: int, response: Response):
#     post = findpost(postid, allposts)
#     if not post:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return {"message": f"post not found for this {postid} id"}
#     return {"message": "data get successfully", "payload": post}


@app.get("/posts/{postid}/")
def get_all_post(postid: int):
    post = findpost(postid, allposts)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post not found for this {postid} id",
        )
    return {"message": "data get successfully", "payload": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO blogs (title,content,published) VALUES(%s,%s,%s) RETURNING *",
            (post.title, post.content, post.published),
        )
        new_post = cur.fetchone()
        conn.commit()

    return {"message": "post create successfully", "payload": new_post}


@app.delete("/posts/{postid}/", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(postid: int):
    postindex = findpostindex(postid, allposts)
    if not postindex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post not found for this {postid} id",
        )
    allposts.pop(postindex)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{postid}/", status_code=status.HTTP_201_CREATED)
def updatePost(postid: int, update_post: Updatepost):
    postindex = findpostindex(postid, allposts)
    if not postindex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post not found for this {postid} id",
        )
    post_dict = update_post.model_dump()
    post_dict["id"] = postid
    allposts[postindex] = post_dict

    return {"message": "post create successfully", "payload": post_dict}
