from sqlmodel import SQLModel, Field, Column,func
import sqlalchemy.dialects.sqlite as s
from sqlalchemy import String, DateTime
import uuid
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        # The sa_column is not strictly needed here as SQLModel can infer it,
        # but if you need specific column args like `unique`, you'd add it.
    )
    firstname: str
    lastname: str
    email: str = Field(
        sa_column=Column(
            String,
            index=True,
            nullable=False,
            unique=True,
        )
    )
    username: str = Field(
        sa_column=Column(
            String,
            index=True,
            nullable=False,
            unique=True,
        )
        )
    role: str = Field(
        default="user", sa_column=Column(String, nullable=False, server_default="user"))

    hashed_password: str = Field(
        exclude=True,
        nullable=False)
    is_deleted: bool = Field(default=False)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False)
    )



class UserActivityLog(SQLModel, table=True):
    __tablename__ = "user_activity_logs"
    id: int | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    action: str
    performed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    details: str
