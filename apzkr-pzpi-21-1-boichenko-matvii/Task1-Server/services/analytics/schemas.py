import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from common.common_schemas import PaginationParams


class IncomeRequestPeriods(StrEnum):
    day = "day"
    month = "month"
    year = "year"


class OrderByEnum(StrEnum):
    count = "count",
    sum_income = "sum_income"


class IncomeRequest(BaseModel):
    period: IncomeRequestPeriods
    pagination: PaginationParams = PaginationParams()


class IncomeResponse(BaseModel):
    date: datetime
    income: float


class PopularStatisticRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    order_by: OrderByEnum


class MachineData(BaseModel):
    id: uuid.UUID
    name: str
    # Include other relevant machine details


class PopularMachinesResponse(BaseModel):
    machine: MachineData
    sort_value: int | float  # or float, depending on whether you're counting orders or summing payment amounts


class MedicineData(BaseModel):
    id: uuid.UUID
    name: str
    # Include other relevant medicine details


class PopularMedicinesResponse(BaseModel):
    medicine: MedicineData
    sort_value: int | float  # or float, depending on the metric used


class PickupPointData(BaseModel):
    id: uuid.UUID
    name: str
    # Include other relevant machine details


class PopularPickupPointsResponse(BaseModel):
    pickup_point: PickupPointData
    sort_value: int | float  # or float, depending on whether you're counting orders or summing payment amounts

