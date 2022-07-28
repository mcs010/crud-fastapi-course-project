from datetime import datetime
from pydantic import BaseModel

"""Schema model"""
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True # Default value True is applied if user doesn't provide one

class PostCreate(PostBase):
    pass

class Post(PostBase):
    """By extending PostBase, it heritates its fields, so no need to redeclare them"""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True