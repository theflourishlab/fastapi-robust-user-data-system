# Define all crud behaviours with proper status codes and error handling
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from ..auth.schemas import UserUpdateSchema
from .models import User
import uuid
from fastapi import HTTPException, status
from typing import List

class UserService:
    async def get_all_users(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all non-deleted users with pagination."""
        stmt = select(User).where(User.is_deleted == False).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await session.execute(stmt)
        users = result.scalars().all()
        return list(users)

    async def get_user_by_id(self, user_id: uuid.UUID, session: AsyncSession) -> User:
        """Get a single non-deleted user by id."""
        user = await session.get(User, user_id)
        if not user or user.is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update_part_of_a_user(self, user_id: uuid.UUID, user_data: UserUpdateSchema, session: AsyncSession) -> User:
        """Partially update a user's details."""
        db_user = await self.get_user_by_id(user_id, session) # Reuse get_user_by_id to handle not found/deleted cases

        update_data = user_data.model_dump(exclude_unset=True)

        if not update_data:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")

        # Check for username/email conflicts if they are being updated
        if 'username' in update_data or 'email' in update_data:
            query_filter = []
            if 'username' in update_data:
                query_filter.append(User.username == update_data['username'])
            if 'email' in update_data:
                query_filter.append(User.email == update_data['email'])
            
            stmt = select(User).where(User.id != user_id).where(or_(*query_filter))
            existing_user = (await session.execute(stmt)).scalars().first()
            if existing_user:
                if 'username' in update_data and existing_user.username == update_data['username']:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
                if 'email' in update_data and existing_user.email == update_data['email']:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

        for key, value in update_data.items():
            setattr(db_user, key, value)

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    async def soft_delete_user(self, user_id: uuid.UUID, session: AsyncSession) -> None:
        """Soft delete a user by setting is_deleted to True."""
        user = await session.get(User, user_id)
        if not user or user.is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or already deleted")

        user.is_deleted = True
        session.add(user)
        await session.commit()

    async def restore_user(self, user_id: uuid.UUID, session: AsyncSession) -> User:
        """Restore a soft-deleted user."""
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not user.is_deleted:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not deleted")

        user.is_deleted = False
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def hard_delete_user(self, user_id: uuid.UUID, session: AsyncSession) -> None:
        """Permanently delete a user from the database."""
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await session.delete(user)
        await session.commit()