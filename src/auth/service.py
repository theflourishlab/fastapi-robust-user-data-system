from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.users.models import User

from .schemas import UserCreateSchema
from .utils import generate_passwd_hash


class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.execute(statement)

        user = result.scalars().first()

        return user

    async def create_user(self, user_data: UserCreateSchema, session: AsyncSession):
        # Check if username or email already exists
        stmt = select(User).where((User.username == user_data.username) | (User.email == user_data.email))
        existing_user = (await session.execute(stmt)).scalars().first()
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
            if existing_user.email == user_data.email:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user_dict = user_data.model_dump()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = generate_passwd_hash(password)

        new_user = User(**user_dict)
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


    async def update_user(self, user:User , user_data: dict,session:AsyncSession):

        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()

        return user