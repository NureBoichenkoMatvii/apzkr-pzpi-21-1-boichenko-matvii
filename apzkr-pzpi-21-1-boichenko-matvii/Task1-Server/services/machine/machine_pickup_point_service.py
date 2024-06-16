from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from database import db
from database.models import MachinePickupPoint
from services.base_service import BaseCrudService
from services.machine.machine_pickup_point_schemas import *
from services.medicine.medicine_service import MedicineCrudService
from services.mqtt.mqtt_handlers_service import MQTTHandlersService


class MachinePickupPointCrudService(BaseCrudService[MachinePickupPoint]):
    def __init__(self, db_session: AsyncSession, handlers_service: MQTTHandlersService,
                 medicines_service: MedicineCrudService):
        super().__init__(MachinePickupPoint, db_session)
        self.handlers_service: MQTTHandlersService = handlers_service
        self.medicines_service: MedicineCrudService = medicines_service

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session),
                     handlers_service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance),
                     medicines_service: MedicineCrudService = Depends(MedicineCrudService.get_instance)):
        return cls(db_session=db_session, handlers_service=handlers_service, medicines_service=medicines_service)

    async def create_point(self, create_point_dto: CreateMachinePickupPointDto):
        existing_machine_point = await MachinePickupPoint.get(
            self.db, {
                "machine_id": create_point_dto.machine_id,
                "pickup_point_id": create_point_dto.pickup_point_id,
                "arrival_at": create_point_dto.arrival_at
            })
        if existing_machine_point:
            raise HTTPException(status_code=400, detail=ErrorMessages.Machine.MACHINE_HAS_SUCH_PICKUP_POINT)

        point = await MachinePickupPoint.create(self.db, **create_point_dto.model_dump())

        return await db_row_to_pydantic(point, MachinePickupPointResponseDto)

    async def update_point(self, point_id: UUID, update_point_dto: UpdateMachinePickupPointDto):
        point = await MachinePickupPoint.update(self.db, {"id": point_id}, **update_point_dto.model_dump())
        return await db_row_to_pydantic(point, MachinePickupPointResponseDto)

    async def get_point_by_id(self, point_id: UUID):
        point = await MachinePickupPoint.get(self.db, {"id": point_id})
        if not point:
            raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_PICKUP_POINT_NOT_FOUND)
        return await db_row_to_pydantic(point, MachinePickupPointResponseDto)

    async def delete_point_by_id(self, point_id: UUID):
        success = await MachinePickupPoint.delete(self.db, {"id": point_id})
        return success

    async def search_points(self, search_filters: MachinePickupPointSearchDto):
        points = await MachinePickupPoint.get_all(self.db, search_filters.column_filters)
        return [await db_row_to_pydantic(point, MachinePickupPointResponseDto) for point in points]
