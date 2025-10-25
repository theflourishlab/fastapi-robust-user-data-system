from pydantic import BaseModel
import uuid


class UserCreateSchema(BaseModel):
    firstname: str
    lastname: str
    email: str
    username: str
    password: str

class UserReadSchema(BaseModel):
    id: uuid.UUID
    firstname: str
    lastname: str
    email: str
    username: str


class UserUpdateSchema(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    username: str | None = None
