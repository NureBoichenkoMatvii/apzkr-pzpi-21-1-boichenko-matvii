import uuid
from datetime import datetime

from fastapi_users import schemas

from database.models import UserRole


class UserResponse(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str
    role: UserRole
    birthdate: None | datetime


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    role: UserRole | None = None
    birthdate: datetime | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole | None = None
    birthdate: None | datetime = None
