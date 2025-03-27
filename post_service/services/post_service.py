from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from models.post import Post
import post_service_pb2

class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, request: post_service_pb2.CreatePostRequest) -> post_service_pb2.Post:
        post = Post(
            title=request.title,
            description=request.description,
            creator_id=request.creator_id,
            is_private=request.is_private,
            tags=list(request.tags)
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return self._post_to_proto(post)

    def get_post(self, request: post_service_pb2.GetPostRequest) -> post_service_pb2.Post:
        post = self.db.query(Post).filter(Post.id == request.post_id).first()
        if not post:
            raise ValueError("Post not found")
        
        if post.is_private and post.creator_id != request.user_id:
            raise PermissionError("You don't have permission to view this post")
        
        return self._post_to_proto(post)

    def update_post(self, request: post_service_pb2.UpdatePostRequest) -> post_service_pb2.Post:
        post = self.db.query(Post).filter(Post.id == request.post_id).first()
        if not post:
            raise ValueError("Post not found")
        
        if post.creator_id != request.user_id:
            raise PermissionError("You can't update this post")
        
        post.title = request.title
        post.description = request.description
        post.is_private = request.is_private
        post.tags = list(request.tags)
        
        self.db.commit()
        self.db.refresh(post)
        return self._post_to_proto(post)

    def delete_post(self, request: post_service_pb2.DeletePostRequest) -> bool:
        post = self.db.query(Post).filter(Post.id == request.post_id).first()
        if not post:
            raise ValueError("Post not found")
        
        if post.creator_id != request.user_id:
            raise PermissionError("You can't delete this post")
        
        self.db.delete(post)
        self.db.commit()
        return True

    def list_posts(self, request: post_service_pb2.ListPostsRequest) -> post_service_pb2.ListPostsResponse:
        query = self.db.query(Post)
        
        # Filter private posts if user is not the creator
        query = query.filter(
            (Post.is_private == False) | 
            (Post.is_private == True) & (Post.creator_id == request.user_id)
        )
        
        total = query.count()
        posts = query.offset((request.page - 1) * request.page_size).limit(request.page_size).all()
        
        return post_service_pb2.ListPostsResponse(
            posts=[self._post_to_proto(post) for post in posts],
            total=total,
            page=request.page,
            page_size=request.page_size
        )

    def _post_to_proto(self, post: Post) -> post_service_pb2.Post:
        return post_service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat() if post.updated_at else "",
            is_private=post.is_private,
            tags=post.tags
        )