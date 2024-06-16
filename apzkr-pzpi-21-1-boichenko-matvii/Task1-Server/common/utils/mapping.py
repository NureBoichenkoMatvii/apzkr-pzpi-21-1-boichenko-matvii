from typing import TypeVar, Type

from pydantic import BaseModel
from sqlalchemy import Row

from database.models import DbBaseModel as DbBase

DBModelType = TypeVar("DBModelType", bound=DbBase)
PydanticModelType = TypeVar("PydanticModelType", bound=BaseModel)


async def db_row_to_pydantic(db_result_row: Row | DBModelType, pydantic_model: Type[PydanticModelType],
                             validate: bool = True) -> PydanticModelType:
    # print(type(db_result_row))
    columns = db_result_row.__mapper__.columns
    if isinstance(db_result_row, DbBase):
        model_dict = {col.name: getattr(db_result_row, col.name) for col in columns}
    else:
        model_dict = db_result_row._asdict().copy()

    if validate:
        return pydantic_model(**model_dict)
    else:
        return pydantic_model.model_construct(**model_dict)
