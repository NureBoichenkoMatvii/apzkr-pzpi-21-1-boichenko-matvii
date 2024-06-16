import uuid

from pydantic import BaseModel


class UuidDto(BaseModel):
    id: uuid.UUID


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 5


class OrderByParams(BaseModel):
    order_by_column: str = "id"
    desc: bool = False
