from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from common.error_messages import ErrorMessages
from dependencies.user import current_active_user
from services.machine.machine_pickup_point_schemas import CreateMachinePickupPointDto
from services.machine.machine_pickup_point_schemas import MachinePickupPointResponseDto
from services.machine.machine_pickup_point_schemas import MachinePickupPointSearchDto
from services.machine.machine_pickup_point_schemas import UpdateMachinePickupPointDto
from services.machine.machine_pickup_point_service import MachinePickupPointCrudService

pickup_points_router = APIRouter(prefix="/pickup-points", tags=["machine_pickup_points"],
                                 dependencies=[Depends(current_active_user)])


@pickup_points_router.post("/", response_model=MachinePickupPointResponseDto, status_code=status.HTTP_201_CREATED)
async def create_point(create_point_dto: CreateMachinePickupPointDto,
                       service: MachinePickupPointCrudService = Depends(MachinePickupPointCrudService.get_instance)):
    return await service.create_point(create_point_dto)


@pickup_points_router.patch("/{point_id}", response_model=MachinePickupPointResponseDto)
async def patch_point(point_id: UUID, patch_point_dto: UpdateMachinePickupPointDto,
                      service: MachinePickupPointCrudService = Depends(MachinePickupPointCrudService.get_instance)):
    return await service.update_point(point_id, patch_point_dto)


@pickup_points_router.get("/{point_id}", response_model=MachinePickupPointResponseDto)
async def get_point(point_id: UUID,
                    service: MachinePickupPointCrudService = Depends(MachinePickupPointCrudService.get_instance)):
    point = await service.get_point_by_id(point_id)
    return point


@pickup_points_router.delete("/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_point(point_id: UUID,
                       service: MachinePickupPointCrudService = Depends(MachinePickupPointCrudService.get_instance)):
    success = await service.delete_point_by_id(point_id)

    if not success:
        raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_NOT_FOUND)

    return {"detail": "Machine deleted successfully"}


@pickup_points_router.post("/search", response_model=list[MachinePickupPointResponseDto])
async def search_points(request: MachinePickupPointSearchDto,
                        service: MachinePickupPointCrudService = Depends(MachinePickupPointCrudService.get_instance)):
    return await service.search_points(request)
