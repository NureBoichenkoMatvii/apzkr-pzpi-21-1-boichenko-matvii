import uuid
from enum import StrEnum
from typing import TypeVar, Generic

from pydantic import BaseModel

from database.models import MachineLocation
from database.models import MedicineType

T = TypeVar('T')


class BaseMessage(BaseModel, Generic[T]):
    topic: str
    qos: int = 0
    timestamp: float
    msg_timestamp: float  # local timestamp of MQTT from the start/connection of client
    payload: T | None = None


class OrderEventStatus(StrEnum):
    start = "start"
    fail = "fail",
    success = "success"


class OrderEvent(BaseModel):
    status: OrderEventStatus
    reason: str | None = None


class InventoryItemInfo(BaseModel):
    medicine_type: int
    medicine_name: str
    left_amount: int


class MachineStatusInfo(BaseModel):
    mac: str
    temperature: int
    humidity: int
    firmware_version: str
    hardware_version: str
    location: MachineLocation
    inventory: dict[str, InventoryItemInfo]  # dict of machine medicine slots


class MachineConnection(BaseModel):
    online: bool


class RegistrationRequest(BaseModel):
    mac: str


class NewOrderRequestMedicine(BaseModel):
    medicine_type: MedicineType
    medicine_name: str
    count: int


class NewOrderRequest(BaseModel):
    order_id: str  # uuid.UUID
    order_medicines: list[NewOrderRequestMedicine]
