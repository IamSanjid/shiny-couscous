from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from sqlalchemy import text

app = FastAPI()

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # This executes a simple query to verify the connection is alive
    result = await db.execute(text("SELECT 'Connection Successful';"))
    return {"status": result.scalar()}

@app.get("/john")
async def find_john(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT first_name, last_name FROM contacts WHERE company_id = 1 LIMIT 1;"))
    contact = result.fetchone()
    if contact is None:
        return {"contact": None}
    return {"contact": {"first_name": contact[0], "last_name": contact[1]}}