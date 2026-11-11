from fastapi import FastAPI
from app.api.user import router as user  # Явно указываем, что импортируем router
from app.api.cr_dr import router_db as router_db

app = FastAPI()

app.include_router(user)
app.include_router(router_db)
