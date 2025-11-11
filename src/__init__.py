import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.auth.errors import register_auth_errors
from src.auth.routes import auth_router
from src.database.main import init_db
from src.users.routes import user_router
from src.users.errors import register_user_errors

# Create a lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    yield
    print("Server has been stopped")

logger = logging.getLogger(__name__)

version = "v1"

app = FastAPI(
    title="User Data Service for 10,000 users",
    description="A Rest API User Management Backend",
    version=version,
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catches any unhandled exception and returns a structured 500 error response.
    This is a fallback for all errors not caught by specific handlers.
    """
    logger.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "api_error",
                "code": "internal_server_error",
                "message": "An internal server error occurred. We have been notified and are working on a fix.",
                "url": str(request.url),
            }
        },
    )

register_user_errors(app)
register_auth_errors(app)

app.include_router(user_router, prefix=f"/api/{version}/users", tags=["users"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])