from typing import Optional
from click import password_option
from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

while True:
    """Starts server if connection is ok, otherwise it gives us an error"""
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="admin", 
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

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
def get_posts(db: Session = Depends(get_db)):
    """Retrieve all stored posts"""
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).all()

    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #               (post.title, post.content, post.published))
    
    # new_post = cursor.fetchone()

    # conn.commit() # Push changes to database

    new_post = models.Post(**post.dict()) # "**" dumps the unpacked content from the dictionary "post"

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)): # Fast API validates it if it can be converted to the respective type, if so, 
                                           # then it automatically converts to that type
    """Retrieve one specific post"""
    
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"post with id {id} was not found")

    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    """
    Delete a post
    """
    
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))

    # deleted_post = cursor.fetchone()

    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with {id} does not exist")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) # When deleting, the good practice is to return nothing

@app.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Update a post"""
    
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s
    #                WHERE id = %s RETURNING * """, 
    #               (post.title, post.content, post.published, str(id)))

    # updated_post = cursor.fetchone()

    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with {id} does not exist")

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()
    
    return post_query.first()