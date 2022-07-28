from pydantic import BaseModel

"""Schema model"""
class Post(BaseModel):
    title: str
    content: str
    published: bool = True # Default value True is applied if user doesn't provide one