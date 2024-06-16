from typing import List

from fastapi import APIRouter
from fastapi import Depends

from dependencies.user import current_active_user
from services.analytics.analytics_service import AnalyticsService
from services.analytics.schemas import *

analytics_router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(current_active_user)])


@analytics_router.post("/income", response_model=List[IncomeResponse])
async def get_income(data: IncomeRequest, service: AnalyticsService = Depends(AnalyticsService.get_instance)):
    return await service.get_income(data)


@analytics_router.post("/popular-machines", response_model=List[PopularPickupPointsResponse])
async def get_popular_machines(data: PopularStatisticRequest,
                               service: AnalyticsService = Depends(AnalyticsService.get_instance)):
    return await service.get_popular_machines(data)


@analytics_router.post("/popular-medicines", response_model=List[PopularMedicinesResponse])
async def get_popular_medicines(data: PopularStatisticRequest,
                                service: AnalyticsService = Depends(AnalyticsService.get_instance)):
    return await service.get_popular_medicines(data)


@analytics_router.post("/popular-pickup-points", response_model=List[PopularPickupPointsResponse])
async def get_popular_pickup_point(data: PopularStatisticRequest,
                                   service: AnalyticsService = Depends(AnalyticsService.get_instance)):
    return await service.get_popular_pickup_point(data)
