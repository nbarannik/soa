import grpc
import post_service_pb2
import post_service_pb2_grpc

from typing import List, Optional

POST_SERVICE_GRPC_HOST = "post_service"
POST_SERVICE_GRPC_PORT = 50051

class PostServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(f"{POST_SERVICE_GRPC_HOST}:{POST_SERVICE_GRPC_PORT}")
        self.stub = post_service_pb2_grpc.PostServiceStub(self.channel)

    def __del__(self):
        self.channel.close()

    async def create_post(self, title: str, description: str, creator_id: str, is_private: bool = False, tags: List[str] = None):
        tags = tags or []
        request = post_service_pb2.CreatePostRequest(
            title=title,
            description=description,
            creator_id=creator_id,
            is_private=is_private,
            tags=tags
        )
        return self.stub.CreatePost(request)

    async def get_post(self, post_id: str, user_id: str):
        request = post_service_pb2.GetPostRequest(
            post_id=post_id,
            user_id=user_id
        )
        return self.stub.GetPost(request)

    async def update_post(self, post_id: str, title: str, description: str, user_id: str, is_private: bool = False, tags: List[str] = None):
        tags = tags or []
        request = post_service_pb2.UpdatePostRequest(
            post_id=post_id,
            title=title,
            description=description,
            is_private=is_private,
            tags=tags,
            user_id=user_id
        )
        return self.stub.UpdatePost(request)

    async def delete_post(self, post_id: str, user_id: str):
        request = post_service_pb2.DeletePostRequest(
            post_id=post_id,
            user_id=user_id
        )
        return self.stub.DeletePost(request)

    async def list_posts(self, page: int = 1, page_size: int = 10, user_id: str = ""):
        request = post_service_pb2.ListPostsRequest(
            page=page,
            page_size=page_size,
            user_id=user_id
        )
        return self.stub.ListPosts(request)
    
    @staticmethod
    def _grpc_post_to_dict(grpc_post):
        return {
            "id": grpc_post.id,
            "title": grpc_post.title,
            "description": grpc_post.description,
            "creator_id": grpc_post.creator_id,
            "created_at": grpc_post.created_at,
            "updated_at": grpc_post.updated_at,
            "is_private": grpc_post.is_private,
            "tags": list(grpc_post.tags)
        }

def get_post_service():
    return PostServiceClient()