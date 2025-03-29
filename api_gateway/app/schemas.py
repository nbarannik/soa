from pydantic import BaseModel
from typing import List, Optional

class PostCreate(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: List[str] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None

class PostResponse(BaseModel):
    id: str
    title: str
    description: str
    creator_id: str
    created_at: str
    updated_at: str
    is_private: bool
    tags: List[str]

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int