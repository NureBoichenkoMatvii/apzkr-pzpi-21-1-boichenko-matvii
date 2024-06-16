from datetime import timezone
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression as sql

from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from database import db
from database.models import Machine
from database.models import MachineMedicineSlot
from database.models import MachinePickupPoint
from services.base_service import BaseCrudService
from services.machine.machine_schemas import *
from services.mqtt.mqtt_handlers_service import MQTTHandlersService


class MachineCrudService(BaseCrudService[Machine]):
    def __init__(self, db_session: AsyncSession, handlers_service: MQTTHandlersService):
        super().__init__(Machine, db_session)
        self.handlers_service: MQTTHandlersService = handlers_service

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session),
                     handlers_service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
        return cls(db_session=db_session, handlers_service=handlers_service)

    async def post_machine(self, create_machine_dto: CreateMachineDto):
        machine = await Machine.create(self.db, **create_machine_dto.model_dump())
        res = await db_row_to_pydantic(machine, MachineResponseDto)
        return res

    async def put_machine(self, machine_id: UUID, put_machine_dto: PutMachineDto):
        machine = await Machine.update(
            self.db, {"id": machine_id}, **put_machine_dto.model_dump())
        return await db_row_to_pydantic(machine, MachineResponseDto)

    async def patch_machine(self, machine_id: UUID, patch_machine_dto: PatchMachineDto):
        machine = await Machine.update(
            self.db, {"id": machine_id}, **patch_machine_dto.model_dump(exclude_unset=True))
        return await db_row_to_pydantic(machine, MachineResponseDto)

    async def get_machine_by_id(self, machine_id: UUID):
        machine = await Machine.get(self.db, {"id": machine_id})

        if not machine:
            raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_NOT_FOUND)

        return await db_row_to_pydantic(machine, MachineResponseDto)

    async def delete_machine_by_id(self, machine_id: UUID):
        machine_mac: str = (await Machine.get(self.db, {"id": machine_id})).mac
        success: bool = await Machine.delete(self.db, {"id": machine_id})

        await self.handlers_service.send_machine_unregister_request(machine_mac)

        return success

    async def search_machines(self, request: SearchMachinesRequest):
        query = sql.select(Machine).options()

        if request.medicines:
            # Ensure each specified medicine has sufficient stock
            for medicine_id, required_count in request.medicines.items():
                subquery = sql.select(MachineMedicineSlot.machine_id).where(
                    sql.and_(
                        MachineMedicineSlot.medicine_id == medicine_id,
                        (MachineMedicineSlot.total_count - MachineMedicineSlot.reserved_count) >= required_count
                    )
                ).exists()
                query = query.where(subquery)  # Combine all medicine conditions

        if request.pickup_point_stop:
            # Filter for machines that will stop at the specified pickup point
            query = query.join(MachinePickupPoint).where(sql.and_(
                MachinePickupPoint.pickup_point_id == request.pickup_point_stop,
                MachinePickupPoint.arrival_at > datetime.now(tz=timezone.utc)
            ))

        if request.simple_filters:
            query = query.filter_by(**request.simple_filters.model_dump(exclude_unset=True))

        if request.order_by:
            order_by = request.order_by
            if order_by.desc:
                query = query.order_by(desc(getattr(Machine, order_by.order_by_column)))
            else:
                query = query.order_by(asc(getattr(Machine, order_by.order_by_column)))

        if request.pagination:
            pagination = request.pagination
            query = query.offset(pagination.offset).limit(pagination.limit)

        machines = (await self.db.scalars(query)).all()

        results = []
        for m in machines:
            results.append(await db_row_to_pydantic(m, MachineResponseDto))

        return results
