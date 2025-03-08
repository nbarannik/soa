from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import httpx

app = FastAPI()

USER_SERVICE_URL = "http://user_service:8000"

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