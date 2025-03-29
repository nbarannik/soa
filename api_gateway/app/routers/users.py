from fastapi import APIRouter, Request
from app.dependencies import proxy_request

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/auth/register")
async def register_user(request: Request):
    return await proxy_request(request, "auth/register")

@router.post("/auth/login")
async def login_user(request: Request):
    return await proxy_request(request, "auth/login")

@router.post("/auth/logout")
async def login_user(request: Request):
    return await proxy_request(request, "auth/logout")

@router.get("/me")
async def get_current_user(request: Request):
    return await proxy_request(request, "users/me")

@router.patch("/me")
async def update_current_user(request: Request):
    return await proxy_request(request, "users/me")