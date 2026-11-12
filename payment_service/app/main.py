from fastapi import FastAPI
from app.api.auth import router as auth 
from app.api.CT_DT import router_db as router_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается: инициализируем ресурсы")
    yield
    print("Приложение останавливается: освобождаем ресурсы")

app = FastAPI(lifespan=lifespan)

app.include_router(auth)
app.include_router(router_db)