import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.post import Post
import os

SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://post_user:post_password@post_service_db:5432/post_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_post_model(db):
    # Test create
    post = Post(
        title="Test Post",
        description="Test Description",
        creator_id="user1",
        is_private=False,
        tags=["test", "python"]
    )
    db.add(post)
    db.commit()
    
    retrieved = db.query(Post).filter(Post.title == "Test Post").first()
    
    assert retrieved is not None
    assert retrieved.title == "Test Post"
    assert retrieved.description == "Test Description"
    assert retrieved.creator_id == "user1"
    assert retrieved.is_private is False
    assert set(retrieved.tags) == {"test", "python"}
    assert isinstance(retrieved.created_at, datetime)
    assert retrieved.updated_at is None
    
    # Test update
    retrieved.title = "Updated Title"
    db.commit()
    updated = db.query(Post).filter(Post.id == retrieved.id).first()
    assert updated.title == "Updated Title"
    assert isinstance(updated.updated_at, datetime)
    
    # Test to_dict
    post_dict = retrieved.to_dict()
    assert isinstance(post_dict, dict)
    assert post_dict["title"] == "Updated Title"
    assert isinstance(post_dict["created_at"], str)