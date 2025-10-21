from fastapi import status, HTTPException, Response, APIRouter, Depends
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.main import get_session
from src.users.models import User
from src.users.schemas import UserCreateSchema, UserUpdateSchema
from src.users.services import UserService

user_router = APIRouter()
user_service = UserService()


@user_router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_a_user(user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)) -> User:
    """Create a new user."""
    return await user_service.create_user(user_data=user_data, session=session)


@user_router.get("/all", response_model=List[User])
async def get_all_users(session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100) -> List[User]:
    """Returns a paginated list of non-deleted users."""
    return await user_service.get_all_users(session=session, skip=skip, limit=limit)


@user_router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> User:
    """Get a single non-deleted user by id."""
    return await user_service.get_user_by_id(user_id=user_id, session=session)


@user_router.patch("/{user_id}", response_model=User)
async def update_part_of_a_user(user_id: uuid.UUID, user_data: UserUpdateSchema, session: AsyncSession = Depends(get_session)) -> User:
    """Partially update a user's details."""
    return await user_service.update_part_of_a_user(user_id=user_id, user_data=user_data, session=session)


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Soft delete a user by setting the is_deleted flag to true."""
    await user_service.soft_delete_user(user_id=user_id, session=session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.delete("/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Permanently delete a user from the database."""
    await user_service.hard_delete_user(user_id=user_id, session=session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@user_router.patch("/{user_id}/restore", response_model=User)
async def restore_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> User:
    """Restore a soft-deleted user by setting is_deleted to false."""
    return await user_service.restore_user(user_id=user_id, session=session)