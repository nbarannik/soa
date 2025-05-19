import pytest
from datetime import datetime
from models.database import Base, engine, get_db
from models.post import Post
from services.post_service import PostService
import post_service_pb2

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def post_service(db):
    return PostService(db)

def test_create_post(post_service):
    request = post_service_pb2.CreatePostRequest(
        title="Test Post",
        description="Test Description",
        creator_id="user1",
        is_private=False,
        tags=["test", "python"]
    )
    
    response = post_service.create_post(request)
    assert response.title == "Test Post"
    assert response.description == "Test Description"
    assert response.creator_id == "user1"
    assert response.is_private is False
    assert set(response.tags) == {"test", "python"}

def test_get_post(post_service):
    # Create
    create_request = post_service_pb2.CreatePostRequest(
        title="Test Post",
        description="Test Description",
        creator_id="user1",
        tags=["test"]
    )
    created_post = post_service.create_post(create_request)
    
    # Test get
    get_request = post_service_pb2.GetPostRequest(
        post_id=created_post.id,
        user_id="user1"
    )
    fetched_post = post_service.get_post(get_request)
    assert fetched_post.id == created_post.id
    assert fetched_post.title == "Test Post"
    
    # Test private post
    private_post = post_service.create_post(
        post_service_pb2.CreatePostRequest(
            title="Private Post",
            description="Private",
            creator_id="user1",
            is_private=True
        )
    )
    
    # Creator can access
    get_request = post_service_pb2.GetPostRequest(
        post_id=private_post.id,
        user_id="user1"
    )
    assert post_service.get_post(get_request).id == private_post.id
    
    # Other user can't access
    get_request = post_service_pb2.GetPostRequest(
        post_id=private_post.id,
        user_id="user2"
    )
    with pytest.raises(PermissionError):
        post_service.get_post(get_request)

def test_update_post(post_service):
    # Create a post first
    create_request = post_service_pb2.CreatePostRequest(
        title="Test Post",
        description="Test Description",
        creator_id="user1"
    )
    created_post = post_service.create_post(create_request)
    
    # Update the post
    update_request = post_service_pb2.UpdatePostRequest(
        post_id=created_post.id,
        title="Updated Title",
        description="Updated Description",
        is_private=True,
        tags=["updated"],
        user_id="user1"
    )
    updated_post = post_service.update_post(update_request)
    assert updated_post.title == "Updated Title"
    assert updated_post.description == "Updated Description"
    assert updated_post.is_private is True
    assert updated_post.tags == ["updated"]
    
    # Test update by non-owner
    update_request.user_id = "user2"
    with pytest.raises(PermissionError):
        post_service.update_post(update_request)

def test_delete_post(post_service):
    # Create a post
    create_request = post_service_pb2.CreatePostRequest(
        title="To Delete",
        description="Will be deleted",
        creator_id="user1"
    )
    created_post = post_service.create_post(create_request)
    
    # Delete the post
    delete_request = post_service_pb2.DeletePostRequest(
        post_id=created_post.id,
        user_id="user1"
    )
    assert post_service.delete_post(delete_request) is True
    
    # Verify deleted
    get_request = post_service_pb2.GetPostRequest(
        post_id=created_post.id,
        user_id="user1"
    )
    with pytest.raises(ValueError):
        post_service.get_post(get_request)
    
    # Test delete by non-owner
    new_post = post_service.create_post(
        post_service_pb2.CreatePostRequest(
            title="Another Post",
            description="Test",
            creator_id="user1"
        )
    )
    delete_request = post_service_pb2.DeletePostRequest(
        post_id=new_post.id,
        user_id="user2"
    )
    with pytest.raises(PermissionError):
        post_service.delete_post(delete_request)

def test_list_posts(post_service):
    # Create posts
    for i in range(1, 6):
        post_service.create_post(
            post_service_pb2.CreatePostRequest(
                title=f"Post {i}",
                description=f"Description {i}",
                creator_id="user1",
                is_private=(i % 2 == 0)  # Every even post is private
            )
        )
    
    # Create some posts by another user
    for i in range(1, 4):
        post_service.create_post(
            post_service_pb2.CreatePostRequest(
                title=f"Other Post {i}",
                description=f"Other Description {i}",
                creator_id="user2",
                is_private=(i % 2 == 1)  # Every odd post is private
            )
        )
    
    # Test listing for user1
    list_request = post_service_pb2.ListPostsRequest(
        page=1,
        page_size=10,
        user_id="user1"
    )
    response = post_service.list_posts(list_request)
    
    # user1 should see:
    # - All their own posts (5)
    # - Public posts from user2 (1 and 3 are private, 2 is public)
    assert response.total == 6  # 5 (user1) + 1 (user2 public)
    
    # Test pagination
    list_request.page_size = 3
    response = post_service.list_posts(list_request)
    assert len(response.posts) == 3
    assert response.page == 1
    assert response.page_size == 3
    assert response.total == 6