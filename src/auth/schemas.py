from pydantic import BaseModel, EmailStr, Field
import uuid


class UserCreateSchema(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    username: str
    password: str

class UserUpdateSchema(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    username: str | None = None

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserLoginSchema(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
