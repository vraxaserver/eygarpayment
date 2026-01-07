import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Payment Service...")
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("🛑 Shutting down Payment Service...")
    await close_db()
    print("✅ Database connections closed")


# If behind nginx at /payment/, set ROOT_PATH=/payment
# If running at root, leave it empty.
ROOT_PATH = os.getenv("ROOT_PATH", "").rstrip("/")
if ROOT_PATH and not ROOT_PATH.startswith("/"):
    ROOT_PATH = f"/{ROOT_PATH}"

app = FastAPI(
    title="Payment Service",
    description="Microservice for handling payment transactions",
    version="1.0.0",
    lifespan=lifespan,

    # Critical fix for reverse-proxy subpath deployments
    root_path=ROOT_PATH,

    # Keep these as "app-relative" paths (FastAPI will apply root_path automatically)
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"], summary="Health Check", status_code=status.HTTP_200_OK)
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.SERVICE_NAME,
            "version": "1.0.0",
        }
    )


@app.get("/", tags=["root"], summary="Root Endpoint", status_code=status.HTTP_200_OK)
async def root():
    # Build links that include the prefix (root_path) correctly
    prefix = app.root_path or ""
    return JSONResponse(
        content={
            "message": "Welcome to Payment Service API",
            "version": "1.0.0",
            "docs": f"{prefix}/docs",
            "health": f"{prefix}/health",
            "openapi": f"{prefix}/openapi.json",
        }
    )


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8002")),  # ✅ payment service port
        reload=os.getenv("UVICORN_RELOAD", "false").lower() == "true",  # ✅ no reload by default
    )
