import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.main import get_session
from src.users.models import User
from .schemas import UserCreateSchema, TokenSchema, UserLoginSchema
from .service import AuthService
from .dependencies import get_user_from_refresh_token
from .utils import create_access_token, verify_password

auth_router = APIRouter()
auth_service = AuthService()

logger = logging.getLogger(__name__)


@auth_router.post("/signup")
async def create_user_account(
    user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)
) -> User:
    """Create a new user account."""
    try:
        return await auth_service.create_user(user_data=user_data, session=session)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user.")


@auth_router.post("/login", response_model=TokenSchema)
async def login_for_access_token(
    login_data: UserLoginSchema,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return an access token."""
    user = await auth_service.get_user_by_email(email=login_data.email, session=session)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    token_data = {"sub": user.email, "id": str(user.id)}
    access_token = create_access_token(user_data=token_data, refresh=False)
    refresh_token = create_access_token(user_data=token_data, refresh=True)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post("/refresh", response_model=TokenSchema)
async def refresh_access_token(current_user: User = Depends(get_user_from_refresh_token)):
    """Generate a new access and refresh token."""
    token_data = {"sub": current_user.email, "id": str(current_user.id)}
    
    access_token = create_access_token(user_data=token_data, refresh=False)
    refresh_token = create_access_token(user_data=token_data, refresh=True)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}