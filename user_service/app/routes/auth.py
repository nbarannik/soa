from fastapi import APIRouter, HTTPException, Response, Depends
from .. import schemas, crud
from .dependencies import create_access_token, validate_user_token

router = APIRouter()

@router.post("/register")
async def register(user: schemas.UserCreate):
    db_user = await crud.create_user(user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    return {"message": "User registered successfully"}

@router.post("/login", response_model=schemas.SessionToken)
async def login(response: Response, user_login: schemas.LoginRequest):
    user = await crud.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    session_token = create_access_token(str(user.id))
    response.set_cookie(key="users_access_token", value=session_token, httponly=True)
    return {"session_token": session_token}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'User logout successfully'}

@router.get("/auth")
async def auth(user_id: str = Depends(validate_user_token)):
    return user_id