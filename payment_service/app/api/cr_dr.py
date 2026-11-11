from fastapi import APIRouter
from app.models.models import Base
from app.core.db import engine

router_db = APIRouter()

@router_db.post ("/drop_table")
async def dr_table ():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    return {"status": "tables drop_all"}

@router_db.post ("/Create_table")
async def cr_table ():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"status": "tables created"}