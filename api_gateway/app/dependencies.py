from fastapi import Header, HTTPException, Request, Response, status
import httpx

USER_SERVICE_URL = "http://user_service:8000"

async def get_user_id(x_user_id: str = Header(...)):
    return x_user_id

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

async def auth_user(request: Request) -> str:
    async with httpx.AsyncClient() as client:
        try:
            cookies = dict(request.cookies)
            
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/auth",
                cookies=cookies,
                timeout=5.0
            )
            
            if response.status_code == status.HTTP_200_OK:
                try:
                    return response.text
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Invalid response format from user service"
                    )
            
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
                
            raise HTTPException(
                status_code=response.status_code,
                detail=f"User service error: {response.text}"
            )
                
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User service is unavailable"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="User service timeout"
            )