from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserCreate, UserCreateResponse
from app.core.db import get_db
from app.models.models import User

router = APIRouter()

@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя (async, без хеширования)"
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
    ):
    result = await db.execute(select(User).where(
        (User.username == user_data.username) | (User.email == user_data.email)
    ))
    existing = result.scalars().first()
    if existing:
        field = "username" if existing.username == user_data.username else "email"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field} already taken")

    new_user = User(
        username = user_data.username,
        email = user_data.email,
        password_hash = user_data.password_hash
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user