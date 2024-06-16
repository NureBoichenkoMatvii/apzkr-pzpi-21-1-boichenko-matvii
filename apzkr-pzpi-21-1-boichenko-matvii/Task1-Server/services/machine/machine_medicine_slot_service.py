from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import db
from database.models import MachineMedicineSlot, Machine, Medicine
from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from services.base_service import BaseCrudService
from services.machine.machine_medicine_slot_schemas import *
from services.mqtt.mqtt_handlers_schemas import InventoryItemInfo
from services.mqtt.mqtt_handlers_service import MQTTHandlersService
from services.medicine.medicine_service import MedicineCrudService


class MachineMedicineSlotCrudService(BaseCrudService[MachineMedicineSlot]):
    def __init__(self, db_session: AsyncSession, handlers_service: MQTTHandlersService, medicines_service: MedicineCrudService):
        super().__init__(MachineMedicineSlot, db_session)
        self.handlers_service: MQTTHandlersService = handlers_service
        self.medicines_service: MedicineCrudService = medicines_service

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session),
                     handlers_service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance),
                     medicines_service: MedicineCrudService = Depends(MedicineCrudService.get_instance)):
        return cls(db_session=db_session, handlers_service=handlers_service, medicines_service=medicines_service)

    async def create_slot(self, create_slot_dto: CreateMachineMedicineSlotDto):
        machine = await Machine.get(self.db, {"id": create_slot_dto.machine_id})

        existing_machine_slot = await MachineMedicineSlot.get(
            self.db, {
                "machine_id": create_slot_dto.machine_id,
                "medicine_id": create_slot_dto.medicine_id
            })
        if existing_machine_slot:
            raise HTTPException(status_code=400, detail=ErrorMessages.Machine.MACHINE_HAS_SUCH_MEDICINE_SLOT)

        medicine_dto = await self.medicines_service.get_by_id(create_slot_dto.medicine_id)

        slot = await MachineMedicineSlot.create(self.db, **create_slot_dto.model_dump())

        await self.handlers_service.send_inventory_update_request(machine.mac, {
            str(slot.id): InventoryItemInfo(
                medicine_type=medicine_dto.type,
                medicine_name=medicine_dto.name,
                left_amount=slot.total_count,
            )
        })

        return await db_row_to_pydantic(slot, MachineMedicineSlotResponseDto)

    async def update_slot(self, slot_id: UUID, update_slot_dto: UpdateMachineMedicineSlotDto):
        slot = await MachineMedicineSlot.update(self.db, {"id": slot_id}, **update_slot_dto.model_dump())

        await self.handlers_service.send_inventory_update_request(slot.machine.mac, {
            str(slot.id): InventoryItemInfo(
                medicine_type=slot.medicine.type,
                medicine_name=slot.medicine.name,
                left_amount=slot.total_count,
            )
        })

        return await db_row_to_pydantic(slot, MachineMedicineSlotResponseDto)

    async def get_slot_by_id(self, slot_id: UUID):
        slot = await MachineMedicineSlot.get(self.db, {"id": slot_id})
        if not slot:
            raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_SLOT_NOT_FOUND)
        return await db_row_to_pydantic(slot, MachineMedicineSlotResponseDto)

    async def delete_slot_by_id(self, slot_id: UUID):
        success = await MachineMedicineSlot.delete(self.db, {"id": slot_id})
        return success

    async def search_slots(self, search_filters: dict):
        slots = await MachineMedicineSlot.get_all(self.db, search_filters)
        return [await db_row_to_pydantic(slot, MachineMedicineSlotResponseDto) for slot in slots]
