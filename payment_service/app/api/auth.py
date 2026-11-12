from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserCreate, UserCreateResponse, Token
from app.core.db import get_db
from app.models.models import User
from app.integrations.OAuth2 import oauth2_scheme, create_access_token
from ..secret_key import SECRET_KEY, ALGORITHM
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or not User.is_active(username):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        return User(id=payload.get("user_id"), username=username, is_active=True)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

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
    password = user_data.password_hash
    salt = bcrypt.gensalt()
    password = password.encode("utf-8")
    hashed = bcrypt.hashpw(password, salt)
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
        password_hash = hashed.decode("ascii")
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# Эндпоинт для аутентификации (получения токена)
@router.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Здесь должна быть логика проверки пользователя в базе данных
    # Для примера создадим пользователя вручную
    user = User(id=1, username=form_data.username, password_hash="hashed_password_here")  # В проде берём хэш из БД
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    access_token = create_access_token({
        "sub": user.username,
        "user_id": user.id
    })
    return Token(access_token=access_token, token_type="bearer")

# Защищённый эндпоинт
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user.username}
