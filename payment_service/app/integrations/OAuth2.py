from datetime import datetime, timedelta, timezone
from app.secret_key import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема OAuth2 для Bearer-токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Функция для создания JWT-токена
def create_access_token(data: dict) -> str:
    to_encode = {**data, "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)