import structlog
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response

from app.api.auth import router as auth 
from app.api.CT_DT import router_db as router_db
from app.api.status_service import router as status_service
from contextlib import asynccontextmanager


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерируем уникальный ID, если его нет в заголовках (например, от API Gateway)
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Привязываем request_id к контексту structlog для этого запроса
        # Мы используем get_logger().bind(), но результат нужно где-то хранить.
        # Самый простой способ в FastAPI - положить в request.state
        request.state.logger = structlog.get_logger().bind(request_id=request_id)
        
        response = await call_next(request)
        return response
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌐 Server started at http://127.0.0.1:8000/docs")
    yield
    print("Приложение останавливается: освобождаем ресурсы")

app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)
app.include_router(status_service)
app.include_router(auth)
app.include_router(router_db)