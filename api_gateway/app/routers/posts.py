from fastapi import APIRouter, Depends, HTTPException
import grpc
from app.schemas import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.dependencies import auth_user
from app.services.post_service import PostServiceClient, get_post_service

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    user_id: str = Depends(auth_user),
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

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    user_id: str = Depends(auth_user),
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

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_data: PostUpdate,
    user_id: str = Depends(auth_user),
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

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    user_id: str = Depends(auth_user),
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

@router.get("/", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 10,
    user_id: str = Depends(auth_user),
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