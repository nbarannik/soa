from fastapi import APIRouter, Depends, HTTPException
from .. import schemas, crud
from .dependencies import get_current_user, validate_user_token

router = APIRouter()

@router.get("/me", response_model=schemas.UserResponse)
async def read_user_me(current_user: schemas.UserResponse = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=schemas.UserResponse)
async def update_user_me(
    user_update: schemas.UserUpdate,
    user_id: StopAsyncIteration = Depends(validate_user_token)
):
    updated_user = await crud.update_user(user_id, user_update)
    return updated_user