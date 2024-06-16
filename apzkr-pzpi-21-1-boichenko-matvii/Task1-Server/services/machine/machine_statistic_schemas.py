import uuid

from pydantic import BaseModel

from common.common_schemas import PaginationParams, OrderByParams


class CreateMachineStatisticDto(BaseModel):
    machine_id: uuid.UUID
    info: dict


class MachineStatisticResponseDto(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    info: dict


class MachineStatisticSearchDto(BaseModel):
    column_filters: dict

    pagination: PaginationParams = PaginationParams()
    order_by: OrderByParams | None
