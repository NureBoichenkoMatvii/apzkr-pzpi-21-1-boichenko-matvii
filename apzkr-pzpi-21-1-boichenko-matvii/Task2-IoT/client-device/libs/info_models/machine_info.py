from decimal import Decimal
from enum import IntEnum
from typing import Dict

from pydantic import BaseModel
from pydantic import Field
from pydantic import confloat


class MachineStatus(IntEnum):
    unregistered = 0
    registered = 1


class InventoryItemInfo(BaseModel):
    medicine_type: int
    medicine_name: str
    left_amount: int


class MachineLocation(BaseModel):
    latitude: confloat(gt=-90, lt=90) | None = (
        Field(..., description="Latitude in degrees (-90 to 90)."))
    longitude: confloat(gt=-180, lt=180) | None = (
        Field(..., description="Longitude in degrees (-180 to 180)."))

    @classmethod
    def json_encoders(cls) -> Dict[any, any]:
        return {Decimal: lambda v: float(v)}


class MachineInfo(BaseModel):
    mac: str
    firmware_version: str
    hardware_version: str
    status: MachineStatus
    location: MachineLocation
    temperature: int  # temperature in celsius
    humidity: int  # humidity percents
    inventory: dict[str, InventoryItemInfo]
