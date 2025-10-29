from fastapi import FastAPI
from src.users.routes import user_router
from src.auth.routes import auth_router
from src.database.main import init_db
from contextlib import asynccontextmanager

# Create a lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    yield
    print("Server has been stopped")



version = "v1"

app = FastAPI(
    title="User Data Service for 10,000 users",
    description="A Rest API User Management Backend",
    version=version,
    lifespan=lifespan
)

app.include_router(user_router, prefix=f"/api/{version}/users", tags=["users"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])