from fastapi import APIRouter

from cache import redis_client


router = APIRouter(tags=["Cache"])


@router.get("/cache/status")
def cache_status():
    if redis_client:
        return {
            "redis": "connected",
            "message": "Redis cache is available"
        }

    return {
        "redis": "not connected",
        "message": "Backend is using PostgreSQL only"
    }