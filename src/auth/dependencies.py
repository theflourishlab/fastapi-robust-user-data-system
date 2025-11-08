import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal, List, Any

from src.database.redis import token_in_blocklist
from src.database.main import get_session
from src.users.models import User
from .errors import InvalidCredentialsException, TokenRevokedException, TokenExpiredException, InvalidTokenException, InsufficientPermissionsException
from src.auth.utils import decode_token
from src.auth.service import AuthService

bearer_scheme = HTTPBearer()
auth_service = AuthService()


def get_user_from_token(token_type: Literal["access", "refresh"]):
    """
    A dependency factory to get a user from a token of a specific type.
    This avoids code duplication for access and refresh token validation.
    """
    async def _get_user(
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        try:
            payload = decode_token(token.credentials)
            if payload is None:
                raise InvalidTokenException("Could not validate credentials")

            # Blocklist check for both token types
            if await token_in_blocklist(payload.get("jti")):
                raise TokenRevokedException("Token has been revoked")

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token has expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenException("Invalid token")

        # Ensure the token is of the expected type
        if payload.get("type") != token_type:
            raise InvalidTokenException(
                f"Invalid token type, expected '{token_type}' token"
            )

        email: str = payload.get("user", {}).get("sub")
        if not email:
            raise InvalidTokenException("Token is missing user information")

        user = await auth_service.get_user_by_email(email=email, session=session)
        if user is None:
            raise InvalidCredentialsException("User from token not found")
        return user
    return _get_user

get_current_user = get_user_from_token("access")
get_user_from_refresh_token = get_user_from_token("refresh")

def validate_token(token_type: Literal["access", "refresh"]):
    """
    A dependency factory that validates a token and returns its payload.
    It performs all security checks (expiry, blocklist, type) without the
    overhead of a database query. Ideal for endpoints that need authentication
    but not the full user object, like logout.
    """
    async def _validate_token(
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    ) -> dict:
        try:
            payload = decode_token(token.credentials)
            if payload is None:
                raise InvalidTokenException("Could not validate credentials")
    
            if await token_in_blocklist(payload.get("jti")):
                raise TokenRevokedException("Token has been revoked")
    
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token has expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenException("Invalid token")
    
        if payload.get("type") != token_type:
            raise InvalidTokenException(
                f"Invalid token type, expected '{token_type}' token"
            )
    
        return payload
    return _validate_token

validate_access_token = validate_token("access")


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        
        raise InsufficientPermissionsException("You are not allowed to perform this action")