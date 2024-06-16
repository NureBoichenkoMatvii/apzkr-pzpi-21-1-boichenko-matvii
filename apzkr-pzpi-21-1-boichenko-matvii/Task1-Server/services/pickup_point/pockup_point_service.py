from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from database import db
from database.models import PickupPoint
from services.base_service import BaseCrudService
from services.pickup_point.pickup_point_schemas import *


class PickupPointCrudService(BaseCrudService[PickupPoint]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(PickupPoint, db_session)

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session)):
        return cls(db_session=db_session)

    async def create_point(self, create_point_dto: CreatePickupPointDto):
        point = await PickupPoint.create(self.db, **create_point_dto.model_dump())
        return await db_row_to_pydantic(point, PickupPointResponseDto)

    async def update_point(self, point_id: UUID, update_point_dto: PatchPickupPointDto):
        point = await PickupPoint.update(self.db, {"id": point_id}, **update_point_dto.model_dump())
        return await db_row_to_pydantic(point, PickupPointResponseDto)

    async def get_point_by_id(self, point_id: UUID):
        point = await PickupPoint.get(self.db, {"id": point_id})
        if not point:
            raise HTTPException(status_code=404, detail=ErrorMessages.pickup_point.PICKUP_POINT_NOT_FOUND)
        return await db_row_to_pydantic(point, PickupPointResponseDto)

    async def delete_point_by_id(self, point_id: UUID):
        success = await PickupPoint.delete(self.db, {"id": point_id})
        return success

    async def search_points(self, search_filters: dict):
        points = await PickupPoint.get_all(self.db, search_filters)
        return [await db_row_to_pydantic(point, PickupPointResponseDto) for point in points]
