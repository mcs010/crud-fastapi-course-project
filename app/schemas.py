from pydantic import BaseModel

"""Schema model"""
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True # Default value True is applied if user doesn't provide one

class PostCreate(PostBase):
    pass