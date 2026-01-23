from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ...db.database import get_db
from ...schemas.parse_model import ParseRequest, ParseResponse
from ai_integration import parse_contact_info

router = APIRouter(prefix="/parse", tags=["parse"])

@router.post("/", response_model=ParseResponse)
async def find_user(req: ParseRequest, db: AsyncSession = Depends(get_db)):
    user = parse_contact_info(req.text)
    name_val = user.name
    name = name_val.strip() if isinstance(name_val, str) else None
    if name:
        parts = name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else None
    else:
        first_name, last_name = None, None
    email = user.email
    phone = user.phone
    found_in_database = False

    if not first_name and not last_name and not email and not phone:
        return ParseResponse(
            name=None,
            email=None,
            phone=None,
            found_in_database=False,
            company=None
        )

    query = text("""
                 SELECT first_name, last_name, email, phone, company_id FROM contacts
                 WHERE email = :email OR phone = :phone OR (first_name = :first_name AND last_name = :last_name)
                 LIMIT 1
                 """)
    result = await db.execute(query, {"email": email, "phone": phone, "first_name": first_name, "last_name": last_name})
    user_record = result.fetchone()

    if not user_record:
        return ParseResponse(
            name=name,
            email=email,
            phone=phone,
            found_in_database=False,
            company=None
        )
    found_in_database = True
    query = text("SELECT name FROM companies WHERE company_id = :company_id")
    result = await db.execute(query, {"company_id": user_record.company_id})
    company_record = result.fetchone()

    return ParseResponse(
        name=name,
        email=email,
        phone=phone,
        found_in_database=found_in_database,
        company=company_record.name if company_record else None
    )