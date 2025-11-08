from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Response, APIRouter, Depends
from src.database.main import get_session
from src.users.models import User
from src.auth.schemas import UserUpdateSchema
from src.users.services import UserService
from src.auth.dependencies import get_current_user
from src.auth.dependencies import RoleChecker


user_router = APIRouter()
user_service = UserService()

# Dependency for admin-only access
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@user_router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the current logged-in user's details."""
    return current_user


@user_router.get("/all", response_model=List[User], dependencies=[admin_only])
async def get_all_users(session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100) -> List[User]:
    """Returns a paginated list of non-deleted users."""
    return await user_service.get_all_users(session=session, skip=skip, limit=limit)


@user_router.get("/{user_id}", response_model=User, dependencies=[Depends(get_current_user)])
async def get_user_by_id(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> User:
    """Get a single non-deleted user by id."""
    return await user_service.get_user_by_id(user_id=user_id, session=session)


@user_router.patch("/{user_id}", response_model=User, dependencies=[Depends(get_current_user)])
async def update_part_of_a_user(user_id: uuid.UUID, user_data: UserUpdateSchema, session: AsyncSession = Depends(get_session)) -> User:
    """Partially update a user's details."""
    return await user_service.update_part_of_a_user(user_id=user_id, user_data=user_data, session=session)


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
async def soft_delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Soft delete a user by setting the is_deleted flag to true."""
    await user_service.soft_delete_user(user_id=user_id, session=session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.delete("/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_only])
async def hard_delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Permanently delete a user from the database."""
    await user_service.hard_delete_user(user_id=user_id, session=session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@user_router.patch("/{user_id}/restore", response_model=User, dependencies=[admin_only])
async def restore_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> User:
    """Restore a soft-deleted user by setting is_deleted to false."""
    return await user_service.restore_user(user_id=user_id, session=session)