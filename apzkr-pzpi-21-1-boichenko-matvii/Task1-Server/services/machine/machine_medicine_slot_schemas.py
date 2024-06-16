import uuid
from pydantic import BaseModel, ConfigDict
from pydantic_partial import create_partial_model

from common.common_schemas import UuidDto


class CreateMachineMedicineSlotDto(BaseModel):
    machine_id: uuid.UUID
    medicine_id: uuid.UUID
    total_count: int
    reserved_count: int


UpdateMachineMedicineSlotDto = create_partial_model(CreateMachineMedicineSlotDto)


class MachineMedicineSlotResponseDto(CreateMachineMedicineSlotDto, UuidDto):
    model_config = ConfigDict(strict=True)
