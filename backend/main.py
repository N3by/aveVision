from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, classify


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    if os.getenv("TESTING") != "1":
        from app.services.model import load_model_from_gcs
        load_model_from_gcs()
    yield
    from app.database import close_db
    await close_db()


app = FastAPI(title="AveVision API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classify.router)


@app.get("/health")
async def health():
    from app.services.model import is_model_loaded
    return {"status": "ok", "model_loaded": is_model_loaded()}
