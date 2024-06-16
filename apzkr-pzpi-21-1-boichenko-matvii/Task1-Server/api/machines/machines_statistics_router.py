from uuid import UUID

from fastapi import APIRouter, Depends, status

from dependencies.user import current_active_user
from services.machine.machine_statistic_schemas import *
from services.machine.machine_statistic_service import MachineStatisticCrudService

statistics_router = APIRouter(prefix="/statistics", tags=["machine_statistics"],
                              dependencies=[Depends(current_active_user)])


@statistics_router.post("/", response_model=MachineStatisticResponseDto, status_code=status.HTTP_201_CREATED)
async def create_statistic(create_statistic_dto: CreateMachineStatisticDto,
                           service: MachineStatisticCrudService = Depends(MachineStatisticCrudService.get_instance)):
    return await service.create_statistic(create_statistic_dto)


@statistics_router.get("/{statistic_id}", response_model=MachineStatisticResponseDto)
async def get_statistic(statistic_id: UUID,
                        service: MachineStatisticCrudService = Depends(MachineStatisticCrudService.get_instance)):
    return await service.get_statistic_by_id(statistic_id)


@statistics_router.post("/search", response_model=list[MachineStatisticResponseDto])
async def search_machine_statistics(search_dto: MachineStatisticSearchDto,
                                    service: MachineStatisticCrudService = Depends(
                                        MachineStatisticCrudService.get_instance)):
    return await service.search_statistics(search_dto)
