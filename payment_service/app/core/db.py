
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:mysecretpassword@localhost:54322/payflow_db"

# Создаём асинхронный движок (один на всё приложение)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,                 # логирование SQL (в проде лучше False)
    pool_size=10,              # размер пула соединений
    max_overflow=20,           # сколько можно сверх пула
    pool_pre_ping=True,        # проверять соединение перед использованием
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,     # важно для async: объекты остаются валидными после commit
    class_=AsyncSession,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class Base(DeclarativeBase):
    pass
