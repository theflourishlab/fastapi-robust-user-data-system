from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status

from src.users.errors import create_exception_handler


class AuthException(Exception):
    """Base class for authentication-related exceptions."""
    pass


class InvalidCredentialsException(AuthException):
    """Raised when login credentials (email/password) are incorrect."""
    pass


class TokenExpiredException(AuthException):
    """Raised when a JWT has expired."""
    pass


class TokenRevokedException(AuthException):
    """Raised when a JWT has been revoked (e.g., via logout)."""
    pass


class InvalidTokenException(AuthException):
    """Raised for any other JWT validation error."""
    pass


class InsufficientPermissionsException(AuthException):
    """Raised when a user does not have the required role for an action."""
    pass


def register_auth_errors(app: FastAPI):
    """Registers all custom auth exception handlers with the FastAPI app."""
    app.add_exception_handler(
        InvalidCredentialsException,
        create_exception_handler(status.HTTP_401_UNAUTHORIZED, "authentication_error", "invalid_credentials")
    )
    app.add_exception_handler(
        TokenExpiredException,
        create_exception_handler(status.HTTP_401_UNAUTHORIZED, "authentication_error", "token_expired")
    )
    app.add_exception_handler(
        TokenRevokedException,
        create_exception_handler(status.HTTP_403_FORBIDDEN, "authentication_error", "token_revoked")
    )
    app.add_exception_handler(
        InvalidTokenException,
        create_exception_handler(status.HTTP_401_UNAUTHORIZED, "authentication_error", "invalid_token")
    )
    app.add_exception_handler(
        InsufficientPermissionsException,
        create_exception_handler(status.HTTP_403_FORBIDDEN, "permission_error", "insufficient_permissions")
    )