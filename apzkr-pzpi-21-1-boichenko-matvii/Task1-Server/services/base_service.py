from typing import Type, Generic, TypeVar, List
from uuid import UUID

from database.models import DbBaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import db


ModelType = TypeVar('ModelType', bound=DbBaseModel)


class BaseCrudService(Generic[ModelType]):
    def __init__(self, model_class: Type[ModelType], db_session: AsyncSession):
        self.model_class: Type[ModelType] = model_class
        self.db: AsyncSession = db_session

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session)):
        return cls(db_session=db_session)

    # async def create_item(self, create_dto):
    #     model_instance: ModelType = await self.model_class.create(self.db, **create_dto.model_dump())
    #     return model_instance
    #
    # async def update_item(self, model_id, update_dto):
    #     model_instance: ModelType = await self.model_class.update(
    #         self.db, {"id": model_id}, **update_dto.model_dump())
    #     return model_instance
    #
    # async def patch_item(self, model_id, patch_dto):
    #     model_instance: ModelType = await self.model_class.update(
    #         self.db, {"id": model_id}, **patch_dto.model_dump())
    #     return model_instance

    async def get_by_id(self, model_id: UUID):
        model_instance: ModelType = await self.model_class.get(self.db, {"id": model_id})
        return model_instance

    async def delete_by_id(self, model_id: UUID):
        success: bool = await self.model_class.delete(self.db, {"id": model_id})
        return success

    async def search(self, search_filters: dict):
        models: List[ModelType] = await self.model_class.get(self.db, search_filters)
        return models