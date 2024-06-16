import uuid

from pydantic import BaseModel
from pydantic_partial import create_partial_model

from common.common_schemas import UuidDto
from services.medicine.schemas import MedicineResponseDto


class CreateOrderMedicineDto(BaseModel):
    order_id: uuid.UUID
    medicine_id: uuid.UUID
    medicine_count: int


PatchOrderMedicineDto = create_partial_model(CreateOrderMedicineDto)


class PutOrderMedicineDto(CreateOrderMedicineDto):
    pass


class OrderMedicineResponseDto(CreateOrderMedicineDto, UuidDto):
    medicine: MedicineResponseDto | None = None
