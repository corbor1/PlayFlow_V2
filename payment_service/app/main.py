from fastapi import FastAPI
from app.api.auth import router as auth 
from app.api.CT_DT import router_db as router_db
from app.api.status_service import router as status_service

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌐 Server started at http://127.0.0.1:8000/docs")
    yield
    print("Приложение останавливается: освобождаем ресурсы")

app = FastAPI(lifespan=lifespan)

app.include_router(status_service)
app.include_router(auth)
app.include_router(router_db)