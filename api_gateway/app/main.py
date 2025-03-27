from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import Response, JSONResponse
import httpx
import grpc
import post_service_pb2
import post_service_pb2_grpc
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

USER_SERVICE_URL = "http://user_service:8000"
POST_SERVICE_GRPC_HOST = "post_service"
POST_SERVICE_GRPC_PORT = 50051

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

async def get_user_id(x_user_id: str = Header(...)):
    return x_user_id

# Userservice proxy
async def proxy_request(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        target_url = f"{USER_SERVICE_URL}/{path}"
        try:
            response = await client.request(
                request.method,
                target_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="user_service is unavailable")

# User service endpoints
@app.post("/auth/register")
async def register_user(request: Request):
    return await proxy_request(request, "auth/register")

@app.post("/auth/login")
async def login_user(request: Request):
    return await proxy_request(request, "auth/login")

@app.post("/auth/logout")
async def login_user(request: Request):
    return await proxy_request(request, "auth/logout")

@app.get("/users/me")
async def get_current_user(request: Request):
    return await proxy_request(request, "users/me")

@app.patch("/users/me")
async def update_current_user(request: Request):
    return await proxy_request(request, "users/me")

# Post service endpoints
@app.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    user_id: str = Depends(get_user_id),
    post_service: PostServiceClient = Depends(get_post_service)
):
    try:
        response = await post_service.create_post(
            title=post_data.title,
            description=post_data.description,
            creator_id=user_id,
            is_private=post_data.is_private,
            tags=post_data.tags
        )
        post_dict = PostServiceClient._grpc_post_to_dict(response.post)
        return PostResponse(**post_dict)
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=e.details())

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    user_id: str = Depends(get_user_id),
    post_service: PostServiceClient = Depends(get_post_service)
):
    try:
        response = await post_service.get_post(post_id=post_id, user_id=user_id)
        post_dict = PostServiceClient._grpc_post_to_dict(response.post)
        return PostResponse(**post_dict)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Post not found")
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(status_code=403, detail="Permission denied")
        raise HTTPException(status_code=400, detail=e.details())

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_data: PostUpdate,
    user_id: str = Depends(get_user_id),
    post_service: PostServiceClient = Depends(get_post_service)
):
    try:
        current_post = await post_service.get_post(post_id=post_id, user_id=user_id)
        current_data = current_post.post
        
        response = await post_service.update_post(
            post_id=post_id,
            title=post_data.title if post_data.title is not None else current_data.title,
            description=post_data.description if post_data.description is not None else current_data.description,
            is_private=post_data.is_private if post_data.is_private is not None else current_data.is_private,
            tags=post_data.tags if post_data.tags is not None else current_data.tags,
            user_id=user_id
        )
        post_dict = PostServiceClient._grpc_post_to_dict(response.post)
        return PostResponse(**post_dict)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Post not found")
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(status_code=403, detail="Permission denied")
        raise HTTPException(status_code=400, detail=e.details())

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    user_id: str = Depends(get_user_id),
    post_service: PostServiceClient = Depends(get_post_service)
):
    try:
        response = await post_service.delete_post(post_id=post_id, user_id=user_id)
        return {"success": response.success}
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Post not found")
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(status_code=403, detail="Permission denied")
        raise HTTPException(status_code=400, detail=e.details())

@app.get("/posts", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 10,
    user_id: str = Depends(get_user_id),
    post_service: PostServiceClient = Depends(get_post_service)
):
    try:
        response = await post_service.list_posts(page=page, page_size=page_size, user_id=user_id)
        return PostListResponse(
            posts=[PostResponse(**PostServiceClient._grpc_post_to_dict(post)) for post in response.posts],
            total=response.total,
            page=response.page,
            page_size=response.page_size
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=e.details())