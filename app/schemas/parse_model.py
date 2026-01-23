from pydantic import BaseModel

class ParseRequest(BaseModel):
    text: str
    llm: str

class ParseResponse(BaseModel):
    name: str | None
    email: str | None
    phone: str | None
    found_in_database: bool
    company: str | None