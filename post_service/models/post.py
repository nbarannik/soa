from sqlalchemy import Column, String, Boolean, DateTime, ARRAY
from sqlalchemy.sql import func
from uuid import uuid4
from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_private = Column(Boolean, default=False)
    tags = Column(ARRAY(String), default=[])

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "creator_id": self.creator_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_private": self.is_private,
            "tags": self.tags
        }