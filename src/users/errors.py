from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status

class UserException(Exception):
    """This is the base class for all user Exception"""
    pass


class UserNotFoundException(UserException):
    """Raised when a user is not found in the database."""
    pass


class UserAlreadyExistsException(UserException):
    """Raised when trying to create a user that already exists."""
    pass


class UsernameConflictException(UserException):
    """Raised when a username is already registered by another user during an update."""
    pass


class EmailConflictException(UserException):
    """Raised when an email is already in use by another user during an update."""
    pass


class UserNotDeletedException(UserException):
    """Raised when attempting to restore a user that is not soft-deleted."""
    pass



def create_exception_handler(
    status_code: int, error_type: str, error_code: str
) -> Callable[[Request, Exception], JSONResponse]:
    """
    Factory function to create a FastAPI exception handler that returns a
    Stripe-like error response.
    """
    async def exception_handler(request: Request, exc: UserException):
        """
        Handles the exception and returns a structured JSON response.
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "type": error_type,
                    "code": error_code,
                    "message": str(exc),  # Use the dynamic message from the exception
                }
            },
        )

    return exception_handler



def register_user_errors(app: FastAPI):
    """Registers all custom user exception handlers with the FastAPI app."""
    app.add_exception_handler(
        UserNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="invalid_request_error",
            error_code="resource_not_found",
        ),
    )
    app.add_exception_handler(
        UserAlreadyExistsException, # Note: This is not currently used in services.py but is good to have.
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            error_type="invalid_request_error",
            error_code="resource_already_exists",
        ),
    )
    app.add_exception_handler(
        UsernameConflictException,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            error_type="invalid_request_error",
            error_code="username_taken",
        ),
    )
    app.add_exception_handler(
        EmailConflictException,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            error_type="invalid_request_error",
            error_code="email_in_use",
        ),
    )
    app.add_exception_handler(
        UserNotDeletedException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="invalid_request_error",
            error_code="user_not_deleted",
        ),
    )