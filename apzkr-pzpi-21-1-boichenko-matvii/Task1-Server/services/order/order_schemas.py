import uuid
from datetime import datetime

from pydantic import BaseModel
from pydantic_partial import create_partial_model

from common.common_schemas import UuidDto
from database.models import OrderStatus, Currencies
from services.machine.machine_pickup_point_schemas import MachinePickupPointResponseDto
from services.machine.machine_schemas import MachineResponseDto
from services.order.order_medicine_schemas import OrderMedicineResponseDto
from services.pickup_point.pickup_point_schemas import PickupPointResponseDto


class MedicineInfoDto(BaseModel):
    id: uuid.UUID
    count: int


class CreateOrderDto(BaseModel):
    user_id: uuid.UUID
    machine_id: uuid.UUID | None
    pickup_point_id: uuid.UUID
    status: OrderStatus
    payment_currency: Currencies

    medicines: list[MedicineInfoDto] = []


class PutOrderDto(CreateOrderDto):
    user_id: uuid.UUID
    machine_id: uuid.UUID | None
    pickup_point_id: uuid.UUID
    status: OrderStatus
    payment_currency: Currencies


PatchOrderDto = create_partial_model(PutOrderDto)


class OrderResponseDto(PutOrderDto, UuidDto):
    payment_amount: float
    created_at: datetime
    updated_at: datetime


class GetOrderByIdResponseDto(OrderResponseDto):
    order_medicines: list[OrderMedicineResponseDto]
    pickup_point: PickupPointResponseDto
    machine: MachineResponseDto | None = None
    machine_pickup_point: MachinePickupPointResponseDto | None = None
