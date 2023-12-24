from random import randrange
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    id: Optional[int]
    title: str
    content: str
    rating: Optional[int] = None
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
    return {"message": "this is home page"}


@app.get("/posts")
def get_all_post():
    return {"message": "data get successfully", "payload": allposts}


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
def create_post(post: Post):
    new_post = post.model_dump()
    new_post["id"] = randrange(1, 1000000000000)

    allposts.append(new_post)
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
