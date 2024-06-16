import uuid
from datetime import datetime

from pydantic import BaseModel
from pydantic_partial import create_partial_model

from common.common_schemas import OrderByParams
from common.common_schemas import PaginationParams
from database.models import MachineStatus, MachineLocation


class CreateMachineDto(BaseModel):
    name: str
    mac: str
    location: MachineLocation
    admin_user_id: uuid.UUID
    status: MachineStatus = MachineStatus.unregistered
    last_maintenance_date: datetime | None = None


PatchMachineDto = create_partial_model(CreateMachineDto)


class PutMachineDto(CreateMachineDto):
    pass


class MachineIdDto(BaseModel):
    id: uuid.UUID


class MachineResponseDto(CreateMachineDto, MachineIdDto):
    pass


class SearchMachinesRequest(BaseModel):
    # simple filters on columns of Machine
    simple_filters: PatchMachineDto | None = None
    # dict where key is id of medicine and value its count
    medicines: dict[uuid.UUID, int] | None = None
    # to get machines with future stop at given pickup point
    pickup_point_stop: uuid.UUID | None = None

    pagination: PaginationParams = PaginationParams()
    order_by: OrderByParams | None
