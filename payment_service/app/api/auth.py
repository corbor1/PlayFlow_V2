from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserCreate, UserCreateResponse, Token
from app.core.db import get_db
from app.models.models import User
from app.integrations.OAuth2 import oauth2_scheme, create_access_token, verify_password
from ..secret_key import SECRET_KEY, ALGORITHM
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user",
            )
        return User(
            id=payload.get("user_id"),
            username=username,
            is_active=True,
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя (async, без хеширования)"
)
async def register_user(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    ):

    log = request.state.logger.bind(
        action="registration",
        username=user_data.username,
        email=user_data.email
    )
    log.info("registration_started")

    salt = bcrypt.gensalt()
    password_bytes = user_data.password.encode("utf-8")   # plain-text пароль
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash_str = hashed.decode("utf-8")           # строка для БД

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash_str,
        # created_at/updated_at лучше через server_default в модели
    )
    result = await db.execute(select(User).where(
        (User.username == user_data.username) | (User.email == user_data.email)
    ))
    existing = result.scalars().first()
    if existing:
        field = "username" if existing.username == user_data.username else "email"
        log = request.state.logger.bind(
                action="already taken",
                username=user_data.username,
                email=user_data.email
            )
        log.error("User alredy taken")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field} already taken")

    new_user = User(
        username = user_data.username,
        email = user_data.email,
        password_hash = hashed.decode("ascii")
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        log.info(
            "registration_completed",
            status="success",
            user_id=new_user.id
        )
        return new_user

    except IntegrityError:
        await db.rollback()
        log.warning(
            "registration_failed",
            reason="duplicate_entry",
            conflict_check="username_or_email" 
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken"
        )

    except Exception as e:
        log.error("registration_unexpected_error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    

    

# Эндпоинт для аутентификации (получения токена)
@router.post("/auth/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),   # 1) читает форму (username, password)
    db: AsyncSession = Depends(get_db),                 # 2) даёт сессию БД
):
    # 3) Ищем пользователя по username в БД
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    # 4) Проверяем: пользователь существует? пароль верный?
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 5) Проверяем активность
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 6) Выдаём токен
    access_token = create_access_token({"sub": user.username, "user_id": user.id})
    return Token(access_token=access_token, token_type="bearer")

# Защищённый эндпоинт
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user.username}
