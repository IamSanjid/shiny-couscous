from fastapi import FastAPI
from .api.endpoints.health import router as health_router
from .api.endpoints.parse import router as parse_router

app = FastAPI(title="Contact Info Parser")

app.include_router(health_router)

app.include_router(parse_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)