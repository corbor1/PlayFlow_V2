from fastapi import FastAPI
from app.api.user import router as user 
from app.api.cr_dr import router_db as router_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается: инициализируем ресурсы")
    yield
    print("Приложение останавливается: освобождаем ресурсы")

app = FastAPI(lifespan=lifespan)

app.include_router(user)
app.include_router(router_db)
