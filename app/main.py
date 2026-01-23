from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from sqlalchemy import text
from ai_integration import aparse_contact_info

app = FastAPI()

class ParseRequest(BaseModel):
    text: str
    llm: str

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # This executes a simple query to verify the connection is alive
    result = await db.execute(text("SELECT 'ok';"))
    return {"status": result.scalar(), "database": "connected"}

@app.post("/parse")
async def find_user(req: ParseRequest, db: AsyncSession = Depends(get_db)):
    contact = await aparse_contact_info(req.text)
    name = contact.name.strip() if contact.name else None
    first_name, last_name = name.split(" ") if name else (None, None)
    email = contact.email
    phone = contact.phone
    found_in_database = False

    if not first_name and not last_name and not email and not phone:
        return {
            "name": None,
            "email": None,
            "phone": None,
            "found_in_database": False,
            "company": None
        }

    query = text("""
                 SELECT first_name, last_name, email, phone, company_id FROM contacts
                 WHERE email = :email OR phone = :phone OR (first_name = :first_name AND last_name = :last_name)
                 LIMIT 1
                 """)
    result = await db.execute(query, {"email": email, "phone": phone, "first_name": first_name, "last_name": last_name})
    user_record = result.fetchone()

    if not user_record:
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "found_in_database": False,
            "company": None
        }
    found_in_database = True
    query = text("SELECT name FROM companies WHERE company_id = :company_id")
    result = await db.execute(query, {"company_id": user_record.company_id})
    company_record = result.fetchone()

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "found_in_database": found_in_database,
        "company": company_record.name if company_record else None
    }