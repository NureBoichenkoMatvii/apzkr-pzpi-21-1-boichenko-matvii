import uuid
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic_partial import create_partial_model

from common.common_schemas import OrderByParams
from common.common_schemas import PaginationParams
from common.common_schemas import UuidDto


class CreateMachinePickupPointDto(BaseModel):
    machine_id: uuid.UUID
    pickup_point_id: uuid.UUID
    arrival_at: datetime
    departure_at: datetime
    deliver_orders: bool


UpdateMachinePickupPointDto = create_partial_model(CreateMachinePickupPointDto)


class MachinePickupPointResponseDto(CreateMachinePickupPointDto, UuidDto):
    model_config = ConfigDict(strict=True)


class MachinePickupPointSearchDto(BaseModel):
    column_filters: dict

    pagination: PaginationParams = PaginationParams()
    order_by: OrderByParams | None
