from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from . import models, schemas
from passlib.context import CryptContext
from .database import async_session_maker
from .routes.config import settings
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_username(username: str) -> models.User | None:
    async with async_session_maker() as session:
        stmt = select(models.User).where(models.User.username == username)
        result = await session.execute(stmt)
        return result.scalars().first()

async def get_user_by_id(user_id: str) -> models.User | None:
    async with async_session_maker() as session:
        stmt = select(models.User).where(models.User.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

async def create_user(user: schemas.UserCreate) -> models.User | None:
    async with async_session_maker() as session:
        if await get_user_by_username(user.username):
            return None

        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            username=user.username,
            password_hash=hashed_password,
            email=user.email,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

async def authenticate_user(username: str, password: str) -> models.User | None:
    user = await get_user_by_username(username)
    if not user or not pwd_context.verify(password, user.password_hash):
        return None
    return user

async def update_user(user_id: str, user_update: schemas.UserUpdate) -> models.User | None:
    async with async_session_maker() as session:
        stmt = select(models.User).where(models.User.id == user_id)
        result = await session.execute(stmt)
        db_user = result.scalars().first()

        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)

        await session.commit()
        await session.refresh(db_user)
        return db_user