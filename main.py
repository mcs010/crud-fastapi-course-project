from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

app = FastAPI()

"""Schema model"""
class Post(BaseModel):
    title: str
    content: str
    published: bool = True # Default value True is applied if user doesn't provide one
    rating: Optional[int] = None # Default value None is applied if user doesn't provide one

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favourite foods", 
            "content": "I like pizza", "id": 2}]

def find_post(id):
    """Function to find one specific post"""
    for post in my_posts:
        if post["id"] == id:
            return post

def find_index_post(id):
    """Function that finds a specific index from my_posts, to support other HTTP request functions"""
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            return index

@app.get("/")
def root():
    """Shows the message at api index/home page"""
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    """Retrieve all stored posts"""
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    """Create a new post"""
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/{id}")
def get_post(id: int, response: Response): # Fast API validates it if it can be converted to the respective type, if so, 
                                           # then it automatically converts to that type
    """Retrieve one specific post"""
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"post with id {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND # If the post doesn't exist, returns 404 code, instead of 200
        # return {"message": f"post with id {id} was not found"}
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    """
    Delete a post
    Find the index in the array that has required ID
    my_posts.pop(index)
    """
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with {id} does not exist")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT) # When deleting, the good practice is return nothing

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    """Update a post"""
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with {id} does not exist")
    
    post_dict = post.dict()     # Gets the updated data from frontend and casts it to python dict
    post_dict["id"] = id        # Adds the id key to the updated post
    my_posts[index] = post_dict # Replaces the stored post (at 'index' value) to the updated post 
    return {"data": post_dict}