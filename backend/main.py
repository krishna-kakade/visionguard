"""VisionGuard Backend Application Entry Point.

Explainable Visual Fact-Checking Assistant using Multimodal Image Forensics
and AI-assisted Verification.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from api.routes_health import router as health_router
from api.routes_analysis import router as analysis_router

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("visionguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes SQLite database tables and resources on application startup."""
    logger.info("Initializing VisionGuard database...")
    init_db()
    logger.info("VisionGuard engine ready.")
    yield
    logger.info("VisionGuard backend shutting down.")


app = FastAPI(
    title="VisionGuard API",
    description="Explainable Visual Fact-Checking Assistant using Multimodal Image Forensics and AI-assisted Verification",
    version="1.0.0",
    lifespan=lifespan
)

# Rule 37: Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(analysis_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
