import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.redis import add_jti_to_blocklist
from src.database.main import get_session
from src.users.models import User
from .schemas import UserCreateSchema, TokenSchema, UserLoginSchema
from .errors import InvalidCredentialsException
from .service import AuthService
from .dependencies import get_current_user, get_user_from_refresh_token, validate_access_token
from .utils import create_access_token, verify_password

auth_router = APIRouter()
auth_service = AuthService()

logger = logging.getLogger(__name__)


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)
) -> User:
    """Create a new user account."""
    return await auth_service.create_user(user_data=user_data, session=session)


@auth_router.post("/login", response_model=TokenSchema)
async def login_for_access_token(
    login_data: UserLoginSchema,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return an access token."""
    user = await auth_service.get_user_by_email(email=login_data.email, session=session)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise InvalidCredentialsException("Incorrect email or password")
    
    token_data = {"sub": user.email, "id": str(user.id)}
    access_token = create_access_token(user_data=token_data, refresh=False)
    refresh_token = create_access_token(user_data=token_data, refresh=True)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post("/refresh_token", response_model=TokenSchema)
async def refresh_access_token(current_user: User = Depends(get_user_from_refresh_token)):
    """Generate a new access and refresh token."""
    token_data = {"sub": current_user.email, "id": str(current_user.id), "role":current_user.role}
    
    access_token = create_access_token(user_data=token_data, refresh=False)
    refresh_token = create_access_token(user_data=token_data, refresh=True)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@auth_router.post("/logout")
async def revoke_token(
    payload: dict = Depends(validate_access_token),
):
    """
    Logs out the user by adding their current access token's JTI to the blocklist.
    """
    jti = payload.get("jti")
    if jti:
        await add_jti_to_blocklist(jti)
    
    return JSONResponse(
        content={
            "message": "Logged out successfully"
        },
        status_code=status.HTTP_200_OK
    )