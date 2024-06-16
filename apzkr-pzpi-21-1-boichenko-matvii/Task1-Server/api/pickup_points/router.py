from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from dependencies.user import current_active_user
from services.pickup_point.metrics_service import CalculateDistanceRequest
from services.pickup_point.metrics_service import DistanceTimeResponse
from services.pickup_point.metrics_service import MetricsService
from services.pickup_point.metrics_service import RouteOptimizationRequest
from services.pickup_point.metrics_service import RouteOptimizationResult
from services.pickup_point.pickup_point_schemas import CreatePickupPointDto
from services.pickup_point.pickup_point_schemas import PatchPickupPointDto
from services.pickup_point.pickup_point_schemas import PickupPointResponseDto
from services.pickup_point.pockup_point_service import PickupPointCrudService

pickup_points_router = APIRouter(prefix="/pickup-points",
                                 tags=["pickup_points"],
                                 dependencies=[Depends(current_active_user)])


@pickup_points_router.post("/", response_model=PickupPointResponseDto, status_code=status.HTTP_201_CREATED)
async def create_point(create_point_dto: CreatePickupPointDto,
                       service: PickupPointCrudService = Depends(PickupPointCrudService.get_instance)):
    return await service.create_point(create_point_dto)


@pickup_points_router.patch("/{medicine_id}", response_model=PickupPointResponseDto)
async def patch_point(medicine_id: UUID, patch_point_dto: PatchPickupPointDto,
                      service: PickupPointCrudService = Depends(PickupPointCrudService.get_instance)):
    return await service.update_point(medicine_id, patch_point_dto)


@pickup_points_router.get("/{medicine_id}", response_model=PickupPointResponseDto)
async def get_point(medicine_id: UUID,
                    service: PickupPointCrudService = Depends(PickupPointCrudService.get_instance)):
    return await service.get_point_by_id(medicine_id)


@pickup_points_router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_point(medicine_id: UUID,
                       service: PickupPointCrudService = Depends(PickupPointCrudService.get_instance)):
    success = await service.delete_point_by_id(medicine_id)
    if not success:
        raise HTTPException(status_code=404, detail="point not found")
    return {"detail": "point deleted successfully"}


@pickup_points_router.post("/search", response_model=list[PickupPointResponseDto])
async def search_points(filters: dict,
                        service: PickupPointCrudService = Depends(PickupPointCrudService.get_instance)):
    return await service.search_points(filters)


@pickup_points_router.post("/optimize", response_model=RouteOptimizationResult)
async def optimize_route(request: RouteOptimizationRequest,
                         service: MetricsService = Depends(MetricsService.get_instance)):
    res = await service.optimize_route(request)
    print(res)
    return res.model_dump()


@pickup_points_router.post("/get-distance", response_model=DistanceTimeResponse)
async def calculate_distance(request: CalculateDistanceRequest,
                             service: MetricsService = Depends(MetricsService.get_instance)):
    res = await service.calculate_distance(request)
    print(res)
    return res.model_dump()
