from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from common.error_messages import ErrorMessages
from dependencies.user import current_active_user
from services.machine.machine_medicine_slot_schemas import (CreateMachineMedicineSlotDto,
                                                            UpdateMachineMedicineSlotDto,
                                                            MachineMedicineSlotResponseDto)
from services.machine.machine_medicine_slot_service import MachineMedicineSlotCrudService

slots_router = APIRouter(prefix="/medicine-slots", tags=["machine_medicine_slots"], dependencies=[Depends(current_active_user)])


@slots_router.post("/", response_model=MachineMedicineSlotResponseDto, status_code=status.HTTP_201_CREATED)
async def create_slot(create_slot_dto: CreateMachineMedicineSlotDto,
                      service: MachineMedicineSlotCrudService = Depends(MachineMedicineSlotCrudService.get_instance)):
    return await service.create_slot(create_slot_dto)


@slots_router.put("/{slot_id}", response_model=MachineMedicineSlotResponseDto)
async def update_slot(slot_id: UUID, update_slot_dto: UpdateMachineMedicineSlotDto,
                      service: MachineMedicineSlotCrudService = Depends(MachineMedicineSlotCrudService.get_instance)):
    return await service.update_slot(slot_id, update_slot_dto)


@slots_router.get("/{slot_id}", response_model=MachineMedicineSlotResponseDto)
async def get_slot(slot_id: UUID,
                   service: MachineMedicineSlotCrudService = Depends(MachineMedicineSlotCrudService.get_instance)):
    return await service.get_slot_by_id(slot_id)


@slots_router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(slot_id: UUID,
                      service: MachineMedicineSlotCrudService = Depends(MachineMedicineSlotCrudService.get_instance)):
    success = await service.delete_slot_by_id(slot_id)
    if not success:
        raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_SLOT_NOT_FOUND)
    return {"detail": "Slot deleted successfully"}


@slots_router.post("/search", response_model=list[MachineMedicineSlotResponseDto])
async def search_slots(filters: dict,
                       service: MachineMedicineSlotCrudService = Depends(MachineMedicineSlotCrudService.get_instance)):
    return await service.search_slots(filters)
