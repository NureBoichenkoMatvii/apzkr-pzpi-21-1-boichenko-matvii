from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from common.error_messages import ErrorMessages
from dependencies.user import current_active_user
from services.machine.machine_schemas import CreateMachineDto
from services.machine.machine_schemas import MachineResponseDto
from services.machine.machine_schemas import PatchMachineDto
from services.machine.machine_schemas import PutMachineDto
from services.machine.machine_schemas import SearchMachinesRequest
from services.machine.machine_service import MachineCrudService
from .machine_pickup_point_router import pickup_points_router
from .machines_medicine_slots_router import slots_router
from .machines_statistics_router import statistics_router

machines_router = APIRouter(prefix="/machines", tags=["machines"], dependencies=[Depends(current_active_user)])
machines_router.include_router(slots_router)
machines_router.include_router(statistics_router)
machines_router.include_router(pickup_points_router)


@machines_router.post("/", response_model=MachineResponseDto, status_code=status.HTTP_201_CREATED)
async def create_machine(create_machine_dto: CreateMachineDto,
                         service: MachineCrudService = Depends(MachineCrudService.get_instance)):
    return await service.post_machine(create_machine_dto)


@machines_router.put("/{machine_id}", response_model=MachineResponseDto)
async def update_machine(machine_id: UUID, put_machine_dto: PutMachineDto,
                         service: MachineCrudService = Depends(MachineCrudService.get_instance)):
    return await service.put_machine(machine_id, put_machine_dto)


@machines_router.patch("/{machine_id}", response_model=MachineResponseDto)
async def patch_machine(machine_id: UUID, patch_machine_dto: PatchMachineDto,
                        service: MachineCrudService = Depends(MachineCrudService.get_instance)):
    return await service.patch_machine(machine_id, patch_machine_dto)


@machines_router.get("/{machine_id}", response_model=MachineResponseDto)
async def get_machine(machine_id: UUID, service: MachineCrudService = Depends(MachineCrudService.get_instance)):
    machine = await service.get_machine_by_id(machine_id)

    return machine


@machines_router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(machine_id: UUID, service: MachineCrudService = Depends(MachineCrudService.get_instance)):
    success = await service.delete_machine_by_id(machine_id)

    if not success:
        raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_NOT_FOUND)

    return {"detail": "Machine deleted successfully"}


@machines_router.post("/search", response_model=list[MachineResponseDto])
async def search_machines(request: SearchMachinesRequest,
                          service: MachineCrudService = Depends(MachineCrudService.get_instance)):
    return await service.search_machines(request)
