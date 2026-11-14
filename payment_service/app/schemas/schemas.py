from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Модель для ответа токена
class Token(BaseModel):
    access_token: str
    token_type: str