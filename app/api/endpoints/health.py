from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ...db.database import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    # This executes a simple query to verify the connection is alive
    result = await db.execute(text("SELECT 'ok';"))
    if not result:
        return {"status": "error", "database": "not connected"}
    return {"status": result.scalar(), "database": "connected"}