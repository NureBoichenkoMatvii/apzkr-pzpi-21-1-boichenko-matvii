import uuid

from pydantic import BaseModel


class OrderMedicineInfo(BaseModel):
    medicine_type: int
    medicine_name: str
    count: int


class OrderInfo(BaseModel):
    order_id: str  # uuid.UUID
    order_medicines: list[OrderMedicineInfo]
