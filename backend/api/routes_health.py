"""Health check routes for VisionGuard."""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health_check():
    """Returns the operational status of the VisionGuard service."""
    return {
        "status": "ok",
        "service": "VisionGuard"
    }
