from fastapi import Request, Depends, HTTPException, status
from jose import JWTError, jwt
from .config import settings
from .. import crud
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str):
    to_encode = {}
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    to_encode.update({"usr": user_id})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

async def validate_user_token(users_access_token: str = Depends(get_token)):
    if users_access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt.decode(users_access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("usr")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
async def get_current_user(user_id: str = Depends(validate_user_token)):
    user = await crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user